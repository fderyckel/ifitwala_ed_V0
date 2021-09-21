// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Event', {
	onload_post_render: function (frm) {
		frm.get_field.('employees').grid.set_multiple_add('employee');
	}
});

frappe.ui.form.on('Training Event Employee', {
	employee: function (frm) {
		frm.events.set_employee_query(frm);
	}
});
