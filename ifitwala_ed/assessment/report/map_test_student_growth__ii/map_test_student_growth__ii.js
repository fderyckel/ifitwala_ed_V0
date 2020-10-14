// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MAP Test Student Growth II"] = {
	"filters": [
		{
			"fieldname":"student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student",
			"reqd": 1
		},
		{
			"fieldname": "discipline",
			"label": __("Test Type"),
			"fieldtype": "Select",
			"options": "\nMathematics\nLanguage\nReading"
		},
		{
			"fieldname": "result_type",
			"label": __("Result Type"),
			"fieldtype": "Select",
			"options": "\nRIT Score\nPercentile"
		}

	]
};
