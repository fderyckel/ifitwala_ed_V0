# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):

	columns, data = [], []

	student_group = filters.get("student_group")
	students = frappe.get_list("Student Group Student", fields = ["student", "student_name", "group_roll_number"], filters = {"name": student_group})
	student_list = [student.student for student in students]
	if not student_list:
		return columns, []

	student_details = get_student_details(student_list)

	for s in students:
		student_details = student_map.get(s.student)
		row = [s.group_roll_number, s.student, s.student_name, student_details.get("student_mobile_number")]

		data.append(row)

	return columns, data

def get_columns():
	columns = [
			{
				"label": _("Student Roll No"),
				"fieldname": "group_roll_number",
				"fieldtype": "Int",
				"width": 50
			},
			{
				"label": _("Student ID"),
				"fieldname": "student",
				"fieldtype": "Link",
				"options": "Student",
				"width": 80
			},
			{
				"label": _("Student Name"),
				"fieldname": "student_full_name",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("Student Mobile"),
				"fieldname": "student_mobile_number",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Guardian 1 Name"),
				"fieldname": "student_full_name",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("Relation with Guardian 1"),
				"fieldname": "student_full_name",
				"fieldtype": "Data",
				"width": 90
			}
	]
	return columns

def get_student_details(student_list):
	student_map = frappe._dict()
	student_details = frappe.db.sql(""" SELECT name, student_full_name, student_mobile_number
										FROM `tabStudent`
										WHERE name in (%s)""" % ', '.join(['%s']*len(student_list)), tuple(student_list), as_dict=1)
	for s in student_details:
		student = frappe._dict()
		student["student_full_name"] = s.student_full_name
		student["student_mobile_number"] = s.student_mobile_number
		student_map[s.name] = student

	return student_map
