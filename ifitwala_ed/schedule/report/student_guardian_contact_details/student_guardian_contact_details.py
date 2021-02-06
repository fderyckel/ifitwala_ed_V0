# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):

	columns, data = [], []

	school_settings = frappe.get_doc("Education Settings")
	if school_settings.academic_year:
		academic_year = filters.set(school_settings.academic_year)
	else:
		academic_year = filters.get("academic_year")

	student_group = filters.get("student_group")

	group = frappe.get_list("Student Group", filter = {"name": student_group})


	columns = get_columns






	return columns, data

def get_columns():
	columns = [
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
