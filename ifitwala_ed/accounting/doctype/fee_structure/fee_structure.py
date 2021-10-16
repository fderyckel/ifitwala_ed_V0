# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class FeeStructure(Document):
	def validate(self):
		self.calculate_total()

	def calculate_total(self):
		"""to calculate total amount"""
		self.total_amount = 0
		for d in self.components:
			self.total_amount += d.amount
