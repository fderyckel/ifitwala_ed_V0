// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Holiday List', {
	refresh: function(frm) {
    if(frm.doc.holidays) {
      frm.set_value('total_holidays', frm.doc.holidays.length);
			var time_diff = frappe.datetime.get_day_diff(frm.doc.to_date, frm.doc.from_date);
			frm.set_value('total_working_days', time_diff - frm.doc.holidays.length)
	},

  from_date: function(frm) {
    if(frm.doc.from_date && !frm.doc.to_date)  {
      var a_year_from_start = frappe.datetime.add_months(frm.doc.from_date, 12);
      frm.set_value('to_date', frappe.datetime.add_days(a_year_from_start, - 1));
    }
  }
});
