// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Academic Year', {
	refresh: function(frm) {
	},

	year_start_date: function(frm) {
		if(frm.doc.year_start_date && !frm.doc.year_end_date) {
			var a_year_from_start = frappe.datetime.add_months(frm.doc.year_start_date, 12);
			frm.set_value('year_end_date', frappe.datetime.add_days(a_year_from_start, - 1));
		}
	}
});
