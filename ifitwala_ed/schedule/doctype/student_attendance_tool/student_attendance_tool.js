// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt
frappe.provide("education");

frappe.ui.form.on('Student Attendance Tool', {
	onload: function(frm) {
		frm.set_query('student_group', function() {
			return {
				'filters': {
					'group_based_on': frm.doc.group_based_on,
					'status': 'Active'
				}
			};
		});
	},

	refresh: function(frm) {
		if (frappe.route_options) {
			frm.set_value('based_on', frappe.route_options.based_on);
			frm.set_value('student_group', frappe.route_options.student_group);
			frm.set_value('course_schedule', frappe.route_options.course_schedule);
			frappe.route_options = null;
		}
		frm.disable_save();
	},

	based_on: function(frm) {
		if (frm.doc.based_on == 'student_group') {
			frm.set_value('course_schedule', '');
		} else {
			frm.set_value('student_group', '');
		}
	},

	student_group: function(frm) {
		if ((frm.doc.student_group && frm.doc.date) || frm.doc.course_schedule) {
			var method = "ifitwala_ed.schedule.doctype.student_attendance_tool.student_attendance_tool.get_student_attendance_records";

			frappe.call({
				method: method,
				args: {
					based_on: frm.doc.based_on,
					student_group: frm.doc.student_group,
					date: frm.doc.date,
					course_schedule: frm.doc.course_schedule
				},
				callback: function(r) {
					frm.events.get_students(frm, r.message);
				}
			})
		}
	},

	date: function(frm) {
		if (frm.doc.date > frappe.datetime.get_today()) {
			frappe.throw(__('Cannot mark attendance for future dates.'));
		}
		frm.trigger('student_group');
	},

	course_schedule: function(frm) {
		frm.trigger('student_group');
	},

	get_students: function(frm, students) {
		if (!frm.students_area) {
			frm.students_area = $('<div>')
				.appendTo(frm.fields_dict.students_html.wrapper);
		}
		students = students || [];
		frm.students_editor = new education.StudentsEditor(frm, frm.students_area, students);
	}
});

education.StudentsEditor = class StudentsEditor {
	constructor(frm, wrapper, students) {
		this.wrapper = wrapper;
		this.frm = frm;
		if (students.length > 0) {
			this.make(frm, students);
		} else {
			this.show_empty_state();
		}
	}

};
