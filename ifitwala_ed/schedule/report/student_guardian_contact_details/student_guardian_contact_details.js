// Copyright (c) 2016, ifitwala and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Guardian Contact Details"] = {
	"filters": [
		{
			"fieldname":"student_group",
			"label": __("Student Group"),
			"fieldtype": "Link",
			"options": "Student Group",
			"reqd": 1
		},
	]
};
