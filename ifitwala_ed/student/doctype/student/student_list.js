// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.listview_settings['Student'] = {
	filters: [["enabled","=", "1"]], 
	get_indicator: function(doc) {
		var indicator = [__(doc.student_gender), frappe.utils.guess_colour(doc.student_gender), "student_gender,=," + doc.student_gender];
		indicator[1] = {"Male": "blue", "Female": "pink", "Other":"purple"}[doc.student_gender];
		return indicator;
	}
};
