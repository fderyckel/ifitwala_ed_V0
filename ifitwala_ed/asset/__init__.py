# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def get_storage_account(storage, storage_account=None):
	account = storage.account
	if not account and storage.parent_storage:
		if storage_account:
			if storage_account.get(storage.parent_storage):
				account = storage_account.get(storage.parent_storage).account
			else:
				from frappe.utils.nestedset import rebuild_tree
				rebuild_tree("Storage", "parent_storage")
		else:
			account = frappe.db.sql("""
				SELECT
					account from `tabStorage`
				WHERE
					lft <= %s and rgt >= %s and school = %s
					and account is not null and ifnull(account, '') !=''
				ORDER BY lft DESC limit 1""", (storage.lft, storage.rgt, storage.school), as_list=1)

			account = account[0][0] if account else None

	if not account and storage.school:
		account = get_school_default_inventory_account(storage.school)

	if not account and storage.school:
		account = frappe.db.get_value('Account', {'account_type': 'Stock', 'is_group': 0, "school": storage.school}, 'name')

	if not account and storage.school and not storage.is_group:
		frappe.throw(_("Please set Account in Storage {0} or Default Inventory Account in School {1}").format(storage.name, storage.school))

	return account

def get_school_default_inventory_account(school):
	return frappe.get_cached_value('School', school, 'default_inventory_account')
