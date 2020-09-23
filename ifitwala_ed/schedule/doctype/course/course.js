// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course', {
	refresh: function(frm) { 
		if (!cur_frm.doc.__islocal) {
			frm.add_custom_button(__('Add to Programs'), function() {
				frm.trigger('add_course_to_programs')
			}, __('Action'));
		}

	}, 
	
	add_course_to_programs: function(frm) {
		get_programs_without_course(frm.doc.name).then(r => {
			if (r.message.length) {
				frappe.prompt([
					{
						fieldname: 'programs',
						label: __('Programs'),
						fieldtype: 'MultiSelectPills',
						get_data: function() {
							return r.message;
						}
					},
					{
						fieldtype: 'Check',
						label: __('Is Mandatory'),
						fieldname: 'mandatory',
					}
				],
				function(data) {
					frappe.call({
						method: 'ifitwala_ed.schedule.doctype.course.course.add_course_to_programs',
						args: {
							'course': frm.doc.name,
							'programs': data.programs,
							'mandatory': data.mandatory
						},
						callback: function(r) {
							if (!r.exc) {
								frm.reload_doc();
							}
						},
						freeze: true,
						freeze_message: __('...Adding Course to Programs')
					})
				}, __('Add Course to Programs'), __('Add'));
			} else {
				frappe.msgprint(__('This course is already added to the existing programs'));
			}
		});
	}
	
});

let get_programs_without_course = function(course) {
	return frappe.call({
		type: 'GET',
		method: 'erpnext.education.doctype.course.course.get_programs_without_course',
		args: {'course': course}
	});
}
