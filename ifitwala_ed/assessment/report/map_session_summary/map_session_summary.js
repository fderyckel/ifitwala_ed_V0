// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MAP Session Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -36),
			"reqd": 0
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 0
		},
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 0
		},
		{
			"fieldname":"academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term",
			"reqd": 0,
			"get_query": function() {
				return{
					filters: {
						"academic_year": frappe.query_report.get_filter_value('academic_year')
					}
				};
			}
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
			"options": "Program",
			"reqd": 0
		},
		{
			"fieldname": "result_type",
			"label": __("Result Type"),
			"fieldtype": "Select",
			"options": "\nRIT Score\nPercentile"
		}

	]
};
