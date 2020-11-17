# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StudentLeaveApplication(Document):

	def validate(self):
		self.validate_holiday_list()

	def  validate_holiday_list(self):
		holidays = get_holiday_list()
