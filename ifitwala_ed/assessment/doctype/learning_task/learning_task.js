// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Learning Task', {
  onload: function(frm) {
    frm.set_query('grading_scale', function() {
      return {
        filters: {docstatus: 1}
      };
    });
  },

	refresh: function(frm) {
    if (frm.doc.status == 1) {
      frm.add_custom_button(__('Assessment Result Tool'), function() {
        frappe.route_options = {
          assessment_event: frm.doc.name,
          student_group: frm.doc.student_group
        }
        frappe.set_route('Form', 'Assessment Result Tool');
      });
    }

    frm.set_query('course', function() {
      return {
        query: 'ifitwala_ed.assessment.doctype.assessment_event.assessment_event.get_courses',
        filters: {
          'program': frm.doc.program
        }
      };
    });

    frm.set_query('academic_term', function() {
      return {
        filters: {'academic_year': frm.doc.academic_year}
      };
    });
	},

  course: function(frm) {
    if (frm.doc.course && frm.doc.maximum_points) {
      frappe.call({
        methods: 'ifitwala_ed.ifitwala_ed.api.get_assessment_criteria',
        args: {
          'course': frm.doc.course
        },
        callback: function(r) {
          if (r.message) {
            frm.doc.assessment_criteria = []
          }
        }
      });
    }
  }
});
