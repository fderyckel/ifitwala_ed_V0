// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee', {

	refresh: function(frm) {

	}, 
	
	create_user: function(frm) {
		if (!frm.doc.employee_professional_email)
		{
			frappe.throw(__("Please enter Professional Email"))
		}
		frappe.call({
			method: "ifitwala_ed.hr.doctype.employee.employee.create_user",
			args: { employee: frm.doc.name, email: frm.doc.employee_professional_email },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	}
});

