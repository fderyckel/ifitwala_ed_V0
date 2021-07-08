# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, ifitwala_ed
from frappe.utils import cint, flt, cstr, get_link_to_form, today, getdate
from frappe import _
import frappe.defaults


def create_repost_item_valuation_entry(args):
	args = frappe._dict(args)
	repost_entry = frappe.new_doc("Repost Item Valuation")
	repost_entry.based_on = args.based_on
	if not args.based_on:
		repost_entry.based_on = 'Transaction' if args.voucher_no else "Item and Location"
	repost_entry.voucher_type = args.voucher_type
	repost_entry.voucher_no = args.voucher_no
	repost_entry.item_code = args.item_code
	repost_entry.location = args.location
	repost_entry.posting_date = args.posting_date
	repost_entry.posting_time = args.posting_time
	repost_entry.organization = args.organization
	repost_entry.allow_zero_rate = args.allow_zero_rate
	repost_entry.flags.ignore_links = True
	repost_entry.save()
	repost_entry.submit()


def future_sle_exists(args, sl_entries=None):
	key = (args.voucher_type, args.voucher_no)

	if validate_future_sle_not_exists(args, key, sl_entries):
		return False
	elif get_cached_data(args, key):
		return True

	if not sl_entries:
		sl_entries = get_sle_entries_against_voucher(args)
		if not sl_entries:
			return

	or_conditions = get_conditions_to_validate_future_sle(sl_entries)

	data = frappe.db.sql("""
		SELECT item_code, location, count(name) as total_row
		from `tabStock Ledger Entry`
		where
			({})
			and timestamp(posting_date, posting_time)
				>= timestamp(%(posting_date)s, %(posting_time)s)
			and voucher_no != %(voucher_no)s
			and is_cancelled = 0
		GROUP BY
			item_code, location
		""".format(" or ".join(or_conditions)), args, as_dict=1)

	for d in data:
		frappe.local.future_sle[key][(d.item_code, d.location)] = d.total_row

	return len(data)

def validate_future_sle_not_exists(args, key, sl_entries=None):
	item_key = ''
	if args.get('item_code'):
		item_key = (args.get('item_code'), args.get('location'))

	if not sl_entries and hasattr(frappe.local, 'future_sle'):
		if (not frappe.local.future_sle.get(key) or
			(item_key and item_key not in frappe.local.future_sle.get(key))):
			return True

def get_cached_data(args, key):
	if not hasattr(frappe.local, 'future_sle'):
		frappe.local.future_sle = {}

	if key not in frappe.local.future_sle:
		frappe.local.future_sle[key] = frappe._dict({})

	if args.get('item_code'):
		item_key = (args.get('item_code'), args.get('location'))
		count = frappe.local.future_sle[key].get(item_key)

		return True if (count or count == 0) else False
	else:
		return frappe.local.future_sle[key]

def get_sle_entries_against_voucher(args):
	return frappe.get_all("Stock Ledger Entry",
		filters={"voucher_type": args.voucher_type, "voucher_no": args.voucher_no},
		fields=["item_code", "location"],
		order_by="creation asc")

def get_conditions_to_validate_future_sle(sl_entries):
	location_items_map = {}
	for entry in sl_entries:
		if entry.location not in location_items_map:
			location_items_map[entry.location] = set()

		location_items_map[entry.location].add(entry.item_code)

	or_conditions = []
	for location, items in location_items_map.items():
		or_conditions.append(
			f"""location = {frappe.db.escape(location)}
				and item_code in ({', '.join(frappe.db.escape(item) for item in items)})""")

	return or_conditions

def create_repost_item_valuation_entry(args):
	args = frappe._dict(args)
	repost_entry = frappe.new_doc("Repost Item Valuation")
	repost_entry.based_on = args.based_on
	if not args.based_on:
		repost_entry.based_on = 'Transaction' if args.voucher_no else "Item and Location"
	repost_entry.voucher_type = args.voucher_type
	repost_entry.voucher_no = args.voucher_no
	repost_entry.item_code = args.item_code
	repost_entry.location = args.location
	repost_entry.posting_date = args.posting_date
	repost_entry.posting_time = args.posting_time
	repost_entry.organization = args.organization
	repost_entry.allow_zero_rate = args.allow_zero_rate
	repost_entry.flags.ignore_links = True
	repost_entry.save()
	repost_entry.submit()
