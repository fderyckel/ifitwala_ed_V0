# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, formatdate
from frappe.model.document import Document

class CourseSchedule(Document):

	def validate(self):
		self.validate_course()
		self.set_title()
		self.validate_date()
		self.validate_overlap()
		if not self.instructors:
			self.extend("instructors", self.get_instructors())

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
		ac_term = frappe.db.get_value("Student Group", self.student_group, "academic_term")
		academic_term = frappe.get_doc("Academic Term", ac_term)
		if not (getdate(academic_term.term_start_date) <= getdate(self.schedule_date) <= getdate(academic_term.term_end_date)):
			frappe.throw(_("The schedule date {0} does not belong to the academic term {1} selected for that student group.").format(formatdate(self.schedule_date), academic_term.name))

	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""
		from ifitwala_ed.utils import validate_overlap_for

		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "Student Group")

		validate_overlap_for(self, "Course Schedule", "Room")
		validate_overlap_for(self, "Course Schedule", "Instructor")

	def get_instructors(self):
		return frappe.db.sql("""select instructor from `tabStudent Group Instructor` where parent = %s""", (self.student_group), as_dict=1) 



@frappe.whitelist()
def get_course_schedule_events(start, end, filters=None):

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Course Schedule", filters)

	data = frappe.db.sql(""" SELECT name, course, color,
					timestamp(schedule_date, from_time) as from_datetime,
					timestamp(schedule_date, to_time) as to_datetime,
					room, student_group, 0 as 'all_day'
			FROM `tabCourse Schedule`
			WHERE ( schedule_date between %(start)s and %(end)s )
			{conditions}""".format(conditions = conditions), {
					"start":start,
					"end": end}, as_dict=True, update={"all_day": 0})
	return data
