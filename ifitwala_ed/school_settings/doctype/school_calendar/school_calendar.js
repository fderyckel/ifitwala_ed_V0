// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('School Calendar', {
  onload: function(frm) {

    frm.set_query('academic_year', function() {
      return {
        'filters': {
          'school': (frm.doc.school)
        }
      }
    });
  },

  academic_year: function(frm) {
    frm.events.get_terms(frm);
  },

  get_terms: function(frm) {
    frm.set_value('terms', []);
    frappe.call({
      method: 'get_terms',
      doc: frm.doc,
      callback: function(r) {
        if(r.message) {
          frm.set_value('terms', r.message);
        }
      }
    })
  };


	// refresh: function(frm) {

	// }
});
