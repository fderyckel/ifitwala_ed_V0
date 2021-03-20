# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def get_location_account(location, location_account=None):
	account = location.account
	if not account and location.parent_location:
		if location_account:
			if location_account.get(location.parent_location):
				account = location_account.get(location.parent_location).account
			else:
				from frappe.utils.nestedset import rebuild_tree
				rebuild_tree("Location", "parent_location")
		else:
			account = frappe.db.sql("""
				SELECT
					account FROM `tabLocation`
				WHERE
					lft <= %s AND rgt >= %s AND organization = %s
					AND account is not null AND ifnull(account, '') !=''
				ORDER BY lft DESC limit 1""", (location.lft, location.rgt, location.organization), as_list=1)

			account = account[0][0] if account else None

	if not account and location.organization:
		account = get_organization_default_inventory_account(location.organization)

	if not account and location.organization:
		account = frappe.db.get_value('Account', {'account_type': 'Stock', 'is_group': 0, "organization": location.organization}, 'name')

	if not account and location.organization and not location.is_group:
		frappe.throw(_("Please set Account in Location {0} or Default Inventory Account in Organization {1}").format(location.name, location.organization))

	return account

def get_organization_default_inventory_account(organization):
	return frappe.get_cached_value('Organization', organization, 'default_inventory_account')
