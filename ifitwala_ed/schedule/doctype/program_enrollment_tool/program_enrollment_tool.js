// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Program Enrollment Tool', {

	setup: function(frm) {
		frm.add_fetch('student', 'student_full_name', 'student_name');
	},

	onload: function(frm) {
		frm.set_query('academic_term', function() {
			return {
				'filters': {
					'academic_year': (frm.doc.academic_year)
				}
			};
		});
		frm.set_query('new_academic_term', function() {
			return {
				'filters': {
					'new_academic_year': (frm.doc.new_academic_year)
				}
			};
		});
	},

	refresh: function(frm) {
		frm.disable_save();
		frm.fields_dict.enroll_students.$input.addClass(' btn btn-primary');
		frappe.realtime.on("program_enrollment_tool", function(data) {
			frappe.hide_msgprint(true);
			frappe.show_progress(__("Enrolling students"), data.progress[0], data.progress[1]);
		});
	},

	// logic for the "get students" button.  Calling the get_students funciton in .py file.
	get_students: function(frm) {
		frm.set_value("students", []);
		frappe.call({
			method: "get_students",
			doc: frm.doc,
			callback: function(r) {
				if(r.message) {
					frm.set_value("students", r.message);
				}
			}
		});
	},

	// logic for the "enroll student" button.
	enroll_students: function(frm) {
		frappe.call({
			method: "enroll_students",
			doc:frm.doc,
			callback: function(r) {
				frm.set_value("students", []);
				frappe.hide_msgprint(true);
			}
		});
	}
});
