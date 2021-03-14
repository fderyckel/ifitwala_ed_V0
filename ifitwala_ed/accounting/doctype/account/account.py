# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, cstr
from frappe.utils.nestedset import NestedSet

class RootNotEditable(frappe.ValidationError): pass

class Account(NestedSet):
	nsm_parent_field = 'parent_account'

	def autoname(self):
		from ifitwala_ed.accounting.utils import get_autoname_with_number
		self.name = get_autoname_with_number(self.account_number, self.account_name, None, self.school)

	def  validate(self):
		from ifitwala_ed.accounting.utils import validate_field_number
		self.validate_parent()
		self.validate_root_details()
		validate_field_number("Account", self.name, self.account_number, self.school, "account_number")

	def on_update(self):
		if frappe.local.flags.ignore_on_update:
			return
		else:
			super(Account, self).on_update()

	def validate_parent(self):
		"""Fetch Parent Details and validate parent account"""
		if self.parent_account:
			par = frappe.db.get_value("Account", self.parent_account, ["name", "is_group", "school"], as_dict=1)
			if not par:
				frappe.throw(_("Account {0}: Parent account {1} does not exist").format(self.name, self.parent_account))
			elif par.name == self.name:
				frappe.throw(_("Account {0}: You can not assign itself as parent account").format(self.name))
			elif not par.is_group:
				frappe.throw(_("Account {0}: Parent account {1} can not be a ledger").format(self.name, self.parent_account))
			elif par.company != self.company:
				frappe.throw(_("Account {0}: Parent account {1} does not belong to school: {2}").format(self.name, self.parent_account, self.school))

	def validate_root_details(self):
		if frappe.db.exists("Account", self.name):
			if not frappe.db.get_value("Account", self.name, "parent_account"):
				frappe.throw(_("Root cannot be edited."), RootNotEditable)

		if not self.parent_account and not self.is_group:
			frappe.throw(_("The root account {0} must be a group").format(frappe.bold(self.name)))
