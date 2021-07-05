// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course Schedule', {

	onload: function(frm) {
		frm.add_fetch('student_group', 'course', 'course');
		frm.add_fetch('course', 'calendar_event_color', 'calendar_event_color');
	},

	refresh: function(frm) {
		if (!frm.__islocal) {
			frm.add_custom_button(__("Take Attendance"), function() {
				frappe.route_options = {
					based_on: "Course Schedule",
					course_schedule: frm.doc.name
				}
				frappe.set_route("Form", "Student Attendance Tool");
			}).addClass("btn-primary");
		}
	},

	//student_group: function(frm) {
	//	frm.events.get_instructors(frm);
	//	frm.events.get_students(frm);
	//},

	//get_instructors: function(frm) {
	//	frm.set_value('instructors',[]);
	//	frappe.call({
	//		method: 'get_instructors',
	//		doc:frm.doc,
	//		callback: function(r) {
	//			if(r.message) {
	//				frm.set_value('instructors', r.message);
	//			}
	//		}
	//	})
	//},

	//get_students: function(frm) {
	//	frm.set_value('students',[]);
	//	frappe.call({
	//		method: 'get_students',
	//		doc:frm.doc,
	//		callback: function(r) {
	//			if(r.message) {
	//				frm.set_value('students', r.message);
	//			}
	//		}
	//	})
	//}
});
