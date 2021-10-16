// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

if(!window.ifitwala_ed) window.ifitwala_ed = {};

frappe.send_message = function(opts, btn) {
	return frappe.call({
		type: "POST",
		method: "ifitwala_ed.templates.utils.send_message",
		btn: btn,
		args: opts,
		callback: opts.callback
	});
};

ifitwala_ed.subscribe_to_newsletter = function(opts, btn) {
	return frappe.call({
		type: "POST",
		method: "frappe.email.doctype.newsletter.newsletter.subscribe",
		btn: btn,
		args: {"email": opts.email},
		callback: opts.callback
	});
}
