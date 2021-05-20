# -*- coding: utf-8 -*-
# Copyright (c) 2020, flipo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, json
from frappe import _
from frappe.utils import cint, today, formatdate, get_timestamp
from frappe.utils.nestedset import NestedSet, get_root_of
from frappe.model.document import Document
import frappe.defaults
from frappe.cache_manager import clear_defaults_cache
from frappe.contacts.address_and_contact import load_address_and_contact

from past.builtins import cmp
import functools

from ifitwala_ed.accounting.doctype.account.account import get_account_currency

class School(NestedSet):
	nsm_parent_field = 'parent_school'

	def onload(self):
		load_address_and_contact(self, "school")

	def validate(self):
		self.validate_abbr()
		self.validate_parent_school()

	def on_update(self):
		NestedSet.on_update(self)
		#if not frappe.db.sql("""SELECT name FROM `tabLocation` WHERE school=%s AND docstatus<2 LIMIT 1 """, self.name):
		#	self.create_default_location()
		#if not frappe.db.get_value("Cost Center", {"is_group": 0, "school": self.name}):
		#	self.create_default_cost_center()

	def on_trash(self):
		NestedSet.validate_if_child_exists(self)
		frappe.utils.nestedset.update_nsm(self)

	def after_rename(self, olddn, newdn, merge=False):
		frappe.db.set(self, "school_name", newdn)
		clear_defaults_cache()

	def validate_abbr(self):
		if not self.abbr:
			self.abbr = ''.join([c[0] for c in self.school_name.split()]).upper()

		self.abbr = self.abbr.strip()

		if self.get('__islocal') and len(self.abbr) > 5:
		 	frappe.throw(_("Abbreviation cannot have more than 5 characters"))

		if not self.abbr.strip():
			frappe.throw(_("Abbreviation is mandatory"))

		if frappe.db.sql("""SELECT abbr FROM `tabSchool` WHERE name!=%s AND abbr=%s""", (self.name, self.abbr)):
			frappe.throw(_("Abbreviation {0} is already used for another school.").format(self.abbr))

	def validate_parent_school(self):
		if self.parent_school:
			is_group = frappe.get_value('School', self.parent_school, 'is_group')
			if not is_group:
				frappe.throw(_("Parent School must be a group school."))

	def create_default_location(self):
		for loc_detail in [
			{"location_name": self.name, "is_group": 1},
			{"location_name": _("Classroom 1"), "is_group": 0, "location_type": "Classroom"},
			{"location_name": _("Office 1"), "is_group": 0, "location_type": "Office"}]:
			if not frappe.db.exists("Location", "{0} - {1}".format(loc_detail["location_name"], self.abbr)):
				location = frappe.get_doc({
					"doctype": "Location",
					"location_name": loc_detail["location_name"],
					"is_group": loc_detail["is_group"],
					"organization": self.organization,
					"school": self.name,
					"parent_location": "{0} - {1}".format(_("All Locations"), self.abbr) if not loc_detail["is_group"] else "",
					"location_type" : loc_detail["location_type"] if "location_type" in loc_detail else None
				})
			location.flags.ignore_permissions = True
			location.flags.ignore_mandatory = True
			location.insert()

	def create_default_cost_center(self):
		cc_list = [
			{
				'cost_center_name': self.name,
				'school':self.name,
				'is_group': 1,
				'parent_cost_center':None
			},
			{
				'cost_center_name':_('Main'),
				'school':self.name,
				'is_group':0,
				'parent_cost_center':self.name + ' - ' + self.abbr
			},
		]
		for cc in cc_list:
			cc.update({"doctype": "Cost Center"})
			cc_doc = frappe.get_doc(cc)
			cc_doc.flags.ignore_permissions = True

			if cc.get("cost_center_name") == self.name:
				cc_doc.flags.ignore_mandatory = True
			cc_doc.insert()

		frappe.db.set(self, "default_cost_center", _("Main") + " - " + self.abbr)
		frappe.db.set(self, "round_off_cost_center", _("Main") + " - " + self.abbr)
		frappe.db.set(self, "depreciation_cost_center", _("Main") + " - " + self.abbr)

	def set_default_accounts(self):
		default_accounts = {
			"default_cash_account": "Cash",
			"default_bank_account": "Bank",
			"round_off_account": "Round Off",
			"accumulated_depreciation_account": "Accumulated Depreciation",
			"depreciation_expense_account": "Depreciation",
			"capital_work_in_progress_account": "Capital Work in Progress",
			"asset_received_but_not_billed": "Asset Received But Not Billed",
			"expenses_included_in_asset_valuation": "Expenses Included In Asset Valuation"
		}

		if self.enable_perpetual_inventory:
			default_accounts.update({
				"stock_received_but_not_billed": "Stock Received But Not Billed",
				"default_inventory_account": "Stock",
				"stock_adjustment_account": "Stock Adjustment",
				"expenses_included_in_valuation": "Expenses Included In Valuation",
				"default_expense_account": "Cost of Goods Sold"
			})

		if self.update_default_account:
			for default_account in default_accounts:
				self._set_default_account(default_account, default_accounts.get(default_account))

		if not self.default_income_account:
			income_account = frappe.db.get_value("Account", {"account_name": _("Sales"), "school": self.name, "is_group": 0})
			if not income_account:
				income_account = frappe.db.get_value("Account", {"account_name": _("Sales Account"), "school": self.name})
			self.db_set("default_income_account", income_account)

		if not self.default_payable_account:
			self.db_set("default_payable_account", self.default_payable_account)

		if not self.write_off_account:
			write_off_acct = frappe.db.get_value("Account", {"account_name": _("Write Off"), "school": self.name, "is_group": 0})
			self.db_set("write_off_account", write_off_acct)

		if not self.exchange_gain_loss_account:
			exchange_gain_loss_acct = frappe.db.get_value("Account", {"account_name": _("Exchange Gain/Loss"), "school": self.name, "is_group": 0})
			self.db_set("exchange_gain_loss_account", exchange_gain_loss_acct)

		if not self.disposal_account:
			disposal_acct = frappe.db.get_value("Account", {"account_name": _("Gain/Loss on Asset Disposal"), "school": self.name, "is_group": 0})
			self.db_set("disposal_account", disposal_acct)

	def set_mode_of_payment_account(self):
		cash = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name')
		if cash and self.default_cash_account and not frappe.db.get_value('Mode of Payment Account', {'school': self.name, 'parent': cash}):
			mode_of_payment = frappe.get_doc('Mode of Payment', cash)
			mode_of_payment.append('accounts', {'school': self.name, 'default_account': self.default_cash_account})
			mode_of_payment.save(ignore_permissions=True)

	def _set_default_account(self, fieldname, account_type):
		if self.get(fieldname):
			return
		account = frappe.db.get_value("Account", {"account_type": account_type, "is_group": 0, "school": self.name})
		if account:
			self.db_set(fieldname, account)

