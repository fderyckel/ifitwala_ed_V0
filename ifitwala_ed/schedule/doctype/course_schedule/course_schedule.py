# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document

class CourseSchedule(Document):

	def validate(self):
		self.validate_course()
		self.set_title()
		self.validate_date()

	# set up the course field if it is based on a course.
	def validate_course(self):
		group_based_on, course = frappe.db.get_value("Student Group", self.student_group, ["group_based_on", "course"])
		if group_based_on == "course":
			self.course = course

	def set_title(self):
		self.title = self.course + " by " + (self.instructor_name if self.instructor_name else self.instructor)


	def validate_date(self):
		if self.from_time > self.to_time:
			frappe.throw(_("Start time is after End Time. Adjust your start and end time."))
		academic_term = frappe.db.get_value("Student Group", self.student_group, "academic_term")
		if not (getdate(academic_term.term_start_date) <= getdate(self.schedule_date) <= getdate(academic_term.term_end_date)):
			frappe.throw(_("The schedule date {0} does not belong to the academic term {1} selected for that student group.").format(formatdate(schedule_date), academic_term))
