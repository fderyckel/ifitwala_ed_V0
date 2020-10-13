# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data)

	return columns, data, None, chart


def get_columns(filters=None):
	columns = [
			{
				"label": _("Test Date"),
				"fieldname": "test_date",
				"fieldtype": "Date",
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
				"width": 150
			},
			{
				"label": _("Student Name"),
				"fieldname": "student_name",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("Discipline"),
				"fieldname": "discipline",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("RIT Score"),
				"fieldname": "test_rit_score",
				"fieldtype": "Data",
				"width": 80
			},
			{
				"label": _("Percentile"),
				"fieldname": "test_percentile",
				"fieldtype": "Data",
				"width": 80
			}
	]

	return columns

def get_data(filters = None):
	data = []
	conditions = get_filter_conditions(filters)
	map_results = frappe.db.sql("""
			SELECT student, student_name, program, test_percentile, test_rit_score, academic_term, test_date, discipline
			FROM `tabMAP Test`
			WHERE
					docstatus = 0 %s
			ORDER BY
					test_date, discipline, test_rit_score""" % (conditions),  as_dict=1)

	for test in map_results:
		data.append({
				'student': test.student,
				'discipline': test.discipline,
				'student_name': test.student_name,
				'program': test.program,
				'test_rit_score': test.test_rit_score,
				'test_percentile': test.test_percentile,
				'test_date': test.test_date,
				'academic_term': test.academic_term
		})

	return data

def get_chart_data(data):
	if not data:
		return None

	labels =  []
	math = []
	reading = []
	langauge = []

	for entry in data:
		if entry.get("academic_term") not in labels:
			labels.append(entry.get("academic_term"))
		if entry.get("discipline") == "Mathematics":
			math.append(entry.get("test_percentile"))
		if entry.get("discipline") == "Reading":
			reading.append(entry.get("test_percentile"))
		if entry.get("discipline") == "Language":
			language.append(entry.get("test_percentile"))

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Math Percentile"),
					"values": math
				},
				{
					"name": _("Reading Percentile"),
					"values": reading
				},
				{
					"name": _("Language Percentile"),
					"values": language
				}
			]
		},
		"type": "line"

	}





def get_filter_conditions(filters):
	conditions = ""

	if filters.get("discipline"):
		conditions += " and discipline = '%s' " % (filters.get("discipline"))

	if filters.get("student"):
		conditions += " and student = '%s' " % (filters.get("student"))

	return conditions