@frappe.whitelist()
def enqueue_replace_abbr(school, old, new):
	kwargs = dict(school=school, old=old, new=new)
	frappe.enqueue('ifitwala_ed.school_settings.doctype.school.school.replace_abbr', **kwargs)


@frappe.whitelist()
def replace_abbr(school, old, new):
	new = new.strip()
	if not new:
		frappe.throw(_("Abbr can not be blank or space"))

	frappe.only_for("System Manager")

	frappe.db.set_value("School", school, "abbr", new)

	def _rename_record(doc):
		parts = doc[0].rsplit(" - ", 1)
		if len(parts) == 1 or parts[1].lower() == old.lower():
			frappe.rename_doc(dt, doc[0], parts[0] + " - " + new)

	def _rename_records(dt):
		# rename is expensive so let's be economical with memory usage
		doc = (d for d in frappe.db.sql("select name from `tab%s` where school=%s" % (dt, '%s'), school))
		for d in doc:
			_rename_record(d)

def get_name_with_abbr(name, school):
	school_abbr = frappe.db.get_value("School", school, "abbr")
	parts = name.split(" - ")
	if parts[-1].lower() != school_abbr.lower():
		parts.append(school_abbr)
	return " - ".join(parts)

@frappe.whitelist()
def get_children(doctype, parent=None, school=None, is_root=False):
	if parent is None or parent == "All Schools":
		parent = ""

	return frappe.db.sql("""
		SELECT
			name as value,
			is_group as expandable
		FROM
			`tab{doctype}` comp
		WHERE
			ifnull(parent_school, "")={parent}
		""".format(
			doctype=doctype,
			parent=frappe.db.escape(parent)
		), as_dict=1)


@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_school == 'All Schools':
		args.parent_school = None

	frappe.get_doc(args).insert()
