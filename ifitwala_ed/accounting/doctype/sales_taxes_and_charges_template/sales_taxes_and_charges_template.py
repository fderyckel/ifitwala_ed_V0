# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from ifitwala_ed.controllers.accounts_controller import (validate_account_head, validate_cost_center, validate_inclusive_tax, validate_taxes_and_charges)

class SalesTaxesandChargesTemplate(Document):
	def validate(self):
		validate_taxes_and_charges_template(self)

	def autoname(self):
		if self.organization and self.title:
			abbr = frappe.get_cached_value('Organization',  self.organization,  'abbr')
			self.name = '{0} - {1}'.format(self.title, abbr)

	def set_missing_values(self):
		for data in self.taxes:
			if data.charge_type == 'On Net Total' and flt(data.rate) == 0.0:
				data.rate = frappe.db.get_value('Account', data.account_head, 'tax_rate')

def validate_taxes_and_charges_template(doc):
	if doc.is_default == 1:
		frappe.db.sql("""UPDATE `tab{0}` SET is_default = 0 WHERE is_default = 1 AND name != %s AND organization = %s""".format(doc.doctype), (doc.name, doc.organization))

	validate_disabled(doc)

	# Validate with existing taxes and charges template for unique tax category
	validate_for_tax_category(doc)

	for tax in doc.get("taxes"):
		validate_taxes_and_charges(tax)
		validate_account_head(tax, doc)
		validate_cost_center(tax, doc)
		validate_inclusive_tax(tax, doc)

def validate_disabled(doc):
	if doc.is_default and doc.disabled:
		frappe.throw(_("Disabled template must not be default template"))

def validate_for_tax_category(doc):
	if frappe.db.exists(doc.doctype, {"organization": doc.organization, "tax_category": doc.tax_category, "disabled": 0, "name": ["!=", doc.name]}):
		frappe.throw(_("A template with tax category {0} already exists. Only one template is allowed with each tax category").format(frappe.bold(doc.tax_category)))
