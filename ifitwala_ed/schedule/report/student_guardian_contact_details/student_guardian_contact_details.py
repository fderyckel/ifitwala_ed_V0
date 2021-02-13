# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):

	columns, data = [], []
	columns = get_columns(filters)

	student_group = filters.get("student_group")
	students = frappe.get_list("Student Group Student", fields = ["student", "student_name", "group_roll_number"], filters = {"parent": student_group})
	student_list = [student.student for student in students]
	if not student_list:
		return columns, []

	student_details = get_student_details(student_list)
	guardian_details = get_guardian_details(student_list)

	for s in students:
		yo = student_details.get(s.student)
		row = [s.group_roll_number, s.student, s.student_name, yo.get("student_mobile_number"), yo.get("address"),
				yo.get("state"), yo.get("pincode"), yo.get("country")]

		data.append(row)

	return columns, data

def get_columns(fitlers=None):
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
				"width": 120
			},
			{
				"label": _("Student Name"),
				"fieldname": "student_full_name",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("Mobile"),
				"fieldname": "student_mobile_number",
				"fieldtype": "Data",
				"width": 120
			},
			{
				"label": _("Student Address"),
				"fieldname": "address",
				"fieldtype": "Data",
				"width": 250
			},
			{
				"label": _("State"),
				"fieldname": "state",
				"fieldtype": "Data",
				"width": 50
			},
			{
				"label": _("ZIP code"),
				"fieldname": "pincode",
				"fieldtype": "Data",
				"width": 50
			},
			{
				"label": _("Country"),
				"fieldname": "country",
				"fieldtype": "Data",
				"width": 120
			}
	]

	return columns

def get_student_details(student_list):
	student_map = frappe._dict()
	student_details = frappe.db.sql("""
			SELECT
				`tabStudent`.name,
				`tabStudent`.student_full_name,
				`tabStudent`.student_email,
				`tabStudent`.student_mobile_number,
				concat_ws(', ',
					trim(',' from `tabAddress`.address_line1),
					trim(',' from `tabAddress`.address_line2)
					) AS address,
				`tabAddress`.state,
				`tabAddress`.pincode,
				`tabAddress`.country
			FROM
				`tabStudent` left join `tabDynamic Link` on (
				`tabStudent`.name = `tabDynamic Link`.link_name and
				`tabDynamic Link`.parenttype = 'Address')
				left join `tabAddress` on (`tabAddress`.name=`tabDynamic Link`.parent) """, as_dict=1)
	for s in student_details:
		student = frappe._dict()
		student["student_full_name"] = s.student_full_name
		student["student_mobile_number"] = s.student_mobile_number
		student["address"] = s.address
		student["state"] = s.state
		student["pincode"]= s.pincode
		student["country"] = s.country
		student_map[s.name] = student

	return student_map

def get_guardian_details(student_list):
	guardian_map = frappe._dict()
	guardian_details = frappe.db.sql("""SELECT parent, guardian, guardian_name, relation FROM `tabStudent Guardian` WHERE parent in (%s)""" %
		', '.join(['%s']*len(student_list)), tuple(student_list), as_dict=1)
	guardian_list = list(set([g.guardian for g in guardian_details])) or ['']
