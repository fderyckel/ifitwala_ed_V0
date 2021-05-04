# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, getdate

def set_default_settings(args):
	# enable default currency
	frappe.db.set_value("Currency", args.get("currency"), "enabled", 1)

	global_defaults = frappe.get_doc("Global Defaults", "Global Defaults")
	global_defaults.update({
		'current_fiscal_year': get_fy_details(args.get('fy_start_date'), args.get('fy_end_date')),
		'default_currency': args.get('currency'),
		'default_organization':args.get('organization_name')	,
		"country": args.get("country"),
	})

	global_defaults.save()

	system_settings = frappe.get_doc("System Settings")
	system_settings.email_footer_address = args.get("organization_name")
	system_settings.save()


def create_employee_for_self(args):
	if frappe.session.user == 'Administrator':
		return

	# create employee for self
	emp = frappe.get_doc({
		"doctype": "Employee",
		"employee_full_name": " ".join(filter(None, [args.get("first_name"), args.get("last_name")])),
		"user_id": frappe.session.user,
		"status": "Active",
		"organization": args.get("organization_name")
	})
	emp.flags.ignore_mandatory = True
	emp.insert(ignore_permissions = True)

def get_fy_details(fy_start_date, fy_end_date):
	start_year = getdate(fy_start_date).year
	if start_year == getdate(fy_end_date).year:
		fy = cstr(start_year)
	else:
		fy = cstr(start_year) + '-' + cstr(start_year + 1)
	return fy
