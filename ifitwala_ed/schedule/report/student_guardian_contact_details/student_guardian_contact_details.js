// Copyright (c) 2016, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Guardian Contact Details"] = {
	"filters": [
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 1,
		},
		{
			"fieldname":"program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program",
		},
		{
			"fieldname":"student_group",
			"label": __("Student Group"),
			"fieldtype": "Link",
			"options": "Student Group",
			"reqd": 1
		},
	]
};
