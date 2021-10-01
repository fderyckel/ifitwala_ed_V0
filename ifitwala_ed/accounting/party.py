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
