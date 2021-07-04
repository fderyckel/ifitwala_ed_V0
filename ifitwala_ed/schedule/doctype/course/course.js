// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course', {
	setup: function(frm) {
		frm.add_fetch('team', 'school', 'school');
	},

	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			frm.add_custom_button(__('Add to Programs'), function() {
				frm.trigger('add_course_to_programs')
			}, __('Action'));
		}

		// to only suggest grade scale that are submitted (not cancel nor draft)
		frm.set_query('default_grade_scale', function(){
			return {
				filters: {
					docstatus: 1
				}
			}
		});

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

// to filter out assessment criteria that have already been picked out in the course.
frappe.ui.form.on('Course Assessment Criteria', {
	criteria_add: function(frm){
		frm.fields_dict['assessment_criteria'].grid.get_field('assessment_criteria').get_query = function(doc){
			var criteria_list = [];
			if(!doc.__islocal) criteria_list.push(doc.name);
			$.each(doc.assessment_criteria, function(idx, val){
				if (val.assessment_criteria) criteria_list.push(val.assessment_criteria);
			});
			return { filters: [['Assessment Criteria', 'name', 'not in', criteria_list]] };
		};
	}
});

let get_programs_without_course = function(course) {
	return frappe.call({
		type: 'GET',
		method: 'ifitwala_ed.schedule.doctype.course.course.get_programs_without_course',
		args: {'course': course}
	});
}
