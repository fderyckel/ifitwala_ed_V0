// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting', {
	setup: function(frm){
		if (frm.doc.meeting_organizer == "" | frm.doc.meeting_organizer == null) {
			frm.doc.meeting_organizer = frappe.session.user;
		}
	},

	refresh: function(frm) {
	},

	team: function(frm) {
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
