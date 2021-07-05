# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, formatdate, get_link_to_form
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
		coursse = frappe.db.get_value("Student Group", self.student_group, ["course"])
		if self.course != coursse:
			frappe.throw(_("This course {0} is not the course {1} attached to this student group. Please adjust.").format(get_link_to_form("Course", coursse), get_link_to_form("Course", self.course)))

	def set_title(self):
		course_abbr = frappe.db.get_value("Student Group", self.student_group, ["student_group_abbreviation"])
		self.title = course_abbr

	def validate_date(self):
		if self.from_time > self.to_time:
			frappe.throw(_("Start time is after End Time. Adjust your start and/or your end time."), title=_("Change the times"))
		ac_term = frappe.db.get_value("Student Group", self.student_group, "academic_term")
		academic_term = frappe.get_doc("Academic Term", ac_term)
		if not (getdate(academic_term.term_start_date) <= getdate(self.schedule_date) <= getdate(academic_term.term_end_date)):
			frappe.throw(_("The schedule date {0} does not belong to the academic term {1} selected for that student group.").format(
					formatdate(self.schedule_date), get_link_to_form("Academic Term", academic_term.name)), title=_("Change Schedule Date"))

	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""
		from ifitwala_ed.utils import validate_overlap_for

		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "student_group")
		if self.location:
			validate_overlap_for(self, "Course Schedule", "location")
		if self.instructors:
			tructors = frappe.get_list("Student Group Instructor", fields = ["instructor"], filters = {"parent": self.student_group})
			for tructor in tructors:
				validate_overlap_for(self, "Course Schedule", tructor.instructor)

	#def get_instructors(self):
	#	return frappe.db.sql("""select instructor, instructor_name from `tabStudent Group Instructor` where parent = %s""", (self.student_group), as_dict=1)


@frappe.whitelist()
def get_course_schedule_events(start, end, filters=None):

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Course Schedule", filters)

	data = frappe.db.sql(""" SELECT name, course, calendar_event_color,
					timestamp(schedule_date, from_time) as from_datetime,
					timestamp(schedule_date, to_time) as to_datetime,
					location, student_group, 0 as 'all_day'
			FROM `tabCourse Schedule`
			WHERE ( schedule_date between %(start)s and %(end)s )
			{conditions}""".format(conditions = conditions), {
					"start":start,
					"end": end}, as_dict=True, update={"allDay": 0})
	return data
