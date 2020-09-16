// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_dev.hr");
ifitwala_dev.hr.EmployeeController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: "ifitwala_dev.controllers.queries.employee_query"} }
	},

	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},

});


frappe.ui.form.on('Employee', {

	refresh: function(frm) {

	}, 
	
	create_user: function(frm) {
		if (!frm.doc.professional_email)
		{
			frappe.throw(__("Please enter Professional Email"))
		}
		frappe.call({
			method: "ifitwala_dev.hr.doctype.employee.employee.create_user",
			args: { employee: frm.doc.name, email: frm.doc.professional_email },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	}
});

cur_frm.cscript = new ifitwala_dev.hr.EmployeeController({frm: cur_frm});
