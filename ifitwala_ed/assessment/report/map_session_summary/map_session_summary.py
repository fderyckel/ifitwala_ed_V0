# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	#chart = get_chart_data(data)

	return columns, data, None #, chart

def get_columns(filters=None):
	columns = [
			{
				"label": _("Academic Year"),
				"fieldname": "academic_year",
				"fieldtype": "Link",
				"options": "Academic Year",
				"width": 100
			},
			{
				"label": _("Academic Term"),
				"fieldname": "academic_term",
				"fieldtype": "Link",
				"options": "Academic Term",
				"width": 125
			},
			{
				"label": _("Discipline"),
				"fieldname": "discipline",
				"fieldtype": "Data",
				"width": 120
			},
			{
				"label": _("Program"),
				"fieldname": "program",
				"fieldtype": "Link",
				"options": "Program",
				"width": 125
			},
			{
				"label": _("Median RIT Score"),
				"fieldname": "median",
				"fieldtype": "Data",
				"width": 80
			}
	]

	return columns

def get_data(filters = None):
	data = []
	conditions = get_filter_conditions(filters)
	map_results = frappe.db.sql("""
			SELECT DISTINCT academic_year, academic_term, discipline, program, median(test_rit_score) OVER (PARTITION BY academic_term, program, discipline) AS median
			FROM `tabMAP Test`
			WHERE
					docstatus = 0 %s
			ORDER BY
					academic_term, program""" % (conditions),  as_dict=1)

	for result in map_results:
		data.append({
				'academic_year': result.academic_year,
				'academic_term': result.academic_term,
				'discipline': result.discipline,
				'program': result.program,
				'median': result.median
		})

	return data





def get_filter_conditions(filters):
	conditions = ""

	if filters.get("discipline"):
		conditions += " and discipline = '%s' " % (filters.get("discipline"))

	if filters.get("program"):
			conditions += " and program = '%s' " % (filters.get("program"))

	if filters.get("academic_term"):
		conditions += " and academic_term = '%s' " % (filters.get("academic_term"))

	if filters.get("academic_year"):
		conditions += " and academic_year = '%s' " % (filters.get("academic_year"))

	return conditions
