// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Update Dpt Member Email Group'), function() {
				frappe.call({
					method: 'ifitwala_ed.school_settings.doctype.department.department.update_dpt_email',
					args: {
						'doctype': 'Department',
						'name': frm.doc.name
					}
				});
			}, __('Communication'));

			frm.add_custom_button(__('Newsletter'), function() {
				frappe.route_options = {'Newsletter Email Group.email_group': frm.doc.name};
				frappe.set_route('List', 'Newsletter');
			}, __('Communication'));

			frm.add_custom_button(__('Set New Meeting'), function() {
				frappe.route_options = {'department': frm.doc.name};
				frappe.set_route('Form', 'Meeting');
			}, __('Meeting'));

			frm.add_custom_button(__('Past Meetings'), function() {
				frappe.route_options = {'department': frm.doc.name};
				frappe.set_route('List', 'Meeting');
			}, __('Meeting'));
		}
	}

});
