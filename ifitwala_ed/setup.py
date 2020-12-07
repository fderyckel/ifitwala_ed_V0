# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ifitwala_ed.school_settings.utils import insert_record


def setup_education():
	disable_desk_access_for_student_role()
	disable_desk_access_for_guardian_role()

	if frappe.db.exists("Academic Year", "2019-20"):
		return
	create_academic_sessions()

	if frappe.db.exists("Designation", "Director"):
		return
	create_designations()

	if frappe.db.exists("Student Log Type", "Medical"):
		return
	create_log_type()

	if frappe.db.exists("Student Attendance Code", "Present"):
		return
	create_attendance_code()

def disable_desk_access_for_student_role():
	try:
		student_role = frappe.get_doc("Role", "Student")
	except frappe.DoesNotExistError:
		create_student_role()
		return

	student_role.desk_access = 0
	student_role.save()

def disable_desk_access_for_guardian_role():
	try:
		guardian_role = frappe.get_doc("Role", "Guardian")
	except frappe.DoesNotExistError:
		create_guardian_role()
		return
		
	guardian_role.desk_access = 0
	guardian_role.save()

def create_student_role():
	student_role = frappe.get_doc({
		"doctype": "Role",
		"role_name": "Student",
		"desk_access": 0
	})
	student_role.insert()

def create_guardian_role():
	guardian_role = frappe.get_doc({
		"doctype": "Role",
		"role_name": "Guardian",
		"desk_access": 0
	})
	guardian_role.insert()

def create_academic_sessions():
	data = [
		{"doctype": "Academic Year", "academic_year_name": "2020-21"},
		{"doctype": "Academic Year", "academic_year_name": "2019-20"},
		{"doctype": "Academic Year", "academic_year_name": "2018-19"},
		{"doctype": "Academic Term", "academic_year": "2020-21", "term_name": "Semester 1"},
		{"doctype": "Academic Term", "academic_year": "2020-21", "term_name": "Semester 2"},
		{"doctype": "Academic Term", "academic_year": "2020-21", "term_name": "S1 - S2"},
		{"doctype": "Academic Term", "academic_year": "2019-20", "term_name": "Semester 1"},
		{"doctype": "Academic Term", "academic_year": "2019-20", "term_name": "Semester 2"},
		{"doctype": "Academic Term", "academic_year": "2019-20", "term_name": "S1 - S2"}
	]
	insert_record(data)

def create_designations():
	data = [
		{"doctype": "Designation", "designation_name": "Director"},
		{"doctype": "Designation", "designation_name": "Principle"},
		{"doctype": "Designation", "designation_name": "Assistant Principal"},
		{"doctype": "Designation", "designation_name": "Nurse"},
		{"doctype": "Designation", "designation_name": "Teacher"},
		{"doctype": "Designation", "designation_name": "Teacher Assistant"}
	]
	insert_record(data)

def create_log_type():
	data = [
			{"doctype": "Student Log Type", "log_type": "Behaviour"},
			{"doctype": "Student Log Type", "log_type": "Academic"},
			{"doctype": "Student Log Type", "log_type": "Medical"},
	]
	insert_record(data)

def create_attendance_code():
	data = [
			{"doctype": "Student Attendance Code", "attendance_code": "Present"},
			{"doctype": "Student Attendance Code", "attendance_code": "Absent"},
			{"doctype": "Student Attendance Code", "attendance_code": "Tardy"},
			{"doctype": "Student Attendance Code", "attendance_code": "Excused Absence"},
			{"doctype": "Student Attendance Code", "attendance_code": "Field Trip"},
			{"doctype": "Student Attendance Code", "attendance_code": "Excused Tardy"},
	]
	insert_record(data)
