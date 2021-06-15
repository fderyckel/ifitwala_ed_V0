// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guardian', {
	refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Guardian'};
		if (!frm.is_new())  {
			frappe.contacts.render_address_and_contact(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}

		if(!frm.doc.user && !frm.is_new()) {
			frm.add_custom_button(__("Create and Invite as User"), function() {
				return frappe.call({
					method: "ifitwala_ed.student.doctype.guardian.guardian.invite_guardian",
					args: {
						guardian: frm.doc.name
					},
					callback: function(r) {
						frm.set_value("user", r.message);
					}
				});
			});
		}
	},

	salutation: function() {
		if(frm.doc.salutation) {
			frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[frm.doc.salutation]);
		}
	},
});
