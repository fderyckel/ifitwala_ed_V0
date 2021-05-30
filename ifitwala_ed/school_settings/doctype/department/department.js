// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	onload: function(frm) {
		if (frm.doc.organization) {
			frm.set_query('school', function() {
				return {
					'filters': {'organization': (frm.doc.organization)}
				};
			});
		}
	},

	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Update Dpt Member Email Group'), function() {
				frappe.call({
					method: 'ifitwala_ed.organization_settings.doctype.department.department.update_dpt_email',
					args: {
						'doctype': 'Department',
						'name': frm.doc.name
					}
				});
			}, __('Communication'));

			frm.add_custom_button(__('Newsletter'), function() {
				frappe.call({
					method: 'ifitwala_ed.school_settings.doctype.department.department.create_prefilled_newsletter',
					args: {},
					callback: function(data) {
						frappe.set_route('Form', 'Newsletter', data.message.name)
					}
				});
				//frappe.route_options = {'Newsletter Email Group.email_group': frm.doc.name};
				//frappe.set_route('List', 'Newsletter');
			}, __('Communication'));

			frm.add_custom_button(__('Meetings'), function() {
				frappe.route_options = {'department': frm.doc.name};
				frappe.set_route('List', 'Meeting');
			});
		}
	},

	school: function(frm) {
		if (frm.doc.school) {
			frappe.call({
				'method': 'frappe.client.get',
				args: {
					doctype: 'School',
					name: frm.doc.school
				},
				callback: function(data) {
					let values = {
						'organization': data.message.organization
					};
					frm.set_value(values)
				}
			});
		}
	}

});
