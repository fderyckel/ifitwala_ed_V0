// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Academic Term', {
	refresh: function(frm) {
	},

	term_start_date: function(frm) {
		if(frm.doc.term_start_date && !frm.doc.term_end_date) {
			var four_month_from_now = frappe.datetime.add_months(frm.doc.term_start_date, 4);
			frm.set_value('term_end_date' = frappe.datetime.add_days(four_month_from_now, -1));
		}
	}
});
