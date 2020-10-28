# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_link_to_form
from frappe.model.document import Document
from ifitwala_ed.ifitwala_ed.api import get_student_group_students

class StudentAttendance(Document):

	def validate(self):
		self.set_date()
		self.validate_date()
		self.validate_student()

	def set_date(self):
		if self.course_schedule:
			self.date = frappe.db.get_value("Course Schedule", self.course_schedule, "schedule_date")

	def validate_date(self):
		if not self.leave_application and getdate(self.date) > getdate(today()):
			frappe.throw(_("Attendance cannot be marked for future date."))
		if self.student_group:
			academic_term = frappe.db.get_value("Student Group", self.student_group, "academic_term")
			if academic_term:
				term_start_date, term_end_date = frappe.db.get_value("Academic Term", academic_term, ["term_start_date", "term_end_date"])
				if term_start_date and term_end_date:
					if getdate(term_start_date) <= getdate(self.date) <= getdate(term_end_date):
						frappe.throw(_("Attendance date should be within the academic term {0} dates.").format(get_form_to_link(academic_term)))


	def validate_student(self):
		student_group_students = [d.student for d in get_student_group_students(self.student_group)]
		if student_group and self.student not in student_group_students:
			frappe.throw(_("Student {0}: {1} does not belong to student group {2}").format(get_link_to_form(self.student), self.student_name, get_link_to_form(self.student_group)))
