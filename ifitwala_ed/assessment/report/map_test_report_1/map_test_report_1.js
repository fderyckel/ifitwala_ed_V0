// Copyright (c) 2016, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MAP Test Report 1"] = {
	"filters": [ 
		{
			"fieldname":"from_year",
			"label": __("From Academic Year"),
			"fieldtype": "Link", 
			"options": "Academic Year"
		},
		{
			"fieldname":"to_year",
			"label": __("To Academic Year"),
			"fieldtype": "Link", 
			"options": "Academic Year"
		},
		{
			"fieldname":"program",
			"label": __("Program"),
			"fieldtype": "Link", 
			"options": "Academic Year"
		},
		{
			"fieldname":"student",
			"label": __("Student"),
			"fieldtype": "Link", 
			"options": "Student"
		},
		{ 
			"fieldname":"math_rit",
			"label": __("Math RIT"),
			"fieldtype": "Int"
		},
		{ 
			"fieldname":"math_ile",
			"label": __("Math Percentile"),
			"fieldtype": "int"
		},
		

	]
};
