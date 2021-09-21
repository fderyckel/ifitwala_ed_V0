// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Feedback', {
	onload: function(frm) {
		frm.add_fetch('training_event', 'event_name', 'event_name');
		frm.add_fetch('training_event', 'trainer_name', 'trainer_name');
	}
});
