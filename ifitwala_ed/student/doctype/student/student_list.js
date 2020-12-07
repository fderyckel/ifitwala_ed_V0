// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.listview_settings['Student'] = {
	filters: [["enabled","=", "1"]],
	hide_name_column: true, 
	get_indicator: function(doc) {
		return [__(doc.student_gender), {
            		"Male": "blue",
            		"Other": "purple",
            		"Female": "red"
            		}[doc.student_gender]];
	}
};
