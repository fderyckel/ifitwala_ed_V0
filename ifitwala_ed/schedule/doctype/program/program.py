# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Program(Document):
	def validate(self):
		self.validate_duplicate_course()

	def validate_duplicate_course(self):
		found = []
		for course in self.courses:
			if course.course in found:
				frappe.throw(_("Course {0} is entered twice. Please remove one of them.").format(course.course))
			else:
				found.append(course.course)
