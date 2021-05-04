# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ifitwala_ed.accounting.doctype.sales_taxes_and_charges_template.sales_taxes_and_charges_template import validate_taxes_and_charges_template

class PurchaseTaxesandChargesTemplate(Document):
	def validate(self):
		validate_taxes_and_charges_template(self)

	def autoname(self):
		if self.organization and self.title:
			abbr = frappe.get_cached_value('Organization',  self.organization,  'abbr')
			self.name = '{0} - {1}'.format(self.title, abbr)
