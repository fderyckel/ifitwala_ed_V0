# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe.defaults
from frappe.utils import flt, nowdate

class Bin(Document):
	def before_save(self):
		if self.get("__islocal") or not self.stock_uom:
			self.stock_uom = frappe.get_cached_value('Item', self.item_code, 'stock_uom')
		self.set_projected_qty()

	def get_first_sle(self):
		sle = frappe.db.sql("""SELECT * from `tabStock Ledger Entry` WHERE item_code = %s
				AND location = %s ORDER BY timestamp(posting_date, posting_time) asc, creation asc LIMIT 1""", (self.item_code, self.location), as_dict=1)
		return sle and sle[0] or None

	def set_projected_qty(self):
		self.projected_qty = (flt(self.actual_qty) + flt(self.ordered_qty) + flt(self.requested_qty)
				+ flt(self.planned_qty) - flt(self.reserved_qty))
