// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting', {
	onload: function(frm) {
	 	frm.trigger('department');
	},
	refresh: function(frm) {
		frm.trigger('department');
	},
	department: function(frm) {
		frm.trigger('department');
	},
	department: function(frm) {
		if (frm.doc.department && !frm.doc.attendees) {
			frappe.call({
				method: 'ifitwala_ed.school_settings.doctype.meeting.meeting.get_attendees',
				args: {
					'department': frm.doc.department
				},
				callback: function(r) {
					frm.set_value('attendees','');
					if (r.message) {
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(cur_frm.doc, 'Meeting Attendee', 'attendees');
							row.attendee = d.attendee;
							//row.full_name = d.full_name;
						});
					}
					refresh_field('attendees');
				}
			});
		}
	}
 });

frappe.ui.form.on('Meeting Attendee', {
	attendees_add: function(frm){
		frm.fields_dict['attendees'].grid.get_field('attendee').get_query = function(doc){
			var attendee_list = [];
			if(!doc.__islocal) attendee_list.push(doc.name);
			$.each(doc.attendees, function(idx, val){
				if (val.attendee) attendee_list.push(val.attendee);
			});
			return { filters: [['Employee', 'name', 'not in', attendee_list]] };
		};
	}
});
