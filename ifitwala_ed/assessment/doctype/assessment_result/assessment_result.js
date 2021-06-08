// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assessment Result', {
  onload: function(frm) {
    frm.set_query('grade_scale', function() {
      return {
        filters: {docstatus: 1}
      };
    });
  },

	refresh: function(frm) {
    if (frm.doc.status == 1) {
      frm.add_custom_button(__('Assessment Result Tool'), function() {
        frappe.route_options = {
          assessment_plan: frm.doc.name,
          student_group: frm.doc.student_group
        }
        frappe.set_route('Form', 'Assessment Result Tool');
      });
    }

	}
});
