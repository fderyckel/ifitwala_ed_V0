// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting', {
	refresh: function(frm) {
	},
	
	meeting_organizer: function(frm) {
		if(frm.doc.department && !frm.doc.meeting_organizer) {
			frm.set_value('meeting_organizer', frappe.session.user);
		}
	},

	department: function(frm) {
    frm.events.get_attendees(frm);
  },

  get_attendees: function(frm) {
    frm.set_value('attendees',[]);
    frappe.call({
      method: 'get_attendees',
      doc:frm.doc,
      callback: function(r) {
        if(r.message) {
          frm.set_value('attendees', r.message);
        }
      }
    })
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
