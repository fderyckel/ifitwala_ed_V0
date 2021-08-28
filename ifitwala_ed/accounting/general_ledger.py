# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt, cstr, cint, comma_and, today, getdate, formatdate, now
from frappe import _
from frappe.model.meta import get_field_precision
#from ifitwala_ed.accounting.doctype.budget.budget import validate_expense_against_budget
from ifitwala_ed.accounting.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions

class ClosedAccountingPeriod(frappe.ValidationError): pass

def make_gl_entries(gl_map, cancel=False, adv_adj=False, merge_entries=True, update_outstanding='Yes', from_repost=False):
	if gl_map:
		if not cancel:
			validate_accounting_period(gl_map)
			gl_map = process_gl_map(gl_map, merge_entries)
			if gl_map and len(gl_map) > 1:
				save_entries(gl_map, adv_adj, update_outstanding, from_repost)
			# Post GL Map proccess there may no be any GL Entries
			elif gl_map:
				frappe.throw(_("Incorrect number of General Ledger Entries found. You might have selected a wrong Account in the transaction."))
		else:
			make_reverse_gl_entries(gl_map, adv_adj=adv_adj, update_outstanding=update_outstanding)

def validate_accounting_period(gl_map):
	accounting_periods = frappe.db.sql(""" SELECT
			ap.name as name
		FROM
			`tabAccounting Period` ap, `tabClosed Document` cd
		WHERE
			ap.name = cd.parent
			AND ap.company = %(company)s
			AND cd.closed = 1
			AND cd.document_type = %(voucher_type)s
			AND %(date)s between ap.start_date and ap.end_date
			""", {
				'date': gl_map[0].posting_date,
				'company': gl_map[0].company,
				'voucher_type': gl_map[0].voucher_type
			}, as_dict=1)

	if accounting_periods:
		frappe.throw(_("You cannot create or cancel any accounting entries with in the closed Accounting Period {0}")
			.format(frappe.bold(accounting_periods[0].name)), ClosedAccountingPeriod)
