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

			frm.add_custom_button(__('Meetings'), function() {
				frappe.route_options = {'department': frm.doc.name};
				frappe.set_route('List', 'Meeting');
			});
		}
	}

});

// to filter out Department Members that have already been picked out. 
frappe.ui.form.on('Department Member', {
	members_add: function(frm){
		frm.fields_dict['members'].grid.get_field('member').get_query = function(doc){
			var employee_list = [];
			if(!doc.__islocal) employee_list.push(doc.name);
			$.each(doc.members, function(idx, val){
				if (val.member) employee_list.push(val.member);
			});
			return { filters: [['Employee', 'name', 'not in', employee_list]] };
		};
	}
});
