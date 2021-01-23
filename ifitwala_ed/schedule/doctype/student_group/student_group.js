// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Group', {

	onload: function(frm) {
		frm.add_fetch('student', 'student_full_name', 'student_name');
		// will filter the academic terms  based on the chosen academic year.
		frm.set_query('academic_term', function() {
			return {
				filters: {
					'academic_year': (frm.doc.academic_year)
				}
			};
		});

		if (!frm.__islocal) {
			frm.set_query('student', 'students', function() {
				return{
					query: 'ifitwala_ed.schedule.doctype.student_group.student_group.fetch_students',
					filters: {
						'academic_year': frm.doc.academic_year,
						'group_based_on': frm.doc.group_based_on,
						'academic_term': frm.doc.academic_term,
						'program': frm.doc.program,
						'cohort': frm.doc.cohort,
						'course': frm.doc.course,
						'student_group': frm.doc.name
					}
				}
			});
		}

		if (frm.program) {
			frm.set_query('course', function() {
				return{
					query: 'ifitwala_ed.ifitwala_ed.api.get_courses_from_program',
					filters: {
						'program': frm.doc.program
					}
				}
			});
		}
	},

	refresh: function(frm) {

	},

	group_based_on: function(frm) {
		if (frm.doc.group_based_on == 'Cohort') {
			frm.doc.course = null;
			frm.set_df_property('program', 'reqd', 0);
			frm.set_df_property('course', 'reqd', 0);
		}
		else if (frm.doc.group_based_on == 'Course') {
			frm.set_df_property('program', 'reqd', 0);
			frm.set_df_property('course', 'reqd', 1);
		}
		else if (frm.doc.group_based_on == 'Activity') {
			frm.set_df_property('program', 'reqd', 0);
			frm.set_df_property('course', 'reqd', 1);
		}
	},

	get_students: function(frm) {
		if (frm.doc.group_based_on == "Cohort" || frm.doc.group_based_on == "Course") {
			var student_list = [];
			var max_roll_no = 0;
			$.each(frm.doc.students, function(i,d) {
				student_list.push(d.student);
				if (d.group_roll_number>max_roll_no) {
					max_roll_no = d.group_roll_number;
				}
			});

			if(frm.doc.academic_year) {
				frappe.call({
					method: "ifitwala_ed.schedule.doctype.student_group.student_group.get_students",
					args: {
						"academic_year": frm.doc.academic_year,
						"academic_term": frm.doc.academic_term,
						"group_based_on": frm.doc.group_based_on,
						"program": frm.doc.program,
						"cohort" : frm.doc.cohort,
						"course": frm.doc.course
					},
					callback: function(r) {
						if(r.message) {
							$.each(r.message, function(i, d) {
								if(!in_list(student_list, d.student)) {
									var s = frm.add_child("students");
									s.student = d.student;
									s.student_name = d.student_name;
									if (d.active === 0) {
										s.active = 0;
									}
									s.group_roll_number = ++max_roll_no;
								}
							});
							refresh_field("students");
							frm.save();
						} else {
							frappe.msgprint(__("Student Group is already updated."))
						}
					}
				})
			}
		} else {
			frappe.msgprint(__("Select students manually for the Activity based Group"));
		}
	}
});

frappe.ui.form.on('Student Group Instructor', {
	instructors_add: function(frm){
		frm.fields_dict['instructors'].grid.get_field('instructor').get_query = function(doc){
			let instructor_list = [];
			$.each(doc.instructors, function(idx, val){
				instructor_list.push(val.instructor);
			});
			return { filters: [['Instructor', 'name', 'not in', instructor_list]] };
		};
	}
});
