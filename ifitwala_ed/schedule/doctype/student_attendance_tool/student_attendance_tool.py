# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StudentAttendanceTool(Document):
	pass

@frappe.whitelist()
def get_students(based_on, date=None, student_group=None, course_schedule=None):
	attendance_not_marked = []
	attendance_marked = []
	filters = {}
	if based_on == "Course Schedule":
		student_group = frappe.db.get_value("Course Schedule", course_schedule, "student_group")
		if student_group:
			student_list = frappe.get_list("Student Group Student", fields = ["student", "student_name", "group_roll_number"], filters = {"parent": student_group, "active": 1}, order_by = "group_roll_number")
	marked_student = {}
	for stud in frappe.get_list("Student Attendance", fields=["student", "status"], filters = {"date":date}):
		marked_student[stud['student']] = stud['status']

	for student in student_list:
		student['status'] = marked_student.get(student['student'])
		if student['student'] not in marked_student:
			attendance_not_marked.append(student)
		else:
			attendance_marked.append(student)
	return {
		"marked": attendance_marked,
		"unmarked": attendance_not_marked
	}



@frappe.whitelist()
def get_student_attendance_records(based_on, date=None, student_group=None, course_schedule=None):
	student_list = []
	student_attendance_list = []

	if based_on == "Course Schedule":
		student_group = frappe.db.get_value("Course Schedule", course_schedule, "student_group")
		if student_group:
			student_list = frappe.get_list("Student Group Student", fields = ["student", "student_name", "group_roll_number"], filters = {"parent": student_group, "active": 1}, order_by = "group_roll_number")

		if course_schedule:
			student_attendance_list = frappe.db.sql("""
			 	SELECT student, status
				FROM `tabStudent Attendance`
				WHERE course_schedule = %s""", (course_schedule), as_dict = 1)
		else:
			student_attendance_list = frappe.db.sql("""
			 	SELECT student, status
				FROM `tabStudent Attendance`
				WHERE student_group=%s AND date=%s AND (course_schedule IS NULL OR course_schedule='')""", (student_group, date), as_dict=1)

		for attendance in student_attendance_list:
			for student in student_list:
				if student.student == attendance.student:
					student.status = attendance.status

	return student_list
