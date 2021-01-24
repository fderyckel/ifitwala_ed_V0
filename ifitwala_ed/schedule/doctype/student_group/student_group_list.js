// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.listview_settings['Course'] = {
	filters: [['disabled','=', '0']],
	hide_name_column: true,
	get_indicator: function(doc) {
		var indicator = [__(doc.disabled), frappe.utils.guess_colour(doc.disabled), "status,=," + doc.disabled];
		indicator[1] = {'0': 'green', '1': "darkgrey"}[doc.disabled];
		return indicator;
	}
};
