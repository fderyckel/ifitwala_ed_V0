# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

__version__ = '0.0.1'

def encode_organization_abbr(name, organization):
	'''Returns name encoded with organization abbreviation'''
	organization_abbr = frappe.get_cached_value('Organization',  organization,  "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != organization_abbr.lower():
		parts.append(organization_abbr)

	return " - ".join(parts)

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
