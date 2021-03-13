# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

__version__ = '0.0.1'

def encode_school_abbr(name, school):
	'''Returns name encoded with school abbreviation'''
	school_abbr = frappe.get_cached_value('School',  school,  "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != school_abbr.lower():
		parts.append(school_abbr)

	return " - ".join(parts)
