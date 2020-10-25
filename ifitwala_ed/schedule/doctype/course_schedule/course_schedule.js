// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

cur_frm.add_fetch("student_group", "course", "course")

frappe.ui.form.on('Course Schedule', {
	refresh: function(frm) {

	}
});
