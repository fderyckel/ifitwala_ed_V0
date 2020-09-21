# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe 
from ifitwala_dev.utils import insert_record


def setup_education():
	disable_desk_access_for_student_role(
		
	if frappe.db.exists("Academic Year", "2019-20"): 
		return
	create_academic_sessions()
		
	if frappe.db.exists("Designation", "Director"): 
		return
	create_designations()

def disable_desk_access_for_student_role():
	try:
		student_role = frappe.get_doc("Role", "Student")
	except frappe.DoesNotExistError:
		create_student_role()
		return

	student_role.desk_access = 0
	student_role.save()

def create_student_role():
	student_role = frappe.get_doc({
		"doctype": "Role",
		"role_name": "Student",
		"desk_access": 0
	})
	student_role.insert()
	
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
		{"doctype": "Designation", "designation_name": "Teacher"}
	]
	insert_record(data)
