// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Academic Year', {
	refresh: function(frm) {
		if (!frm.doc.islocal) {
			frm.add_custom_button(__('Create school Calendar'), function() {
				frm.events.start_school_calendar(frm);
				//frappe.route_options = { 'school': 'school', 'academic_year': 'title'};
				//frappe.set_route('Form', 'School Calendar');
			});
		}
	},

	year_start_date: function(frm) {
		if(frm.doc.year_start_date && !frm.doc.year_end_date) {
			var a_year_from_start = frappe.datetime.add_months(frm.doc.year_start_date, 12);
			frm.set_value('year_end_date', frappe.datetime.add_days(a_year_from_start, - 1));
		}
	},

	start_school_calendar: function(frm) {
		return frappe.call({
			method: 'ifitwala_ed.school_settings.doctype.academic_year.academic_year.start_school_calendar',
			args: {'school': frm.doc.school, 'academic_year':frm.doc.title},
			callback: function(r) {
				var doc = frappe.model.sync(r.message);
				frappe.set_route("Form", doc[0].doctype, doc[0].name);
			}
		});
	}
});
