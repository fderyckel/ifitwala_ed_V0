# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import re
from past.builtins import cmp
import functools
import math

import frappe, ifitwala_ed

from frappe import _
from frappe.utils import (flt, getdate, get_first_day, add_months, add_days, formatdate, cstr, cint)

from six import itervalues





def sort_accounts(accounts, is_root=False, key="name"):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_accounts(a, b):
		if re.split('\W+', a[key])[0].isdigit():
			# if chart of accounts is numbered, then sort by number
			return cmp(a[key], b[key])
		elif is_root:
			if a.report_type != b.report_type and a.report_type == "Balance Sheet":
				return -1
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liability" and b.root_type == "Equity":
				return -1
			if a.root_type == "Income" and b.root_type == "Expense":
				return -1
		else:
			# sort by key (number) or name
			return cmp(a[key], b[key])
		return 1

	accounts.sort(key = functools.cmp_to_key(compare_accounts))
