// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('School Event', {
  onload: function(frm) {
    frm.set_query('reference_type', function(txt) {
      return {
        "filters": {
          "issingle": 0,
        }
      };
    });
  },

  refresh: function(frm) {
    if (frm.doc.reference_type && frm.doc.reference_name) {
      frm.add_custom_button(__(frm.doc.reference_name), function() {
        frappe.set_route('Form', frm.doc.reference_type, frm.doc.reference_name);
      });
    }
  }
});
