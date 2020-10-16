# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, today, formatdate
from frappe.model.document import Document

class HolidayList(Document):
	def validate(self):
		self.validate_days()
		self.total_holidays = len(self.holidays)

	#logic for the button (with button id name)
	def get_weekly_off_dates(self):
		self.validate_values()
		date_list = self.get_weekly_off_dates_list(self.from_date, self.to_date)

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

		return  date_list

	def clear_table(self):
		self.set("holidays", [])
