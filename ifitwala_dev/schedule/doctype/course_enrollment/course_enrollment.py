# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from functools import reduce

class CourseEnrollment(Document): 
	
	def validate_duplication(self):
		enrollment = frappe.get_all("Course Enrollment", filters={
			"student": self.student,
			"course": self.course,
			"program_enrollment": self.program_enrollment
		})
		if enrollment:
			frappe.throw(_("Student is already enrolled."))
