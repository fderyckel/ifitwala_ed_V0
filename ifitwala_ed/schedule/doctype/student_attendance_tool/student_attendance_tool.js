// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Attendance Tool', {
	onload: function(frm) {
		frm.set_query('student_group', function() {
			return {
				'filters': {
					'group_based_on': frm.doc.group_based_on,
					'disabled': 0
				}
			};
		});
	},
	refresh: function(frm) {
		if (frappe.route_options) {
			frm.set_value('based_on', frappe.route_options.based_on);
			frm.set_value('student_group', frappe.route_options.student_group);
			frappe.route_options = null;
		}
		frm.disable_save();
	}
});
