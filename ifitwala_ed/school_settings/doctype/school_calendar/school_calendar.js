// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('School Calendar', {
  refresh: function(frm) {

    frm.set_query('academic_year', function() {
      return {
        'filters': {
          'school': (frm.doc.school)
        }
      }
    });
  }

});
