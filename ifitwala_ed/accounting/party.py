# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint, scrub
from frappe.contacts.doctype.address.address import (
	get_address_display,
	get_organization_address,
	get_default_address,
)
from frappe.contacts.doctype.contact.contact import get_contact_details
from frappe.core.doctype.user_permission.user_permission import get_permitted_documents
from frappe.model.utils import get_fetch_values
from frappe.utils import (
	add_days,
	add_months,
	add_years,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_last_day,
	get_timestamp,
	getdate,
	nowdate,
)
from six import iteritems

import ifitwala_ed
from ifitwala_ed import get_organization_currency
from ifitwala_ed.accounting.utils import get_fiscal_year
from ifitwala_ed.exceptions import InvalidAccountCurrency, PartyDisabled, PartyFrozen


class DuplicatePartyAccountError(frappe.ValidationError): pass

@frappe.whitelist()
def get_party_account(party_type, party, organization=None):
	"""Returns the account for the given `party`.
		Will first search in party (Customer / Supplier) record, if not found,
		will search in group (Customer Group / Supplier Group),
		finally will return default."""
	if not organization:
		frappe.throw(_("Please select a Organization"))

	if not party:
		return

	account = frappe.db.get_value("Party Account",
		{"parenttype": party_type, "parent": party, "organization": organization}, "account")

	if not account and party_type in ['Customer', 'Supplier']:
		party_group_doctype = "Customer Group" if party_type=="Customer" else "Supplier Group"
		group = frappe.get_cached_value(party_type, party, scrub(party_group_doctype))
		account = frappe.db.get_value("Party Account",
			{"parenttype": party_group_doctype, "parent": group, "organization": organization}, "account")

	if not account and party_type in ['Customer', 'Supplier']:
		default_account_name = "default_receivable_account" \
			if party_type=="Customer" else "default_payable_account"
		account = frappe.get_cached_value('Organization',  organization,  default_account_name)

	existing_gle_currency = get_party_gle_currency(party_type, party, organization)
	if existing_gle_currency:
		if account:
			account_currency = frappe.db.get_value("Account", account, "account_currency", cache=True)
		if (account and account_currency != existing_gle_currency) or not account:
				account = get_party_gle_account(party_type, party, organization)

	return account

def get_party_account_currency(party_type, party, organization):
	def generator():
		party_account = get_party_account(party_type, party, organization)
		return frappe.db.get_value("Account", party_account, "account_currency", cache=True)

	return frappe.local_cache("party_account_currency", (party_type, party, organization), generator)

def get_party_gle_currency(party_type, party, organization):
	def generator():
		existing_gle_currency = frappe.db.sql("""select account_currency from `tabGL Entry`
			where docstatus=1 and organization=%(organization)s and party_type=%(party_type)s and party=%(party)s
			limit 1""", { "organization": organization, "party_type": party_type, "party": party })

		return existing_gle_currency[0][0] if existing_gle_currency else None

	return frappe.local_cache("party_gle_currency", (party_type, party, organization), generator,
		regenerate_if_none=True)

def get_party_gle_account(party_type, party, organization):
	def generator():
		existing_gle_account = frappe.db.sql("""select account from `tabGL Entry`
			where docstatus=1 and organization=%(organization)s and party_type=%(party_type)s and party=%(party)s
			limit 1""", { "organization": organization, "party_type": party_type, "party": party })

		return existing_gle_account[0][0] if existing_gle_account else None

	return frappe.local_cache("party_gle_account", (party_type, party, organization), generator,
		regenerate_if_none=True)

def validate_party_gle_currency(party_type, party, organization, party_account_currency=None):
	"""Validate party account currency with existing GL Entry's currency"""
	if not party_account_currency:
		party_account_currency = get_party_account_currency(party_type, party, organization)

	existing_gle_currency = get_party_gle_currency(party_type, party, organization)

	if existing_gle_currency and party_account_currency != existing_gle_currency:
		frappe.throw(_("{0} {1} has accounting entries in currency {2} for organization {3}. Please select a receivable or payable account with currency {2}.")
			.format(frappe.bold(party_type), frappe.bold(party), frappe.bold(existing_gle_currency), frappe.bold(organization)), InvalidAccountCurrency)



def validate_party_frozen_disabled(party_type, party_name):

	if frappe.flags.ignore_party_validation:
		return

	if party_type and party_name:
		if party_type in ("Customer", "Supplier"):
			party = frappe.get_cached_value(party_type, party_name, ["is_frozen", "disabled"], as_dict=True)
			if party.disabled:
				frappe.throw(_("{0} {1} is disabled").format(party_type, party_name), PartyDisabled)
			elif party.get("is_frozen"):
				frozen_accounts_modifier = frappe.db.get_single_value( 'Accounts Settings', 'frozen_accounts_modifier')
				if not frozen_accounts_modifier in frappe.get_roles():
					frappe.throw(_("{0} {1} is frozen").format(party_type, party_name), PartyFrozen)

		elif party_type == "Employee":
			if frappe.db.get_value("Employee", party_name, "status") != "Active":
				frappe.msgprint(_("{0} {1} is not active").format(party_type, party_name), alert=True)
