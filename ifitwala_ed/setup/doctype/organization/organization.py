# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, json
from frappe import _
from frappe.utils import get_timestamp

from frappe.utils import cint, today, formatdate
import frappe.defaults
from frappe.cache_manager import clear_defaults_cache
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.utils.nestedset import NestedSet

from past.builtins import cmp
import functools
from ifitwala_ed.accounting.doctype.account.account import get_account_currency

class Organization(NestedSet):
	nsm_parent_field = 'parent_organization'

	def onload(self):
		load_address_and_contact(self, "organization")
		self.get("__onload")["transactions_exist"] = self.check_if_transactions_exist()

	def check_if_transactions_exist(self):
		exists = False
		for doctype in ["Lending Note"]:
				if frappe.db.sql("""SELECT name FROM `tab%s` WHERE organization=%s AND docstatus=1 LIMIT 1""" % (doctype, "%s"), self.name):
						exists = True
						break
		return exists

	def validate(self):
		self.update_default_account = False
		if self.is_new():
			self.update_default_account = True

		self.validate_abbr()
		self.validate_default_accounts()
		self.validate_currency()
		self.validate_coa_input()
		self.validate_perpetual_inventory()
		self.validate_perpetual_inventory_for_non_stock_items()
		self.check_country_change()
		self.set_chart_of_accounts()
		self.validate_parent_organization()

	def on_update(self):
		NestedSet.on_update(self)
		if not frappe.db.sql("""SELECT name FROM tabAccount WHERE organization=%s AND docstatus<2 LIMIT 1""", self.name):
			if not frappe.local.flags.ignore_chart_of_accounts:
				frappe.flags.country_change = True
				self.create_default_accounts()
				self.create_default_locations()

		if frappe.flags.country_change:
			self.create_default_tax_template()

		if not frappe.db.get_value("Cost Center", {"is_group": 0, "organization": self.name}):
			self.create_default_cost_center()

		if not frappe.local.flags.ignore_chart_of_accounts:
			self.set_default_accounts()
			if self.default_cash_account:
				self.set_mode_of_payment_account()

		if self.default_currency:
			frappe.db.set_value("Currency", self.default_currency, "enabled", 1)

		if hasattr(frappe.local, 'enable_perpetual_inventory') and self.name in frappe.local.enable_perpetual_inventory:
			frappe.local.enable_perpetual_inventory[self.name] = self.enable_perpetual_inventory

		frappe.clear_cache()

	def after_rename(self, olddn, newdn, merge=False):
		frappe.db.set(self, "organization_name", newdn)
		frappe.db.sql("""UPDATE `tabDefaultValue` SET defvalue=%s WHERE defkey='Organization' AND defvalue=%s""", (newdn, olddn))
		clear_defaults_cache()

	def on_trash(self):
		NestedSet.validate_if_child_exists(self)
		frappe.utils.nestedset.update_nsm(self)

		rec = frappe.db.sql("""SELECT name FROM `tabGL Entry` WHERE organization = %s""", self.name)
		if not rec:
			for doctype in ["Account", "Cost Center"]:
				frappe.db.sql("""DELETE FROM `tab{0}` WHERE organization = %s""".format(doctype), self.name)

		if not frappe.db.get_value("Stock Ledger Entry", {"organization": self.name}):
			frappe.db.sql("""DELETE FROM `tabLocation` WHERE organization=%s""", self.name)

		frappe.defaults.clear_default("organization", value=self.name)
		for doctype in ["Mode of Payment Account"]:
			frappe.db.sql("""DELETE FROM `tab{0}` WHERE organization = %s""".format(doctype), self.name)

		# clear default accounts, locations from item
		locations = frappe.db.sql_list("""SELECT name FROM tabLocation WHERE organization=%s""", self.name)
		if locations:
			frappe.db.sql("""DELETE FROM `tabItem Reorder` WHERE location IN (%s)""" % ', '.join(['%s']*len(locations)), tuple(locations))

		# reset default organization
		frappe.db.sql("""UPDATE `tabSingles` SET value="" WHERE doctype='Global Defaults' AND field='default_organization' AND value=%s""", self.name)

		frappe.db.sql("delete from tabEmployee where organization=%s", self.name)
		frappe.db.sql("delete from tabDepartment where organization=%s", self.name)


