// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Learning Unit', {
	onload: function(frm) {
    if (frm.doc.program) {
      frm.set_query ('course', function() {
        return {
          query: 'ifitwala_ed.curriculum.doctype.learning_unit.learning_unit.get_courses',
          filters: {
            'program': frm.doc.program
          }
        }
      });
    }
	},

	duration: function(frm) {
		if (frm.doc.start_date && frm.doc.duration) {
			frappe.set_value('end_date', frappe.datetime.add_days(frm.doc.start_date, frm.doc.duration * 7))
		}
	}
});
