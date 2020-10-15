# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, today
from frappe.model.document import Document

class HolidayList(Document):
	def validate(self):
		self.validate_days()
		self.total_holidays = len(self.holidays)

	def validate_days(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw(_("From Date cannot be after To Date. Please adjust the date."))

		for day in self.get(holiay):
			if not (getdate(self.from_date) <= getdate(day.holiday_date) <= getdate(self.to_date)):
				frappe.throw(_("The holiday on {0} should be between From Date and To Date.").format(day.holiday_date))
