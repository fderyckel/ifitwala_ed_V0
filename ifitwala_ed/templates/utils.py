# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist(allow_guest=True)
def send_message(subject="Website Query", message="", sender="", status="Open"):
	from frappe.www.contact import send_message as website_send_message
	opportunity, guardian = None

	website_send_message(subject, message, sender)

	guardian = frappe.db.sql("""select distinct dl.link_name from `tabDynamic Link` dl
		left join `tabContact` c on dl.parent=c.name where dl.link_doctype='guardian'
		and c.guardian_email = %s""", sender)

	if not guardian:
		opportunity = frappe.db.get_value('Opportunity', dict(email_id=sender))
		if not opportunity:
			new_opportunity = frappe.get_doc(dict(
				doctype='Opportunity',
				email_id = sender,
				status = 'Open',
				notes = message,
				lead_name = sender.split('@')[0].title()
			)).insert(ignore_permissions=True)

	comm = frappe.get_doc({
		"doctype":"Communication",
		"subject": subject,
		"content": message,
		"sender": sender,
		"sent_or_received": "Received",
		'reference_doctype': 'Opportunity',
		'reference_name': opportunity.name
	})
	comm.insert(ignore_permissions=True)

	return "okay"
