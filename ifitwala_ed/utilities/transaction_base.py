# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.share
from frappe import _
from frappe.utils import cstr, now_datetime, cint, flt, get_time, get_datetime, get_link_to_form, date_diff, nowdate
from ifitwala_ed.controllers.status_updater import StatusUpdater

class UOMMustBeIntegerError(frappe.ValidationError): pass

class TransactionBase(StatusUpdater):
	def validate_posting_time(self):
		# set Edit Posting Date and Time to 1 while data import
		if frappe.flags.in_import and self.posting_date:
			self.set_posting_time = 1

		if not getattr(self, 'set_posting_time', None):
			now = now_datetime()
			self.posting_date = now.strftime('%Y-%m-%d')
			self.posting_time = now.strftime('%H:%M:%S.%f')
		elif self.posting_time:
			try:
				get_time(self.posting_time)
			except ValueError:
				frappe.throw(_('Invalid Posting Time'))

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
