# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import ifitwala_ed
import json
from six import text_type

from frappe import _
from frappe.utils import (today, flt, cint, fmt_money, formatdate, getdate, add_days, add_months, get_last_day, nowdate, get_link_to_form)

from ifitwala_ed.accounting.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from ifitwala_ed.accounting.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from ifitwala_ed.utilities.transaction_base import TransactionBase


class AccountMissingError(frappe.ValidationError): pass

force_item_fields = ("item_group", "brand", "stock_uom", "is_fixed_asset", "item_tax_rate",
	"pricing_rules", "weight_per_unit", "weight_uom", "total_weight")

class AccountsController(TransactionBase):
	def __init__(self, *args, **kwargs):
		super(AccountsController, self).__init__(*args, **kwargs)

	def get_print_settings(self):
		print_setting_fields = []
		items_field = self.meta.get_field('items')

		if items_field and items_field.fieldtype == 'Table':
			print_setting_fields += ['compact_item_print', 'print_uom_after_quantity']

		taxes_field = self.meta.get_field('taxes')
		if taxes_field and taxes_field.fieldtype == 'Table':
			print_setting_fields += ['print_taxes_with_zero_amount']

		return print_setting_fields

	@property
	def organization_currency(self):
		if not hasattr(self, "__organization_currency"):
			self.__organization_currency = ifitwala_ed.get_organization_currency(self.organization)

		return self.__organization_currency

	def onload(self):
		self.set_onload("make_payment_via_journal_entry",
			frappe.db.get_single_value('Accounts Settings', 'make_payment_via_journal_entry'))

		if self.is_new():
			relevant_docs = ("Quotation", "Purchase Order", "Sales Order", "Purchase Invoice", "Sales Invoice")
			if self.doctype in relevant_docs:
				self.set_payment_schedule()

	def ensure_supplier_is_not_blocked(self):
		is_supplier_payment = self.doctype == 'Payment Entry' and self.party_type == 'Supplier'
		is_buying_invoice = self.doctype in ['Purchase Invoice', 'Purchase Order']
		supplier = None
		supplier_name = None

		if is_buying_invoice or is_supplier_payment:
			supplier_name = self.supplier if is_buying_invoice else self.party
			supplier = frappe.get_doc('Supplier', supplier_name)

		if supplier and supplier_name and supplier.on_hold:
			if (is_buying_invoice and supplier.hold_type in ['All', 'Invoices']) or \
					(is_supplier_payment and supplier.hold_type in ['All', 'Payments']):
				if not supplier.release_date or getdate(nowdate()) <= supplier.release_date:
					frappe.msgprint(
						_('{0} is blocked so this transaction cannot proceed').format(supplier_name), raise_exception=1)

	def set_payment_schedule(self):
		if self.doctype == 'Sales Invoice' and self.is_pos:
			self.payment_terms_template = ''
			return

		party_account_currency = self.get('party_account_currency')
		if not party_account_currency:
			party_type, party = self.get_party()

			if party_type and party:
				party_account_currency = get_party_account_currency(party_type, party, self.organization)

		posting_date = self.get("bill_date") or self.get("posting_date") or self.get("transaction_date")
		date = self.get("due_date")
		due_date = date or posting_date

		base_grand_total = self.get("base_rounded_total") or self.base_grand_total
		grand_total = self.get("rounded_total") or self.grand_total

		if self.doctype in ("Sales Invoice", "Purchase Invoice"):
			base_grand_total = base_grand_total - flt(self.base_write_off_amount)
			grand_total = grand_total - flt(self.write_off_amount)
			po_or_so, doctype, fieldname = self.get_order_details()
			automatically_fetch_payment_terms = cint(frappe.db.get_single_value('Accounts Settings', 'automatically_fetch_payment_terms'))

		if self.get("total_advance"):
			if party_account_currency == self.organization_currency:
				base_grand_total -= self.get("total_advance")
				grand_total = flt(base_grand_total / self.get("conversion_rate"), self.precision("grand_total"))
			else:
				grand_total -= self.get("total_advance")
				base_grand_total = flt(grand_total * self.get("conversion_rate"), self.precision("base_grand_total"))

		if not self.get("payment_schedule"):
			if self.doctype in ["Sales Invoice", "Purchase Invoice"] and automatically_fetch_payment_terms \
				and self.linked_order_has_payment_terms(po_or_so, fieldname, doctype):
				self.fetch_payment_terms_from_order(po_or_so, doctype)
				if self.get('payment_terms_template'):
					self.ignore_default_payment_terms_template = 1
			elif self.get("payment_terms_template"):
				data = get_payment_terms(self.payment_terms_template, posting_date, grand_total, base_grand_total)
				for item in data:
					self.append("payment_schedule", item)
			elif self.doctype not in ["Purchase Receipt"]:
				data = dict(due_date=due_date, invoice_portion=100, payment_amount=grand_total, base_payment_amount=base_grand_total)
				self.append("payment_schedule", data)

		for d in self.get("payment_schedule"):
			if d.invoice_portion:
				d.payment_amount = flt(grand_total * flt(d.invoice_portion / 100), d.precision('payment_amount'))
				d.base_payment_amount = flt(base_grand_total * flt(d.invoice_portion / 100), d.precision('base_payment_amount'))
				d.outstanding = d.payment_amount
			elif not d.invoice_portion:
				d.base_payment_amount = flt(d.payment_amount * self.get("conversion_rate"), d.precision('base_payment_amount'))







def validate_taxes_and_charges(tax):
	if tax.charge_type in ['Actual', 'On Net Total', 'On Paid Amount'] and tax.row_id:
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
			frappe.throw(_("Charge of type 'Actual' in row {0} cannot be included in Item Rate or Paid Amount").format(tax.idx))
		elif tax.charge_type == "On Previous Row Amount" and not cint(doc.get("taxes")[cint(tax.row_id) - 1].included_in_print_rate):
			# referred row should also be inclusive
			_on_previous_row_error(tax.row_id)
		elif tax.charge_type == "On Previous Row Total" and \
				not all([cint(t.included_in_print_rate) for t in doc.get("taxes")[:cint(tax.row_id) - 1]]):
			# all rows about the referred tax should be inclusive
			_on_previous_row_error("1 - %d" % (tax.row_id,))
		elif tax.get("category") == "Valuation":
			frappe.throw(_("Valuation type charges can not be marked as Inclusive"))

def validate_account_head(tax, doc):
	organization = frappe.get_cached_value("Account", tax.account_head, "organization")
	if organization != doc.organization:
		frappe.throw(_("Row {0}: account {1} does not belong to organization {2}. Please adjust.").format(tax.idx, frappe.bold(doc.organization), title=_("Invalid Account")))

def validate_cost_center(tax, doc):
	if not tax.cost_center:
		return

	organization = frappe.get_cached_value("Cost Center", tax.cost_center, "Organization")

	if organization != doc.organization:
		frappe.throw(_("Row {0}: Cost Center {1} does not belong to Organization {2}. Please adjust.").format(tax.idx, frappe.bold(tax.cost_center), frappe.bold(doc.organization)), title=_("Invalid Cost Center"))
