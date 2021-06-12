# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Program(Document):
	def validate(self):
		self.validate_duplicate_course()

	def validate_duplicate_course(self):
		found = []
		for course in self.courses:
			doc = frappe.get_doc("Course", course.course)
			if doc.status != "Active":
				frappe.throw(_("Course {0} has been discontinued. It cannot be part of this program or set up the course as active.").format(course.course))

			if course.course in found:
				frappe.throw(_("Course {0} is entered twice. Please remove one of them.").format(course.course))
			else:
				found.append(course.course)
