# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Instructor(Document):

	def validate(self):
		self.validate_duplicate_employee()

	def validate_duplicate_employee(self):
		if self.employee and frappe.db.get_value("Instructor", {'employee': self.employee, 'name': ['!=', self.name]}, 'name'):
			frappe.throw(_("Employee ID is linked with another instructor."))
