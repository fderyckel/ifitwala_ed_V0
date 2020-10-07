# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns, data, chart = [], [], []

	args = frappe._dict()

	args["from_year"] = filters.get("from_year")
	args["to_year"] = filters.get("to_year")
	args["program"] = filters.get("program")
	args["student"] = filters.get("student")

	returned_value = get_formatted_results(args)



	columns = get_columns()



	return columns, data


def get_formatted_results(args):
	cond, cond1, cond2, cond3, cond4 = " ", " ", " ", " ", " "
	args_list = [args.from_year]

	if args.to_year:
		cond = " and ar.to_year=%s"
		args_list.append(args.to_year)
	if args.program:
		cond1 = " and ar.program=%s"
		args_list.append(args.program)
	if args.student:
		cond2 = " and ar.student=%s"
		args_list.append(args.student)

	create_total_dict = False

	map_results = frappe.db.sql('''
			SELECT
			

	''')


def get_columns():
	columns = [
		_("Academic Year") + ":Link/Academic Year:90",
		_("Academic Term") + "Link/Academic Term::90",
		_("Program") + "::90",
		_("Student") + "Link/Student::180",
		_("Math RIT") + "::50",
		_("Math Percentile") + "::50"
	]
	return columns
