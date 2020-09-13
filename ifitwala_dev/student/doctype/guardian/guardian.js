// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guardian', {
	refresh: function(frm) {
		if(!frm.doc.user && !frm.is_new()) {
			frm.add_custom_button(__("Create and Invite as User"), function() {
				return frappe.call({
					method: "ifitwala_ed.students.doctype.guardian.guardian.invite_guardian",
					args: {
						guardian: frm.doc.name
					},
					callback: function(r) {
						frm.set_value("user", r.message);
					}
				});
			});
		}
	}
});
