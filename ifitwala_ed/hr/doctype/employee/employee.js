// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.provide('ifitwala_ed.hr');
ifitwala_ed.hr.EmployeeController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: 'frappe.core.doctype.user.user.user_query',
				filters: {ignore_user_type: 1}
			}
		}
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: 'ifitwala_ed.controllers.queries.employee_query'}
		}
	},

	employee_salutation: function() {
		if(this.frm.doc.employee_salutation) {
			this.frm.set_value("employee_gender", {
				"Mr": "Male",
				"Mrs": "Female",				
				"Ms": "Female",
				"Miss": "Female",
				"Master": "Male",
				"Madam": "Female"
			}[this.frm.doc.employee_salutation]);
		}
	},

});

frappe.ui.form.on('Employee', {

	refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Employee'};
		if (!frm.is_new())  {
			frappe.contacts.render_address_and_contact(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}
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

frappe.ui.form.on('Employee Internal Work History', {

});

cur_frm.cscript = new ifitwala_ed.hr.EmployeeController({frm: cur_frm});
