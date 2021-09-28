// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.listview_settings['Employee'] = {
	hide_name_column: true,
	filters: [["status","=", "Active"]],
	get_indicator: function(doc) {
		var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		indicator[1] = {"Active": "green", "Temporary Leave": "red", "Left": "darkgrey", "Suspended": "orange"}[doc.status];
		return indicator;
	}
};
