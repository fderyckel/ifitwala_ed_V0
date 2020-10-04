// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting', {
	
	onload: function(frm, cdt, cdn) { 
		if (frm.doc.department) {
			frm.set_query("employee", "members", function(doc, cdt, cdn) {
				return{
					query: "ifitwala_ed.school_settings.doctype.meeting.meeting.get_department_members",
					filters: {
						'department': frm.doc.department
					}
				}
			});
		}

	}
});
