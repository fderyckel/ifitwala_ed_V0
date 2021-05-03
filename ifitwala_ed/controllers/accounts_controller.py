# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, ifitwala_ed
import json
from frappe import _
from frappe.utils import (today, flt, cint, fmt_money, formatdate, getdate, add_days, add_months, get_last_day, nowdate, get_link_to_form)


class AccountMissingError(frappe.ValidationError): pass



def validate_taxes_and_charges(tax):
	if tax.charge_type in ['Actual', 'On Net Total'] and tax.row_id:
		frappe.throw(_("Can refer row only if the charge type is 'On Previous Row Amount' or 'Previous Row Total'"))
	elif tax.charge_type in ['On Previous Row Amount', 'On Previous Row Total']:
		if cint(tax.idx) == 1:
			frappe.throw(_("Cannot select charge type as 'On Previous Row Amount' or 'On Previous Row Total' for first row"))
		elif not tax.row_id:
			frappe.throw(_("Please specify a valid Row ID for row {0} in table {1}").format(tax.idx, _(tax.doctype)))
		elif tax.row_id and cint(tax.row_id) >= cint(tax.idx):
			frappe.throw(_("Cannot refer row number greater than or equal to current row number for this Charge type"))

	if tax.charge_type == "Actual":
		tax.rate = None

def validate_inclusive_tax(tax, doc):
	def _on_previous_row_error(row_range):
		frappe.throw(_("To include tax in row {0} in Item rate, taxes in rows {1} must also be included").format(tax.idx, row_range))

	if cint(getattr(tax, "included_in_print_rate", None)):
		if tax.charge_type == "Actual":
			# inclusive tax cannot be of type Actual
			frappe.throw(_("Charge of type 'Actual' in row {0} cannot be included in Item Rate").format(tax.idx))
		elif tax.charge_type == "On Previous Row Amount" and not cint(doc.get("taxes")[cint(tax.row_id) - 1].included_in_print_rate):
			# referred row should also be inclusive
			_on_previous_row_error(tax.row_id)
		elif tax.charge_type == "On Previous Row Total" and \
				not all([cint(t.included_in_print_rate) for t in doc.get("taxes")[:cint(tax.row_id) - 1]]):
			# all rows about the reffered tax should be inclusive
			_on_previous_row_error("1 - %d" % (tax.row_id,))
		elif tax.get("category") == "Valuation":
			frappe.throw(_("Valuation type charges can not be marked as Inclusive"))
