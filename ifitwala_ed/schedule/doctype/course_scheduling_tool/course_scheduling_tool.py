# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import  calendar
from frappe import _
import datetime
from frappe.utils import getdate, get_link_to_form, get_weekday, add_days, get_time, get_datetime_str
from frappe.model.document import Document
from ifitwala_ed.utils import OverlapError

class CourseSchedulingTool(Document):

	@frappe.whitelist()
	def schedule_course(self):
		course_schedules = []
		course_schedules_errors = []
		rescheduled = []
		reschedule_errors = []

		self.validate_dates()
		#self.validate_mandatory_fields()

		date = getdate(self.from_date)
		while date < getdate(self.to_date):
			if self.day == get_weekday(date):
				course_schedule = self.make_course_schedule(date)
				course_schedule.insert()
				course_schedules.append(course_schedule)
				date = add_days(date, self.n_week * 7)
			else:
				date = add_days(date, 1)

		return dict(
			course_schedules=course_schedules,
			course_schedules_errors=course_schedules_errors,
			rescheduled=rescheduled,
			reschedule_errors=reschedule_errors
		)

		if self.reschedule:
			rescheduled, reschedule_errors = self.delete_course_schedule(rescheduled, reschedule_errors)


	def validate_dates(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw(_("The start date of the course {0} cannot be after its end date {1}. Please adjust the dates.").format(getdate(self.from_date), getdate(self.to_date)))

		at = frappe.get_doc("Academic Term", self.academic_term)
		if at.academic_year != self.academic_year:
			frappe.throw(_("The academic term {0} does not belong to the academic  year {1}").format(self.academic_term, self.academic_year))
		if not (getdate(at.term_start_date) <= getdate(self.from_date) <= getdate(at.term_end_date)):
			frappe.throw(_("The start and end date of the course should be included in the selected academic term {1}.").format(get_link_to_form(self.academic_term)))

	def validate_mandatory_fields(self):
		fields = ['course', 'room', 'from_time', 'to_time', 'from_date', 'to_date']
		for f in fields:
			if not self.get(f):
				frappe.throw(_("{0} is a mandatory field. Please select an appropriate value.").format(self.meta.get_label(f)))

	@frappe.whitelist()
	def get_instructors(self):
		return frappe.db.sql("""SELECT instructor, instructor_name FROM `tabStudent Group Instructor` WHERE parent = %s""", (self.student_group), as_dict=1)

	@frappe.whitelist()
	def get_students(self):
		return frappe.db.sql("""SELECT student, student_name FROM `tabStudent Group Student` WHERE parent = %s""", (self.student_group), as_dict=1)


	def make_course_schedule(self, date):
		course_schedule = frappe.get_doc({
			#"doctype": "Course Event",
			"doctype": "Course Schedule",
			#"subject": f'{self.student_group.split("/")[0]} {getdate(date)}',
			#"event_category": "Course",
			#"event_type": "Private",
			"schedule_date": getdate(date),
			"location": self.location,
			"color": self.calendar_event_color,
			#"starts_on": datetime.datetime.combine(getdate(date), get_time(self.from_time)),
			#"ends_on": datetime.datetime.combine(getdate(date), get_time(self.to_time)),
			"from_time": self.from_time,
			"to_time": self.to_time
			#"reference_type": "Student Group",
			#"reference_name": self.student_group,
		})
		#part = []
		for instructor in self.instructors:
			inst = frappe.get_doc("Instructor", instructor.instructor)
			course_schedule.append("participants", {"participant":inst.user_id})

		for student in self.students:
			stud = frappe.get_doc("Student", student.student)
			course_schedule.append("participants", {"participant": stud.user_id})

		return course_schedule


	def delete_course_schedule(self, rescheduled, reschedule_errors):
		schedules = frappe.get_list("School Event", fields = ["name", "starts_on"],
			filters = [
				["reference_name", "=", self.student_group],
				["starts_on", ">=", datetime.datetime.combine(getdate(date), get_time(self.from_time))],
				["ends_on", "<=", datetime.datetime.combine(getdate(date), get_time(self.to_time))]
			])
		for schedule in schedules:
			try:
				if self.day == get_weekday(getdate(schedule.schedule_date)):
					frappe.delete_doc("School Event", schedule.name)
					rescheduled.append(schedule.name)
			except:
				reschedule_errors.append(schedule.name)

		return rescheduled, reschedule_errors
