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
	chart = get_chart_data(data)

	return columns, data, None, chart

def get_columns(filters=None):
	columns = [
			{
				"label": _("Academic Year"),
				"fieldname": "academic_year",
				"fieldtype": "Link",
				"options": "Academic Year",
				"width": 125
			},
			{
				"label": _("Academic Term"),
				"fieldname": "academic_term",
				"fieldtype": "Link",
				"options": "Academic Term",
				"width": 175
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
				"width": 120
			},
			{
				"label": _("Median RIT Score"),
				"fieldname": "median_rit",
				"fieldtype": "Data",
				"width": 120
			},
			{
				"label": _("Median Percentile"),
				"fieldname": "median_percentile",
				"fieldtype": "Data",
				"width": 120
			}
	]

	return columns

def get_data(filters = None):
	conditions = get_filter_conditions(filters)
	data = frappe.db.sql("""
			SELECT DISTINCT academic_year, academic_term, discipline, program,
							median(test_rit_score) OVER (PARTITION BY academic_term, program, discipline) AS median_rit,
							median(test_percentile) OVER (PARTITION BY academic_term, program, discipline) AS median_percentile
			FROM `tabMAP Test`
			WHERE
					docstatus = 0 %s
			ORDER BY
					academic_term, program""" % (conditions),  as_dict=1)
	return data




def get_chart_data(data):
	if not data:
		return None

	labels =  []
	datasets = []
	terms=[]

	for entry in data:
		if entry.get("program") not in labels:
			labels.append(entry.get("program"))
		if entry.get("academic_term") not in terms:
			terms.append(entry.get("academic_term"))

	for t in terms:
		values=[]
		for l in labels:
			wtf = 0
			for entry in data:
				if entry.get("academic_term")==t and entry.get("program")==l:
					values.append(entry.get("median_rit"))
					wtf+=1
			if wtf  ==  0:
				values.append(0)
		datasets.append({"name": _(t), "values":values})

	return {
		"data": {
			"labels": labels,
			"datasets": datasets
		},
		"type": "bar",
		"height": 300,
		"axis": {
			"y": {
				"min": 150
				}
				}
	}


def get_filter_conditions(filters):
	conditions = ""

	if filters.get('from_date') and filters.get('to_date'):
		conditions += " and test_date BETWEEN '%s' and '%s'" % (filters.get("from_date"), filters.get("to_date"))

	if filters.get("discipline"):
		conditions += " and discipline = '%s' " % (filters.get("discipline"))

	if filters.get("program"):
			conditions += " and program = '%s' " % (filters.get("program"))

	if filters.get("academic_term"):
		conditions += " and academic_term = '%s' " % (filters.get("academic_term"))

	if filters.get("academic_year"):
		conditions += " and academic_year = '%s' " % (filters.get("academic_year"))

	return conditions
