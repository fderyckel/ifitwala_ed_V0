# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from functools import reduce
from frappe.utils import get_link_to_form

class CourseEnrollment(Document):

	def validate(self):
		self.validate_duplication()

	def validate_duplication(self):
		enrollment = frappe.db.exists("Course Enrollment", {
			"student": self.student,
			"course": self.course,
			"program_enrollment": self.program_enrollment,
			"name": ("!=", self.name)
		})
		if enrollment:
			frappe.throw(_("Student is already enrolled in this course via Course Enrollment {0}.").format(
				get_link_to_form("Course Enrollment", enrollment)), title=_("Duplicate Entry"))
