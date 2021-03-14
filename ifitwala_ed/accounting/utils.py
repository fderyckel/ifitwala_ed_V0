# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.defaults
from frappe.utils import nowdate, cstr, flt, cint, now, getdate
from frappe.utils import formatdate, get_number_format_info

def validate_field_number(doctype_name, docname, number_value, school, field_name):
	''' Validate if the number entered isn't already assigned to some other document. '''
	if number_value:
		filters = {field_name: number_value, "name": ["!=", docname]}
		if school:
			filters["school"] = school

		doctype_with_same_number = frappe.db.get_value(doctype_name, filters)

		if doctype_with_same_number:
			frappe.throw(_("{0} Number {1} is already used in {2} {3}").format(doctype_name, number_value, doctype_name.lower(), doctype_with_same_number))

def get_autoname_with_number(number_value, doc_title, name, school):
	''' append title with prefix as number and suffix as company's abbreviation separated by '-' '''
	if name:
		name_split=name.split("-")
		parts = [doc_title.strip(), name_split[len(name_split)-1].strip()]
	else:
		abbr = frappe.get_cached_value('School',  school,  ["abbr"], as_dict=True)
		parts = [doc_title.strip(), abbr.abbr]
	if cstr(number_value).strip():
		parts.insert(0, cstr(number_value).strip())
	return ' - '.join(parts)
