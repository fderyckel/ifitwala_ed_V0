# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import get_link_to_form, today, getdate, formatdate, date_diff, cint
from frappe.model.document import Document

class SchoolCalendar(Document):

	def validate(self):
		if not self.terms:
			self.extend("terms", self.get_terms())
		ay = frappe.get_doc("Academic Year", self.academic_year)
		self.validate_dates()
		self.total_holiday_days = len(self.holidays)
		self.total_number_day = date_diff(ay.year_end_date, ay.year_start_date)
		self.total_instruction_days = date_diff(ay.year_end_date, ay.year_start_date) - self.total_holiday_days

	def get_terms(self):
			self.terms = []
			terms = frappe.get_list("Academic Term", filters = {"academic_year":self.academic_year}, fields=["name as term", "term_start_date as start", "term_end_date as end"])
			for term in terms:
				self.append("terms", {
					"term": term.term, "start": term.start, "end": term.end,
					"length": date_diff(getdate(term.end), getdate(term.start))
				})

	def validate_dates(self):
		ay = frappe.get_doc("Academic Year", self.academic_year)
		for day in self.get("holidays"):
			if not (getdate(ay.year_start_date) <= getdate(day.holiday_date) <= getdate(ay.year_end_date)):
				frappe.throw(_("The holiday on {0} should be within your academic year {1} dates.").format(formatdate(day.holiday_date), get_link_to_form("Academic Year", self.academic_year)))

	def get_long_break_dates(self):
		ay = frappe.get_doc("Academic Year", self.academic_year)
		self.validate_break_dates()
		date_list = self.get_long_break_dates_list(self.start_of_break, self.end_of_break)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append("holidays", {})
			ch.description = self.break_description if self.break_description else "Break"
			ch.color = self.breaks_color if self.breaks_color else ""
			ch.holiday_date = d
			ch.idx = last_idx + i + 1

	def get_weekly_off_dates(self):
		ay = frappe.get_doc("Academic Year", self.academic_year)
		self.validate_values()
		date_list = self.get_weekly_off_dates_list(ay.year_start_date, ay.year_end_date)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append("holidays", {})
			ch.description = self.weekly_off
			ch.holiday_date = d
			ch.color = self.weekend_color if self.weekend_color else ""
			ch.weekly_off = 1
			ch.idx = last_idx + i + 1

	# logic for the button "clear_table"
	def clear_table(self):
		self.set("holidays", [])

	def validate_break_dates(self):
		ay = frappe.get_doc("Academic Year", self.academic_year)
		if not self.start_of_break and not self.end_of_break:
			frappe.throw(_("Please select first the start and end of your break."))
		if getdate(self.start_of_break) > getdate(self.end_of_break):
			frappe.throw(_("The start of the break cannot be after its end. Adjust the dates."))
		if not (getdate(ay.year_start_date) <= getdate(self.start_of_break) <= getdate(ay.year_end_date)) or not (getdate(ay.year_start_date) <= getdate(self.end_of_break) <= getdate(ay.year_end_date)):
			frappe.throw(_("The holiday called {0} should be within your academic year {1} dates.").format(self.break_description, get_link_to_form("Academic Year", self.academic_year)))

	def get_long_break_dates_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		from datetime import timedelta
		import calendar

		date_list = []
		existing_date_list = []
		reference_date = start_date
		existing_date_list = [getdate(holiday.holiday_date) for holiday in self.get("holidays")]

		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days = 1)

		return date_list

	def validate_values(self):
		if not self.weekly_off:
			frappe.throw(_("Please select first the weekly off days."))

	def get_weekly_off_dates_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		from dateutil import relativedelta
		from datetime import timedelta
		import calendar

		date_list = []
		existing_date_list = []

		weekday = getattr(calendar, (self.weekly_off).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday = weekday)
		existing_date_list = [getdate(holiday.holiday_date) for holiday in self.get("holidays")]

		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days = 7)

		return date_list


@frappe.whitelist()
def get_events(start, end, filters=None):
	if filters:
		filters = json.load(filters)
	else:
		filters = []

	if start:
		filters.append(['Holiday', 'holiday_date', '>', getdate(start)])
	if end:
		filters.append(['Holiday', 'holiday_date', '<', getdate(end)])

	return frappe.get_list('School Calendar',
		fields=['name', 'academic_year', 'school', '`tabHoliday`.holiday_date', '`tabHoliday`.description', '`tabHoliday`.color'],
		filters = filters,
		update={"allDay": 1})
