# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, cstr
from frappe.utils.nestedset import NestedSet, get_ancestors_of, get_descendants_of

class RootNotEditable(frappe.ValidationError): pass
class BalanceMismatchError(frappe.ValidationError): pass

class Account(NestedSet):
	nsm_parent_field = 'parent_account'
	def on_update(self):
		if frappe.local.flags.ignore_update_nsm:
			return
		else:
			super(Account, self).on_update()

	def autoname(self):
		from ifitwala_ed.accounting.utils import get_autoname_with_number
		self.name = get_autoname_with_number(self.account_number, self.account_name, None, self.organization)

	def validate(self):
		from ifitwala_ed.accounting.utils import validate_field_number
		if frappe.local.flags.allow_unverified_charts:
			return
		self.validate_parent()
		self.validate_root_details()
		validate_field_number("Account", self.name, self.account_number, self.organization, "account_number")
		self.validate_group_or_ledger()
		self.set_root_and_report_type()
		self.validate_mandatory()
		self.validate_balance_must_be_debit_or_credit()
		self.validate_account_currency()
		self.validate_root_organization_and_sync_account_to_children()

	def on_update(self):
		if frappe.local.flags.ignore_on_update:
			return
		else:
			super(Account, self).on_update()

	def on_trash(self):
		# checks gl entries and if child exists
		if self.check_gle_exists():
			frappe.throw(_("Account with existing transaction can not be deleted"))
		super(Account, self).on_trash(True)

	def validate_parent(self):
		"""Fetch Parent Details and validate parent account"""
		if self.parent_account:
			par = frappe.db.get_value("Account", self.parent_account, ["name", "is_group", "organization"], as_dict=1)
			if not par:
				frappe.throw(_("Account {0}: Parent account {1} does not exist").format(self.name, self.parent_account))
			elif par.name == self.name:
				frappe.throw(_("Account {0}: You can not assign itself as parent account").format(self.name))
			elif not par.is_group:
				frappe.throw(_("Account {0}: Parent account {1} can not be a ledger").format(self.name, self.parent_account))
			elif par.organization != self.organization:
				frappe.throw(_("Account {0}: Parent account {1} does not belong to organization: {2}").format(self.name, self.parent_account, self.organization))

	def validate_root_details(self):
		if frappe.db.exists("Account", self.name):
			if not frappe.db.get_value("Account", self.name, "parent_account"):
				frappe.throw(_("Root cannot be edited."), RootNotEditable)

		if not self.parent_account and not self.is_group:
			frappe.throw(_("The root account {0} must be a group").format(frappe.bold(self.name)))

	def set_root_and_report_type(self):
		if self.parent_account:
			par = frappe.db.get_value("Account", self.parent_account, ["report_type", "root_type"], as_dict=1)
			if par.report_type:
				self.report_type = par.report_type
			if par.root_type:
				self.root_type = par.root_type

		if self.is_group:
			db_value = frappe.db.get_value("Account", self.name, ["report_type", "root_type"], as_dict=1)
			if db_value:
				if self.report_type != db_value.report_type:
					frappe.db.sql("update `tabAccount` set report_type=%s where lft > %s and rgt < %s",(self.report_type, self.lft, self.rgt))
				if self.root_type != db_value.root_type:
					frappe.db.sql("update `tabAccount` set root_type=%s where lft > %s and rgt < %s",(self.root_type, self.lft, self.rgt))

		if self.root_type and not self.report_type:
			self.report_type = "Balance Sheet" if self.root_type in ("Asset", "Liability", "Equity") else "Profit and Loss"

	def validate_group_or_ledger(self):
		if self.get("__islocal"):
			return
		existing_is_group = frappe.db.get_value("Account", self.name, "is_group")
		if cint(self.is_group) != cint(existing_is_group):
			if self.check_gle_exists():
				throw(_("Account with existing transaction cannot be converted to ledger"))
			elif self.is_group:
				if self.account_type and not self.flags.exclude_account_type_check:
					throw(_("Cannot covert to Group because Account Type is selected."))
			elif self.check_if_child_exists():
				throw(_("Account with child nodes cannot be set as ledger"))

	def validate_mandatory(self):
		if not self.root_type:
			frappe.throw(_("Root Type is mandatory"))
		if not self.report_type:
			frappe.throw(_("Report Type is mandatory"))

	def validate_balance_must_be_debit_or_credit(self):
		from ifitwala_ed.accounting.utils import get_balance_on
		if not self.get("__islocal") and self.balance_must_be:
			account_balance = get_balance_on(self.name)
			if account_balance > 0 and self.balance_must_be == "Credit":
				frappe.throw(_("Account balance already in Debit, you are not allowed to set 'Balance Must Be' as 'Credit'"))
			elif account_balance < 0 and self.balance_must_be == "Debit":
				frappe.throw(_("Account balance already in Credit, you are not allowed to set 'Balance Must Be' as 'Debit'"))

	def validate_account_currency(self):
		if not self.account_currency:
			self.account_currency = frappe.get_cached_value('Organization', self.organization, "default_currency")
		elif self.account_currency != frappe.db.get_value("Account", self.name, "account_currency"):
			if frappe.db.get_value("GL Entry", {"account": self.name}):
				frappe.throw(_("Currency can not be changed after making entries using some other currency"))

	def validate_root_organization_and_sync_account_to_children(self):
		# ignore validation while creating new organization or while syncing to child organizations
		if frappe.local.flags.ignore_root_organization_validation or self.flags.ignore_root_organization_validation:
			return
		ancestors = get_root_organization(self.organization)
		if ancestors:
			if frappe.get_value("Organization", self.organization, "allow_account_creation_against_child_organization"):
				return
			if not frappe.db.get_value("Account",
				{'account_name': self.account_name, 'organization': ancestors[0]}, 'name'):
				frappe.throw(_("Please add the account to root level Organization - {}").format(ancestors[0]))
		elif self.parent_account:
			descendants = get_descendants_of('Organization', self.organization)
			if not descendants: return
			parent_acc_name_map = {}
			parent_acc_name, parent_acc_number = frappe.db.get_value('Account', self.parent_account, ["account_name", "account_number"])
			filters = {"organization": ["in", descendants],"account_name": parent_acc_name,}
			if parent_acc_number:
				filters["account_number"] = parent_acc_number

			for d in frappe.db.get_values('Account', filters=filters, fieldname=["organization", "name"], as_dict=True):
				parent_acc_name_map[d["organization"]] = d["name"]

			if not parent_acc_name_map: return

			self.create_account_for_child_organization(parent_acc_name_map, descendants, parent_acc_name)

	def create_account_for_child_organization(self, parent_acc_name_map, descendants, parent_acc_name):
		for organization in descendants:
			organization_bold = frappe.bold(organization)
			parent_acc_name_bold = frappe.bold(parent_acc_name)
			if not parent_acc_name_map.get(organization):
				frappe.throw(_("While creating account for Child Organization {0}, parent account {1} not found. Please create the parent account in corresponding COA")
					.format(organization_bold, parent_acc_name_bold), title=_("Account Not Found"))

			# validate if parent of child organization account to be added is a group
			if (frappe.db.get_value("Account", self.parent_account, "is_group")
				and not frappe.db.get_value("Account", parent_acc_name_map[organization], "is_group")):
				msg = _("While creating account for Child Organization {0}, parent account {1} found as a ledger account.").format(organization_bold, parent_acc_name_bold)
				msg += "<br><br>"
				msg += _("Please convert the parent account in corresponding child organization to a group account.")
				frappe.throw(msg, title=_("Invalid Parent Account"))

			filters = {
				"account_name": self.account_name,
				"organization": organization
			}

			if self.account_number:
				filters["account_number"] = self.account_number

			child_account = frappe.db.get_value("Account", filters, 'name')
			if not child_account:
				doc = frappe.copy_doc(self)
				doc.flags.ignore_root_organization_validation = True
				doc.update({
					"organization": organization,
					# parent account's currency should be passed down to child account's curreny
					# if it is None, it picks it up from default organization currency, which might be unintended
					"account_currency": self.account_currency,
					"parent_account": parent_acc_name_map[organization]
				})

				doc.save()
				frappe.msgprint(_("Account {0} is added in the child organization {1}").format(doc.name, organization))
			elif child_account:
				# update the parent organization's value in child organizations
				doc = frappe.get_doc("Account", child_account)
				parent_value_changed = False
				for field in ['account_type', 'account_currency', 'freeze_account', 'balance_must_be']:
					if doc.get(field) != self.get(field):
						parent_value_changed = True
						doc.set(field, self.get(field))

				if parent_value_changed:
					doc.save()

	# Check if any previous balance exists
	def check_gle_exists(self):
		return frappe.db.get_value("GL Entry", {"account": self.name})

	def check_if_child_exists(self):
		return frappe.db.sql("""SELECT name FROM `tabAccount` WHERE parent_account = %s AND docstatus != 2""", self.name)



@frappe.whitelist()
def get_root_organization(organization):
	# return the topmost organization in the hierarchy
	ancestors = get_ancestors_of('Organization', organization, "lft asc")
	return [ancestors[0]] if ancestors else []


def get_account_currency(account):
	"""Helper function to get account currency"""
	if not account:
		return
	def generator():
		account_currency, organization = frappe.get_cached_value("Account", account, ["account_currency", "organization"])
		if not account_currency:
			account_currency = frappe.get_cached_value('Organization', organization, "default_currency")

		return account_currency

	return frappe.local_cache("account_currency", account, generator)

def on_doctype_update():
	frappe.db.add_index("Account", ["lft", "rgt"])
