# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from collections import defaultdict

import frappe
from frappe import _, throw
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.utils import cint, flt
from frappe.utils.nestedset import NestedSet

import ifitwala_ed
from ifitwala_ed.stock import get_location_account

class Location(NestedSet):
	nsm_parent_field = 'parent_location'

	def autoname(self):
		if self.organization:
			suffix = " - " + frappe.get_cached_value('Organization',  self.organization,  "abbr")
			if not self.location_name.endswith(suffix):
				self.name = self.location_name + suffix
		else:
			self.name = self.location_name

	def onload(self):
		'''load account name for General Ledger Report'''
		if self.organization and cint(frappe.db.get_value("Organization", self.organization, "enable_perpetual_inventory")):
			account = self.account or get_location_account(self)

			if account:
				self.set_onload('account', account)
		load_address_and_contact(self)

	def on_update(self):
		self.update_nsm_model()

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)
