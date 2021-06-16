// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student', {
  setup: function(frm) {
    frm.set_query('student', 'siblings', function(doc) {
      return {
        'filters': {
          'name': ['!=', doc.name]
        }
      };
    });
  },

  refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Student'};

		if (!frm.is_new()) {
			frappe.contacts.render_address_and_contact(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}

  }
});
