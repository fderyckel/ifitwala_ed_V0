# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

install_docs = [
	{"doctype":"Role", "role_name":"Stock Manager", "name":"Stock Manager"},
	{"doctype":"Role", "role_name":"Item Manager", "name":"Item Manager"},
	{"doctype":"Role", "role_name":"Stock User", "name":"Stock User"},
	{"doctype":"Role", "role_name":"Quality Manager", "name":"Quality Manager"},
	{"doctype":"Item Group", "item_group_name":"All Item Groups", "is_group": 1},
	{"doctype":"Item Group", "item_group_name":"Default",
		"parent_item_group":"All Item Groups", "is_group": 0},
]

def get_location_account_map(organization=None):
	organization_location_account_map = organization and frappe.flags.setdefault('location_account_map', {}).get(organization)
	location_account_map = frappe.flags.location_account_map

	if not location_account_map or not organization_location_account_map or frappe.flags.in_test:
		location_account = frappe._dict()

		filters = {}
		if organization:
			filters['organization'] = organization
			frappe.flags.setdefault('location_account_map', {}).setdefault(organization, {})

		for d in frappe.get_all('Location',
			fields = ["name", "account", "parent_location", "organization", "is_group"],
			filters = filters,
			order_by="lft, rgt"):
			if not d.account:
				d.account = get_location_account(d, location_account)

			if d.account:
				d.account_currency = frappe.db.get_value('Account', d.account, 'account_currency', cache=True)
				location_account.setdefault(d.name, d)
		if organization:
			frappe.flags.location_account_map[organization] = location_account
		else:
			frappe.flags.location_account_map = location_account

	return frappe.flags.location_account_map.get(organization) or frappe.flags.location_account_map

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
