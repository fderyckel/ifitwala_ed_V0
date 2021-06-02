# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.share
from frappe import _
from frappe.utils import cstr, now_datetime, cint, flt, get_time, get_datetime, get_link_to_form, date_diff, nowdate





def delete_events(ref_type, ref_name):
	events = frappe.db.sql_list(""" SELECT DISTINCT `tabEvent`.name
        FROM `tabEvent`, `tabEvent Participants`
		WHERE
			`tabEvent`.name = `tabEvent Participants`.parent
			and `tabEvent Participants`.reference_doctype = %s
			and `tabEvent Participants`.reference_docname = %s
		""", (ref_type, ref_name)) or []

	if events:
		frappe.delete_doc("Event", events, for_reload=True)
