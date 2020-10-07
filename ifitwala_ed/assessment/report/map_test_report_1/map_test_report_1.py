# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	start_date = filters.get("from_year")
	if start_date:
		start_date = start_date.year_start_date

	program = filters.get("program")


	columns, data, chart = [], [], []

	returned_value = get_formatted_results(args)



	columns = get_columns()



	return columns, data


def get_formatted_results(args):
	conditions = get_filter_conditions(filters)

	map_results = frappe.db.sql('''
			SELECT student, student_name, program, test_percentile, test_rit_score, test_date, discipline
			FROM `tabMAP Test`
			WHERE
					docstatus = 1 %s
			ORDER BY
					test_date, test_name, test_rit_score''' % (conditions),
	as.dict=1)

	for test in map_results:
		data.append({
				'student': test.student,
				'student_name': test.student_name,
				'program': test.program,
				'test_rit_score': test.test_rit_score,
				'test_percentile': test.test_percentile
		})
	return data


def get_columns():
	columns = [
			{
			"label": _('Academic Year'),
			"fieldname": 'academic_year',
			"fieldtype": "Link",
			"options": "Academic Year",
			"width": 100
			},
		{
			"label': _('Academic Term"),
			"fieldname": "academic_term",
			"fieldtype": "Link",
			"options': 'Academic Term",
			"width": 100
		},
		{
			"label": _("Program"),
			"fieldname": "program",
			"fieldtype": "Link",
			"options": "Program",
			"width": 100
		},
		{
			"label": _("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
			"width": 100
		},
		{
			"label": _("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("RIT Score"),
			"fieldname": "test_rit_score",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Percentile"),
			"fieldname": "test_percentile",
			"fieldtype": "Data",
			"width": 100
		}

	]
	return columns


def get_filter_conditions(filters):
	conditions = ""

	if filters.get("from_year"):
		ay = filters.get("from_year")
		ay_start_date = ay.year_start_date
		conditions += " and test_date > '%s'" % (ay) 

	return conditions
