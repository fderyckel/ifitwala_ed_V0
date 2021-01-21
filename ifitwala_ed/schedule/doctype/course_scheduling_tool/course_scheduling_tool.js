// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course Scheduling Tool', {
  setup: function(frm) {
    frm.add_fetch('student_group', 'program', 'program');
    frm.add_fetch('student_group', 'course', 'course');
    frm.add_fetch('student_group', 'academic_year', 'academic_year');
    frm.add_fetch('student_group', 'academic_term', 'academic_term');
  },

  onload: function(frm) {
    frm.set_query('course', function() {
      return {
        'filters': (frm.doc.)
      };
    });
  },

  refresh: function(frm) {
    frm.disable_save();

  }
});
