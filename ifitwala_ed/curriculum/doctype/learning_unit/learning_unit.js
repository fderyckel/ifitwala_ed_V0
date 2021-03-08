// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Learning Unit', {
	onload: function(frm) {
    if (frm.doc.program) {
      frm.set_query ('course', function() {
        return {
          query: 'ifitwala_ed.curriculum.doctype.learning_unit.learning_unit.get_courses',
          filters: {
            'program': frm.doc.program
          }
        }
      });
    }
	},

	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Add Learning Unit to Courses'), function() {
				frm.trigger('add_lu_to_courses');
			}, __('Action'));
		}

	},

	add_lu_to_courses: function(frm) {
		get_courses_without_given_lu(frm.doc.name).then(r => {
			if (r.message.length) {
				frappe.prompt([
					{
						fieldname: 'courses',
						label: __('Courses'),
						fieldtype: 'MultiSelectPills',
						get_data: function() {
							return r.message;
						}
					}
				],
				function(data) {
					frappe.call({
						method: 'ifitwala_ed.curriculum.doctype.learning_unit.learning_unit.add_lu_to_courses',
						args: { 'lu': frm.doc.name, 'courses': data.courses }, 
						callback: function(r) {
							if (!r.exc) {
								frm.reload_doc();
							}
						},
						freeze: true,
						freeze_message: __('...Adding Learning Unit to courses')
					});
				}, __('Add Learning Unit to Courses'), __('Add'));
			} else {
				frappe.msgprint(__('This Learning Unit has already been added to the course.'));
			}
		});
	},

	duration: function(frm) {
		if (frm.doc.start_date && frm.doc.duration) {
			frm.set_value('end_date', frappe.datetime.add_days(frm.doc.start_date, frm.doc.duration * 7))
		}
	}
});

let get_courses_without_given_lu = function(lu) {
	return frappe.call({
		type: 'GET',
		method: 'ifitwala_ed.curriculum.doctype.learning_unit.learning_unit.get_courses_without_given_lu',
		args: {'lu': lu}
	});
};