##########################################

	def validate_abbr(self):
		if not self.abbr:
			self.abbr = ''.join([c[0] for c in self.organization_name.split()]).upper()

		self.abbr = self.abbr.strip()

		if not self.abbr.strip():
			frappe.throw(_("Abbreviation is mandatory"))

		if frappe.db.sql("SELECT abbr FROM tabOrganization WHERE name!=%s and abbr=%s", (self.name, self.abbr)):
			frappe.throw(_("Abbreviation already used for another organization"))

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
				for_organization = frappe.db.get_value("Account", self.get(account[1]), "organization")
				if for_organization != self.name:
					frappe.throw(_("Account {0} does not belong to organization: {1}").format(self.get(account[1]), self.name))

				if get_account_currency(self.get(account[1])) != self.default_currency:
					error_message = _("{0} currency must be same as organization's default currency. Please select another account.").format(frappe.bold(account[0]))
					frappe.throw(error_message)

	def validate_currency(self):
		if self.is_new():
			return
		self.previous_default_currency = frappe.get_cached_value('Organization',  self.name,  "default_currency")
		if self.default_currency and self.previous_default_currency and self.default_currency != self.previous_default_currency and self.check_if_transactions_exist():
				frappe.throw(_("Cannot change organization's default currency, because there are existing transactions. Transactions must be cancelled to change the default currency."))

	def validate_coa_input(self):
		if self.create_chart_of_accounts_based_on == "Existing Organization":
			self.chart_of_accounts = None
			if not self.existing_organization:
				frappe.throw(_("Please select Existing Organization for creating Chart of Accounts"))

		else:
			self.existing_organization = None
			self.create_chart_of_accounts_based_on = "Standard Template"
			if not self.chart_of_accounts:
				self.chart_of_accounts = "Standard"

	def validate_perpetual_inventory(self):
		if not self.get("__islocal"):
			if cint(self.enable_perpetual_inventory) == 1 and not self.default_inventory_account:
				frappe.msgprint(_("Set default inventory account for perpetual inventory"), alert=True, indicator='orange')

	def validate_perpetual_inventory_for_non_stock_items(self):
		if not self.get("__islocal"):
			if cint(self.enable_perpetual_inventory_for_non_stock_items) == 1 and not self.service_received_but_not_billed:
				frappe.throw(_("Set default {0} account for perpetual inventory for non stock items").format(frappe.bold('Service Received But Not Billed')))

	def check_country_change(self):
		frappe.flags.country_change = False
		if not self.get('__islocal') and self.country != frappe.get_cached_value('Organization',  self.name,  'country'):
			frappe.flags.country_change = True

	def set_chart_of_accounts(self):
		''' If parent organization is set, chart of accounts will be based on that organization '''
		if self.parent_organization:
			self.create_chart_of_accounts_based_on = "Existing Organization"
			self.existing_organization = self.parent_organization

	def validate_parent_organization(self):
		if self.parent_organization:
			is_group = frappe.get_value('Organization', self.parent_organization, 'is_group')
			if not is_group:
				frappe.throw(_("Parent Organization must be a group organization"))

