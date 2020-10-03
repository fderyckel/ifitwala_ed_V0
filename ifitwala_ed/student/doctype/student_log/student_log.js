// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Log', {
	refresh: function(frm) { 
		frm.set_query('student_patient', function() {
			return {
				filters: {'enabled': '1'}
			};
		});

	}
});
