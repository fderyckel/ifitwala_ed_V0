# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr, nowdate, nowtime, get_link_to_form

def get_stock_value_from_bin(storage=None, item_code=None):
	values = {}
	conditions = ""
	if storage:
		conditions += """ AND `tabBin`.storage in (
						SELECT w2.name FROM `tabstorage` w1
						JOIN `tabstorage` w2 ON
						w1.name = %(storage)s
						AND w2.lft BETWEEN w1.lft AND w1.rgt
						) """

		values['storage'] = storage

	if item_code:
		conditions += " and `tabBin`.item_code = %(item_code)s"

		values['item_code'] = item_code

	query = """select sum(stock_value) from `tabBin`, `tabItem` where 1 = 1
		and `tabItem`.name = `tabBin`.item_code and ifnull(`tabItem`.disabled, 0) = 0 %s""" % conditions

	stock_value = frappe.db.sql(query, values)

	return stock_value

def get_bin(item_code, storage):
	bin = frappe.db.get_value("Bin", {"item_code": item_code, "storage": storage})
	if not bin:
		bin_obj = frappe.get_doc({
			"doctype": "Bin",
			"item_code": item_code,
			"storage": storage,
		})
		bin_obj.flags.ignore_permissions = 1
		bin_obj.insert()
	else:
		bin_obj = frappe.get_cached_doc("Bin", bin)
	bin_obj.flags.ignore_permissions = True
	return bin_obj
