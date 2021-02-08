// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Admission', {
  admission_end_date: function(frm) {
    if (frm.doc.admission_start_date && frm.doc.admission_end_date <= frm.doc.admission_start_date) {
      frappe.set_value('admission_end_date', "");
      frappe.throw(_('The Admission End Date should after the Admission Start Date. Please adjust.'))
    }
  }
});
