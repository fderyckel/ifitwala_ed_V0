# -*- coding: utf-8 -*-
# Copyright (c) 2020, flipo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today, formatdate
from frappe.utils.nestedset import NestedSet, get_root_of
from frappe.model.document import Document
import frappe.defaults
from frappe.cache_manager import clear_defaults_cache
from frappe.contacts.address_and_contact import load_address_and_contact

class School(NestedSet):
	nsm_parent_field = 'parent_school'

	def onload(self):
		load_address_and_contact(self, "school")

	def validate(self):
		self.update_default_account = False
		if self.is_new():
			self.update_default_account = True

		self.validate_abbr()
		self.validate_currency()
		self.validate_coa_input()
		self.validate_parent_school()

	def on_update(self):
		NestedSet.on_update(self)
		if not frappe.db.sql("""SELECT name FROM `tabStorage` WHERE school=%s AND docstatus<2 LIMIT 1 """, self.name):
			if not frappe.local.flags.ignore_chart_of_accounts:
				frappe.flags.country_change = True
				self.create_default_accounts()
				self.create_default_storage()
			#self.create_default_storage_account()

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

	def validate_parent_school(self):
		if self.parent_school:
			is_group = frappe.get_value('School', self.parent_school, 'is_group')
			if not is_group:
				frappe.throw(_("Parent School must be a group school."))

	def validate_perpetual_inventory(self):
		if not self.get("__islocal"):
			if cint(self.enable_perpetual_inventory) == 1 and not self.default_inventory_account:
				frappe.msgprint(_("Set default inventory account for perpetual inventory"), alert=True, indicator='orange')

	def create_default_accounts(self):
		from ifitwala_ed.accounting.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
		frappe.local.flags.ignore_root_school_validation = True
		create_charts(self.name, self.chart_of_accounts, self.existing_school)

		frappe.db.set(self, "default_receivable_account", frappe.db.get_value("Account", {"school": self.name, "account_type": "Receivable", "is_group": 0}))
		frappe.db.set(self, "default_payable_account", frappe.db.get_value("Account", {"school": self.name, "account_type": "Payable", "is_group": 0}))

	def create_default_storage(self):
		if not frappe.db.exists("Storage", "{0} - {1}".format(self.name, self.abbr)):
			storage = frappe.get_doc({
				"doctype":"Storage",
				"storage_name": self.name,
				"is_group": 1,
				"school": self.name,
				"parent_warehouse": "{0} - {1}".format(self.parent_school, self.abbr),
				"warehouse_type" : "School"
			})
			storage.flags.ignore_permissions = True
			storage.flags.ignore_mandatory = True
			storage.insert()

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
		select
			name as value,
			is_group as expandable
		from
			`tab{doctype}` comp
		where
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
