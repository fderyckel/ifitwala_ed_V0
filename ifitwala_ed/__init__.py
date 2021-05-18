# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import inspect

from frappe.utils import getdate

__version__ = '0.0.1'

def get_default_organization(user=None):
	'''Get default organization for user'''
	from frappe.defaults import get_user_default_as_list

	if not user:
		user = frappe.session.user

	organizations = get_user_default_as_list(user, 'organization')
	if organizations:
		default_organization = organizations[0]
	else:
		default_organization = frappe.db.get_single_value('Global Defaults', 'default_organization')

	return default_organization

def get_default_currency():
	'''Returns the currency of the default organization'''
	organization = get_default_organization()
	if organization:
		return frappe.get_cached_value('Organization',  organization,  'default_currency')

def get_default_cost_center(organization):
	'''Returns the default cost center of the organization'''
	if not organization:
		return None

	if not frappe.flags.organization_cost_center:
		frappe.flags.organization_cost_center = {}
	if not organization in frappe.flags.organization_cost_center:
		frappe.flags.organization_cost_center[organization] = frappe.get_cached_value('Organization',  organization,  'cost_center')
	return frappe.flags.organization_cost_center[organization]

def get_organization_currency(organization):
	'''Returns the default organization currency'''
	if not frappe.flags.organization_currency:
		frappe.flags.organization_currency = {}
	if not organization in frappe.flags.organization_currency:
		frappe.flags.organization_currency[organization] = frappe.db.get_value('Organization',  organization,  'default_currency', cache=True)
	return frappe.flags.organization_currency[organization]

def encode_organization_abbr(name, organization):
	'''Returns name encoded with organization abbreviation'''
	organization_abbr = frappe.get_cached_value('Organization',  organization,  "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != organization_abbr.lower():
		parts.append(organization_abbr)

	return " - ".join(parts)

def is_perpetual_inventory_enabled(organization):
	if not organization:
		organization = "_Test Organization" if frappe.flags.in_test else get_default_organization()

	if not hasattr(frappe.local, 'enable_perpetual_inventory'):
		frappe.local.enable_perpetual_inventory = {}

	if not organization in frappe.local.enable_perpetual_inventory:
		frappe.local.enable_perpetual_inventory[organization] = frappe.get_cached_value('Organization',
			organization,  "enable_perpetual_inventory") or 0

	return frappe.local.enable_perpetual_inventory[organization]
