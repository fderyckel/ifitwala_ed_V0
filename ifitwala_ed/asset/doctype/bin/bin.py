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

	def update_stock(self, args, allow_negative_stock=False, via_landed_cost_voucher=False):
		'''Called from ifitwala_ed.asset.utils.update_bin'''
		self.update_qty(args)

		if args.get("actual_qty") or args.get("voucher_type") == "Stock Reconciliation":
			from erpnext.stock.stock_ledger import update_entries_after, update_qty_in_future_sle

			if not args.get("posting_date"):
				args["posting_date"] = nowdate()

			if args.get("is_cancelled") and via_landed_cost_voucher:
				return

			# Reposts only current voucher SL Entries
			# Updates valuation rate, stock value, stock queue for current transaction
			update_entries_after({
				"item_code": self.item_code,
				"location": self.location,
				"posting_date": args.get("posting_date"),
				"posting_time": args.get("posting_time"),
				"voucher_type": args.get("voucher_type"),
				"voucher_no": args.get("voucher_no"),
				"sle_id": args.name,
				"creation": args.creation
			}, allow_negative_stock=allow_negative_stock, via_landed_cost_voucher=via_landed_cost_voucher)

			# update qty in future ale and Validate negative qty
			update_qty_in_future_sle(args, allow_negative_stock)


	def update_qty(self, args):
		# update the stock values (for current quantities)
		if args.get("voucher_type")=="Stock Reconciliation":
			self.actual_qty = args.get("qty_after_transaction")
		else:
			self.actual_qty = flt(self.actual_qty) + flt(args.get("actual_qty"))

		self.ordered_qty = flt(self.ordered_qty) + flt(args.get("ordered_qty"))
		self.reserved_qty = flt(self.reserved_qty) + flt(args.get("reserved_qty"))
		self.planned_qty = flt(self.planned_qty) + flt(args.get("planned_qty"))

		self.set_projected_qty()
		self.db_update()

	def set_projected_qty(self):
		self.projected_qty = (flt(self.actual_qty) + flt(self.ordered_qty) + flt(self.planned_qty) - flt(self.reserved_qty))

	def get_first_sle(self):
		sle = frappe.db.sql("""
			select * from `tabStock Ledger Entry`
			where item_code = %s
			and location = %s
			order by timestamp(posting_date, posting_time) asc, creation asc
			limit 1
		""", (self.item_code, self.location), as_dict=1)
		return sle and sle[0] or None

def on_doctype_update():
	frappe.db.add_index("Bin", ["item_code", "location"])
