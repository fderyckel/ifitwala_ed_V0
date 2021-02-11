# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import getdate, today, formatdate, cint, date_diff
from frappe.model.document import Document

class StaffCalendar(Document):
    	def __setup__(self):
        	self.onload()

	def onload(self):
		if not self.weekend_color:
			self.weekend_color = frappe.get_single("Education Settings").default_weekend_color
		if not self.break_color:
			self.breaks_color = frappe.get_single("Education Settings").default_breaks_color

	def validate(self):
		self.validate_days()
		self.total_holidays = len(self.holidays)
		self.total_working_day = date_diff(self.to_date, self.from_date) - self.total_holidays + 1

	#logic for the button (with button id name)
	def get_weekly_off_dates(self):
		self.validate_values()
		date_list = self.get_weekly_off_dates_list(self.from_date, self.to_date)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append("holidays", {})
			ch.description = self.weekly_off
			ch.color = self.weekend_color if self.weekend_color else ""
			ch.holiday_date = d
			ch.weekly_off = 1
			ch.idx = last_idx + i + 1

	def get_long_break_dates(self):
		self.validate_break_values()
		date_list = self.get_long_break_dates_list(self.start_of_break, self.end_of_break)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append("holidays", {})
			ch.description = self.break_description if self.break_description else "Break"
			ch.color = self.breaks_color if self.breaks_color else ""
			ch.holiday_date = d
			ch.idx = last_idx + i + 1

	# logic for the button "clear_table"
	def clear_table(self):
		self.set("holidays", [])

	def validate_days(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw(_("From Date cannot be after To Date. Please adjust the date."))

		for day in self.get("holidays"):
			if not (getdate(self.from_date) <= getdate(day.holiday_date) <= getdate(self.to_date)):
				frappe.throw(_("The holiday on {0} should be between From Date and To Date.").format(formatdate(day.holiday_date)))

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

	def validate_break_values(self):
		if not self.start_of_break and not self.end_of_break:
			frappe.throw(_("Please select first the start and end of your break."))
		if getdate(self.start_of_break) > getdate(self.end_of_break):
			frappe.throw(_("The start of the break cannot be after its end. Adjust the dates."))
		if not (getdate(self.from_date) <= getdate(self.start_of_break) <= getdate(self.to_date)) or not (getdate(self.from_date) <= getdate(self.end_of_break) <= getdate(self.to_date)):
			frappe.throw(_("The start and end of the break have to be within the start and end of the calendar."))

	def get_long_break_dates_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		from dateutil import relativedelta
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


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	if filters:
		filters = json.loads(filters)
	else:
		filters = []

	if start:
		filters.append(['Holiday', 'holiday_date', '>', getdate(start)])
	if end:
		filters.append(['Holiday', 'holiday_date', '<', getdate(end)])

	return frappe.get_list('Staff Calendar',
		fields = ['name', 'academic_year', 'school', '`tabHoliday`.holiday_date', '`tabHoliday`.description', '`tabHoliday`.color'],
		filters = filters,
		update = {"allDay": 1})
