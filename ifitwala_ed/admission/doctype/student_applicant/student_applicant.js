// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Applicant', {
  setup: function(frm) {
    frm.add_fetch('guardian', 'guardian_full_name', 'guardian_name');
  },

  refresh: function(frm) {
    if (frm.doc.application_status === 'Applied' && frm.doc.status === 1) {
      frm.add_custom_button(__('Approve'), function() {
        frm.set_value('application_status', 'Approved');
        frm.save_or_update();
      }, 'Actions');

      frm.add_custom_button(__('Reject'), function() {
        frm.set_value('application_status', 'Rejected');
        frm.save_or_update();
      }, 'Actions');
    }

    if (frm.doc.application_status === 'Approved' && frm.doc.status === 1) {
      frm.add_custom_button(__('Enroll'), function()  {
        frm.events.enroll(frm)
      }).addClass('btn-primary');

      frm.add_custom_button(__('Reject'), function() {
        frm.set_value('application_status', 'Rejected');
        frm.save_or_update();
      }, 'Actions');
    }

    frappe.realtime.on("enroll_student_progress", function(data) {
      if(data.progress) {
        frappe.hide_msgprint(true);
        frappe.show_progress(__("Enrolling student"), data.progress[0],data.progress[1]);
      }
    });
  },

  enroll: function(frm) {
		frappe.model.open_mapped_doc({
			method: "ifitwala_ed.ifitwala_ed.api.enroll_student",
			frm: frm
		})
	}
});

frappe.ui.form.on('Student Sibling', {
	setup: function(frm) {
		frm.add_fetch("student", "title", "sibling_name");
		frm.add_fetch("student", "gender", "sibling_gender");
		frm.add_fetch("student", "date_of_birth", "sibling_date_of_birth");
	}
});
