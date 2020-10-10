// Copyright (c) 2016, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MAP Test Student Growth"] = {
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
		}

	]
};
