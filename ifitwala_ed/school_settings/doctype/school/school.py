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
		self.update_default_account = False
		if self.is_new():
			self.update_default_account = True

		self.validate_abbr()
		self.validate_default_accounts()
		self.validate_currency()
		self.validate_coa_input()
		self.validate_perpetual_inventory()
		self.check_country_change()
		self.set_chart_of_accounts()
		self.validate_parent_school()

	def on_update(self):
		NestedSet.on_update(self)
		if not frappe.db.sql("""SELECT name FROM `tabLocation` WHERE school=%s AND docstatus<2 LIMIT 1 """, self.name):
			if not frappe.local.flags.ignore_chart_of_accounts:
				frappe.flags.country_change = True
				self.create_default_accounts()
				self.create_default_location()
			#self.create_default_location_account()
		if not frappe.db.get_value("Cost Center", {"is_group": 0, "school": self.name}):
			self.create_default_cost_center()

		#if not frappe.db.get_value("Department", {"school": self.name}):
		#	from ifitwala_ed.setup.setup_wizard.operations.install_fixtures import install_post_school_fixtures
		#	install_post_school_fixtures(frappe._dict({'school_name': self.name}))

		if not frappe.local.flags.ignore_chart_of_accounts:
			self.set_default_accounts()
			if self.default_cash_account:
				self.set_mode_of_payment_account()

	def on_trash(self):
		NestedSet.validate_if_child_exists(self)
		frappe.utils.nestedset.update_nsm(self)

	def after_rename(self, olddn, newdn, merge=False):
		frappe.db.set(self, "school_name", newdn)
		frappe.db.sql("""UPDATE `tabDefaultValue` SET defvalue=%s WHERE defkey='School' AND defvalue=%s""", (newdn, olddn))
		clear_defaults_cache()

	def abbreviate(self):
		self.abbr = ''.join([c[0].upper() for c in self.school_name.split()])

	def check_if_transactions_exist(self):
		exists = False
		for doctype in ["Lending Note", "Fees"]:
				if frappe.db.sql("""SELECT name FROM `tab%s` WHERE school=%s AND docstatus=1 LIMIT 1""" % (doctype, "%s"), self.name):
						exists = True
						break
		return exists

	def validate_abbr(self):
		if not self.abbr:
			self.abbr = ''.join([c[0] for c in self.school_name.split()]).upper()

		self.abbr = self.abbr.strip()

		if self.get('__islocal') and len(self.abbr) > 5:
		 	frappe.throw(_("Abbreviation cannot have more than 5 characters"))

		if not self.abbr.strip():
			frappe.throw(_("Abbreviation is mandatory"))

		if frappe.db.sql("""SELECT abbr FROM `tabSchool` WHERE name!=%s AND abbr=%s""", (self.name, self.abbr)):
			frappe.throw(_("Abbreviation {0} is already used for another school").format(self.abbr))

	def validate_default_accounts(self):
		accounts = [
			["Default Bank Account", "default_bank_account"], ["Default Cash Account", "default_cash_account"],
			["Default Receivable Account", "default_receivable_account"], ["Default Payable Account", "default_payable_account"],
			["Default Expense Account", "default_expense_account"], ["Default Income Account", "default_income_account"],
			["Stock Received But Not Billed Account", "stock_received_but_not_billed"], ["Stock Adjustment Account", "stock_adjustment_account"],
			["Expense Included In Valuation Account", "expenses_included_in_valuation"], ["Default Payroll Payable Account", "default_payroll_payable_account"]
		]

		for account in accounts:
			if self.get(account[1]):
				for_school = frappe.db.get_value("Account", self.get(account[1]), "school")
				if for_school != self.name:
					frappe.throw(_("Account {0} does not belong to school: {1}").format(self.get(account[1]), self.name))

				if get_account_currency(self.get(account[1])) != self.default_currency:
					error_message = _("{0} currency must be same as school's default currency. Please select another account.").format(frappe.bold(account[0]))
					frappe.throw(error_message)


	def validate_currency(self):
		if self.is_new():
			return
		self.previous_default_currency = frappe.get_cached_value('School',  self.name,  "default_currency")
		if self.default_currency and self.previous_default_currency and self.default_currency != self.previous_default_currency and self.check_if_transactions_exist():
				frappe.throw(_("Cannot change school's default currency, because there are existing transactions. Transactions must be cancelled to change the default currency."))

	def validate_coa_input(self):
		if self.create_chart_of_accounts_based_on == "Existing School":
			self.chart_of_accounts = None
			if not self.existing_school:
				frappe.throw(_("Please select Existing School for creating Chart of Accounts"))
		else:
			self.existing_school = None
			self.create_chart_of_accounts_based_on = "Standard Template"
			if not self.chart_of_accounts:
				self.chart_of_accounts = "Standard"

	def validate_perpetual_inventory(self):
		if not self.get("__islocal"):
			if cint(self.enable_perpetual_inventory) == 1 and not self.default_inventory_account:
				frappe.msgprint(_("Set default inventory account for perpetual inventory"), alert=True, indicator='orange')

	def check_country_change(self):
		frappe.flags.country_change = False
		if not self.get('__islocal') and self.country != frappe.get_cached_value('School',  self.name,  'country'):
			frappe.flags.country_change = True

	def set_chart_of_accounts(self):
		''' If parent school is set, chart of accounts will be based on that school '''
		if self.parent_school:
			self.create_chart_of_accounts_based_on = "Existing School"
			self.existing_school = self.parent_school

	def validate_parent_school(self):
		if self.parent_school:
			is_group = frappe.get_value('School', self.parent_school, 'is_group')
			if not is_group:
				frappe.throw(_("Parent School must be a group school."))

	def create_default_accounts(self):
		from ifitwala_ed.accounting.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
		frappe.local.flags.ignore_root_school_validation = True
		create_charts(self.name, self.chart_of_accounts, self.existing_school)

		frappe.db.set(self, "default_receivable_account", frappe.db.get_value("Account", {"school": self.name, "account_type": "Receivable", "is_group": 0}))
		frappe.db.set(self, "default_payable_account", frappe.db.get_value("Account", {"school": self.name, "account_type": "Payable", "is_group": 0}))

	def create_default_location(self):
		if not frappe.db.exists("Location", "{0} - {1}".format(self.name, self.abbr)):
			location = frappe.get_doc({
				"doctype":"Location",
				"location_name": self.name,
				"is_group": 1,
				"school": self.name,
				"parent_location": "{0} - {1}".format(self.parent_school, self.abbr),
				"location_type" : "School"
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

		frappe.db.set(self, "cost_center", _("Main") + " - " + self.abbr)
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
