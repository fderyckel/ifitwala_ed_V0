# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from collections import defaultdict
import json

import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe import scrub
from frappe.utils import nowdate, getdate, unique
import ifitwala_ed

# searches for active employees
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def employee_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	fields = get_fields("Employee", ["name", "employee_full_name"])

	return frappe.db.sql("""select {fields} from `tabEmployee`
		where status in ('Active', 'Suspended')
			and docstatus < 2
			and ({key} like %(txt)s
				or employee_full_name like %(txt)s)
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, employee_full_name), locate(%(_txt)s, employee_full_name), 99999),
			idx desc,
			name, employee_full_name
		limit %(start)s, %(page_len)s""".format(**{
			'fields': ", ".join(fields),
			'key': searchfield,
			'fcond': get_filters_cond(doctype, filters, conditions),
			'mcond': get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})




def get_fields(doctype, fields=[]):
	meta = frappe.get_meta(doctype)
	fields.extend(meta.get_search_fields())

	if meta.title_field and not meta.title_field.strip() in fields:
		fields.insert(1, meta.title_field.strip())

	return unique(fields)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def tax_account_query(doctype, txt, searchfield, start, page_len, filters):
	organization_currency = ifitwala_ed.get_organization_currency(filters.get('organization'))

	def get_accounts(with_account_type_filter):
		account_type_condition = ''
		if with_account_type_filter:
			account_type_condition = "AND account_type in %(account_types)s"

		accounts = frappe.db.sql("""
			SELECT name, parent_account
			FROM `tabAccount`
			WHERE `tabAccount`.docstatus!=2
				{account_type_condition}
				AND is_group = 0
				AND organization = %(organization)s
				AND account_currency = %(currency)s
				AND `{searchfield}` LIKE %(txt)s
				{mcond}
			ORDER BY idx DESC, name
			LIMIT %(offset)s, %(limit)s
		""".format(
				account_type_condition=account_type_condition,
				searchfield=searchfield,
				mcond=get_match_cond(doctype)
			),
			dict(
				account_types=filters.get("account_type"),
				ifitwala_ed=filters.get("ifitwala_ed"),
				currency=organization_currency,
				txt="%{}%".format(txt),
				offset=start,
				limit=page_len
			)
		)

		return accounts

	tax_accounts = get_accounts(True)

	if not tax_accounts:
		tax_accounts = get_accounts(False)

	return tax_accounts
