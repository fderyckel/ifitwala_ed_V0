// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

cur_frm.add_fetch("student_group", "course", "course")

frappe.ui.form.on('Course Schedule', {

	onload: function(frm) {

	},


	refresh: function(frm) {

	},

	student_group: function(frm) {
		frm.events.get_instructors(frm);
	},

	get_instructors: function(frm) {
		frm.set_value('instructors',[]);
		frappe.call({
			method: 'get_instructors',
			doc:frm.doc,
			callback: function(r) {
				if(r.message) {
					frm.set_value('instructors', r.message);
				}
			}
		})
	}
});
