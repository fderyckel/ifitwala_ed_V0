# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import  calendar
from frappe import _
from frappe.utils import getdate, get_link_to_form, get_weekday, add_days
from frappe.model.document import Document
from ifitwala_ed.utils import OverlapError

class CourseSchedulingTool(Document):

	def schedule_course(self):
		course_schedules = []
		course_schedules_errors = []
		rescheduled = []
		reschedule_errors = []

		self.validate_dates()

		date = getdate(self.course_start_date)
		while date < getdate(self.course_end_date):
			if self.day == get_weekday(date):
				course_schedule = self.make_course_schedule(date)
				try:
					print('pass')
				except OverlapError:
					print('fail')
					course_schedules_errors.append(date)
				else:
					course_schedules.append(course_schedule)
				date = add_days(date, 7)
			else:
				date = add_days(date, 1)

		return dict(
			course_schedules=course_schedules,
			course_schedules_errors=course_schedules_errors,
			rescheduled=rescheduled,
			reschedule_errors=reschedule_errors
		)


	def validate_dates(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw(_("The start date of the course {0} cannot be after its end date {1}. Please adjust the dates.").format(getdate(self.from_date), getdate(self.to_date)))

		at = frappe.get_doc("Academic Term", self.academic_term)
		if not (getdate(at.term_start_date) <= getdate(self.from_date) <= getdate(at.term_end_date)):
			frappe.throw(_("The start and end date of the course should be included in the selected academic term {1}.").format(get_link_to_form(self.academic_term)))

	def get_instructors(self):
		return frappe.db.sql("""select instructor, instructor_name from `tabStudent Group Instructor` where parent = %s""", (self.student_group), as_dict=1)

	def make_course_schedule(date):
		course_schedule =  frappe.new_doc("Course Schedule")
		course_schedule.student_group = self.student_group
		course_schedule.course = self.course
		course_schedule.schedule_date = date
		course_schedule.room = self.room
		course_schedule.from_time = self.from_time
		course_schedule.to_time = self.to_time
		course_schedule.color = self.color