##############
##############

	def create_default_accounts(self):
		from ifitwala_ed.accounting.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
		frappe.local.flags.ignore_root_organization_validation = True
		create_charts(self.name, self.chart_of_accounts, self.existing_organization)

		frappe.db.set(self, "default_receivable_account", frappe.db.get_value("Account",
			{"organization": self.name, "account_type": "Receivable", "is_group": 0}))
		frappe.db.set(self, "default_payable_account", frappe.db.get_value("Account",
			{"organization": self.name, "account_type": "Payable", "is_group": 0}))

	def create_default_locations(self):
		for loc_detail in [
			{"location_name": _("All Locations"), "is_group": 1},
			{"location_name": "Classroom1", "is_group": 0, "location_type": "Classroom"},
			{"location_name": "Office1", "is_group": 0, "location_type": "Office"}]:

			if not frappe.db.exists("Location", "{0} - {1}".format(loc_detail["location_name"], self.abbr)):
				location = frappe.get_doc({
					"doctype":"Location",
					"location_name": loc_detail["location_name"],
					"is_group": loc_detail["is_group"],
					"organization": self.name,
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
				'organization':self.name,
				'is_group': 1,
				'parent_cost_center':None
			},
			{
				'cost_center_name':_('Main'),
				'organization':self.name,
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
			income_account = frappe.db.get_value("Account", {"account_name": _("Sales"), "organization": self.name, "is_group": 0})
			if not income_account:
				income_account = frappe.db.get_value("Account", {"account_name": _("Sales Account"), "organization": self.name})
			self.db_set("default_income_account", income_account)

		if not self.default_payable_account:
			self.db_set("default_payable_account", self.default_payable_account)

		if not self.default_payroll_payable_account:
			payroll_payable_account = frappe.db.get_value("Account", {"account_name": _("Payroll Payable"), "organization": self.name, "is_group": 0})
			self.db_set("default_payroll_payable_account", payroll_payable_account)

		if not self.write_off_account:
			write_off_acct = frappe.db.get_value("Account", {"account_name": _("Write Off"), "organization": self.name, "is_group": 0})
			self.db_set("write_off_account", write_off_acct)

		if not self.exchange_gain_loss_account:
			exchange_gain_loss_acct = frappe.db.get_value("Account", {"account_name": _("Exchange Gain/Loss"), "organization": self.name, "is_group": 0})
			self.db_set("exchange_gain_loss_account", exchange_gain_loss_acct)

	def _set_default_account(self, fieldname, account_type):
		if self.get(fieldname):
			return
		account = frappe.db.get_value("Account", {"account_type": account_type, "is_group": 0, "organization": self.name})
		if account:
			self.db_set(fieldname, account)

	def set_mode_of_payment_account(self):
		cash = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name')
		if cash and self.default_cash_account and not frappe.db.get_value('Mode of Payment Account', {'organization': self.name, 'parent': cash}):
			mode_of_payment = frappe.get_doc('Mode of Payment', cash)
			mode_of_payment.append('accounts', {
				'organization': self.name,
				'default_account': self.default_cash_account
			})
			mode_of_payment.save(ignore_permissions=True)

	@frappe.whitelist()
	def create_default_tax_template(self):
		from ifitwala_ed.setup.setup_wizard.operations.taxes_setup import create_sales_tax
		create_sales_tax({
			'country': self.country,
			'organization_name': self.name
		})



@frappe.whitelist()
def enqueue_replace_abbr(organization, old, new):
	kwargs = dict(organization=organization, old=old, new=new)
	frappe.enqueue('ifitwala_ed.setup.doctype.organization.organization.replace_abbr', **kwargs)

@frappe.whitelist()
def replace_abbr(organization, old, new):
	new = new.strip()
	if not new:
		frappe.throw(_("Abbr can not be blank or space"))

	frappe.only_for("System Manager")

	frappe.db.set_value("Organization", organization, "abbr", new)

	def _rename_record(doc):
		parts = doc[0].rsplit(" - ", 1)
		if len(parts) == 1 or parts[1].lower() == old.lower():
			frappe.rename_doc(dt, doc[0], parts[0] + " - " + new, force=True)

	def _rename_records(dt):
		# rename is expensive so let's be economical with memory usage
		doc = (d for d in frappe.db.sql("""SELECT name FROM `tab%s` WHERE organization=%s""" % (dt, '%s'), organization))
		for d in doc:
			_rename_record(d)

	for dt in ["Location", "Account", "Cost Center", "Department", "Sales Taxes and Charges Template"]:
		_rename_records(dt)
		frappe.db.commit()


def get_name_with_abbr(name, organization):
	organization_abbr = frappe.get_cached_value('Organization',  organization,  "abbr")
	parts = name.split(" - ")

	if parts[-1].lower() != organization_abbr.lower():
		parts.append(organization_abbr)

	return " - ".join(parts)

@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False):
	if parent == None or parent == "All Organizations":
		parent = ""

	return frappe.db.sql("""
		SELECT name as value, is_group as expandable
		FROM `tab{doctype}` comp
		WHERE ifnull(parent_organization, "")={parent}
		""".format(
			doctype = doctype,
			parent=frappe.db.escape(parent)
		), as_dict=1)

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_organization == 'All Organizations':
		args.parent_organization = None

	frappe.get_doc(args).insert()
