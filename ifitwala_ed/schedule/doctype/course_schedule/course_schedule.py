# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class CourseSchedule(Document):

	def validate(self):
		self.set_title()
		self.validate_course()
		self.validate_date()

	def set_title(self):
		self.title = self.course + "by" + (self.instructor_name if self.instructor_name else self.instructor)

	# set up the course field if it is based on a course.
	def validate_course(self):
		group_based_on, course = frappe.db.get_value("Student Group", self.student_group, ["group_based_on", "course"])
		if group_based_on == "course":
			self.course = course

	def validate_date(self):
		if self.from_time > self.to_time:
			frappe.throw(_("Start time is after End Time. Adjust your start and end time."))
