// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Education Settings', {

	onload:  function(frm) {
		frm.set_query('current_academic_term', function() {
			return {
				'filters':{
					'academic_year': (frm.doc.academic_year)
				}
			};
		});

	},

	refresh: function(frm) {

	}
});
