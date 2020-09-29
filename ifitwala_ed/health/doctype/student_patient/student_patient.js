// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

cur_frm.add_fetch('student', 'student_gender', 'gender');
cur_frm.add_fetch('student', 'student_date_of_birth', 'date_of_birth');

frappe.ui.form.on('Student Patient', {
	refresh: function(frm) {

	}
});
