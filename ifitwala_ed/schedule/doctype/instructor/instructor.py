# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Instructor(Document):
	def __setup__(self):
		self.onload()

	def onload(self):
		self.load_groups()

	def validate(self):
		self.instructor_log = []
		self.validate_duplicate_employee()

	def after_insert(self):
		from frappe.utils.user import add_role
		add_role(self.user_id, "Instructor")

	def validate_duplicate_employee(self):
		if self.employee and frappe.db.get_value("Instructor", {'employee': self.employee, 'name': ['!=', self.name]}, 'name'):
			frappe.throw(_("Employee ID is linked with another instructor."))

	def load_groups(self):
		self.instructor_log = []
		groups = frappe.get_all("Student Group Instructor", filters = {"instructor":self.name}, fields = ["parent", "designation"])
		for group in groups:
			yo = frappe.get_doc("Student Group", group.parent)
			self.append("instructor_log", {"academic_year":yo.academic_year, "academic_term":yo.academic_term,
						"designation":group.designation, "student_group":yo.name, "course":yo.course})
