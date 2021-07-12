// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Attendance', {
	onload: function(frm) {
		frm.add_fetch("course_scedule", "schedule_date", "date");
		frm.add_fetch("course_schedule", "student_group", "student_group");
	}
});
