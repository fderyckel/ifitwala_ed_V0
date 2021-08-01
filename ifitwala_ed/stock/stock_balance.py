# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
import frappe
from frappe.utils import flt, cstr, nowdate, nowtime
from ifitwala_ed.controllers.stock_controller import create_repost_item_valuation_entry


def repost_stock(item_code, location, allow_zero_rate=False, only_actual=False, only_bin=False, allow_negative_stock=False):

	if not only_bin:
		repost_actual_qty(item_code, location, allow_zero_rate, allow_negative_stock)

	if item_code and location and not only_actual:
		qty_dict = {
			"requested_qty": get_requested_qty(item_code, location),
			"ordered_qty": get_ordered_qty(item_code, location)
		}
		if only_bin:
			qty_dict.update({
				"actual_qty": get_balance_qty_from_sle(item_code, location)
			})

		update_bin_qty(item_code, location, qty_dict)

def repost_actual_qty(item_code, location, allow_zero_rate=False, allow_negative_stock=False):
	create_repost_item_valuation_entry({
		"item_code": item_code,
		"location": location,
		"posting_date": "1900-01-01",
		"posting_time": "00:01",
		"allow_negative_stock": allow_negative_stock,
		"allow_zero_rate": allow_zero_rate
	})

def get_requested_qty(item_code, location):
	# skip the whole sum part as not needed yet in organization
	requested_qty = 0
	return requested_qty

def get_ordered_qty(item_code, location):
	# skip the whole sum part as not needed yet in organization
	ordered_qty = 0
	return ordered_qty

def get_balance_qty_from_sle(item_code, location):
	balance_qty = frappe.db.sql("""
		SELECT qty_after_transaction FROM `tabStock Ledger Entry`
		WHERE item_code=%s AND location=%s AND is_cancelled=0
		ORDER BY posting_date DESC, posting_time DESC, creation DESC
		limit 1""", (item_code, location))

	return flt(balance_qty[0][0]) if balance_qty else 0.0

def update_bin_qty(item_code, location, qty_dict=None):
	from ifitwala_ed.stock.utils import get_bin
	bin = get_bin(item_code, location)
	mismatch = False
	for field, value in qty_dict.items():
		if flt(bin.get(field)) != flt(value):
			bin.set(field, flt(value))
			mismatch = True

	if mismatch:
		bin.set_projected_qty()
		bin.db_update()
		bin.clear_cache()
