// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MAP Test Report 1"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -24),
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
		},
		{
			"fieldname": "discipline",
			"label": __("Test Type"),
			"fieldtype": "Select",
			"options": "\nMathematics\nLanguage\nReading",
			"reqd": 1
		},
		{
			"fieldname":"program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"fieldname":"student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		}

	]
};
