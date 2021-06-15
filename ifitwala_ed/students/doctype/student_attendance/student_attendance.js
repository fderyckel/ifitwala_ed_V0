// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

cur_frm.add_fetch("course_scedule", "schedule_date", "date")
cur_frm.add_fetch("course_schedule", "student_group", "student_group")

frappe.ui.form.on('Student Attendance', {
	// refresh: function(frm) {

	// }
});
