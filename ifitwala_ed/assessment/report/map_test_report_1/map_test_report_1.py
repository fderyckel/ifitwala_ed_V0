# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
	if not filters:
		filters = {}

	columns, data, chart = [], [], []

	data = get_data(filters)
	columns = get_columns(filters)

	return columns, data, chart


def get_data(filters = None):
	conditions = get_filter_conditions(filters)

	map_results = frappe.db.sql("""
			SELECT student, student_name, program, test_percentile, test_rit_score, test_date, discipline, academic_year
			FROM `tabMAP Test`
			WHERE
					docstatus = 1 %s
			ORDER BY
					test_date, discipline, test_rit_score""" % (conditions), as_dict=1)

	for test in map_results:
		data.append({
				'student': test.student,
				'academic_year': test.academic_year,
				'discipline': test.discipline,
				'student_name': test.student_name,
				'program': test.program,
				'test_rit_score': test.test_rit_score,
				'test_percentile': test.test_percentile,
				'test_date': test.test_date
		})
	return data


def get_columns(filters=None):
	columns = [
			{
			"label": _("Test Date"),
			"fieldname": "test_date",
			"fieldtype": "Date",
			"width": 150
			},
		{
			"label": _("Academic Term"),
			"fieldname": "academic_term",
			"fieldtype": "Link",
			"options": "Academic Term",
			"width": 150
		},
		{
			"label": _("Program"),
			"fieldname": "program",
			"fieldtype": "Link",
			"options": "Program",
			"width": 150
		},
		{
			"label": _("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
			"width": 150
		},
		{
			"label": _("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Discipline"),
			"fieldname": "discipline",
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
	data = [] 
	conditions = ""

	if filters.get("start_date"):
		conditions += " and test_date > '%s' " % (filters.get("start_date"))

	return conditions
