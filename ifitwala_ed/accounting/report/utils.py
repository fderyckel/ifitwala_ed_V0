from __future__ import unicode_literals

import frappe
from frappe.utils import flt, formatdate, get_datetime_str

from erpnext import get_company_currency, get_default_company
from erpnext.accounts.doctype.fiscal_year.fiscal_year import get_from_and_to_date
from erpnext.setup.utils import get_exchange_rate

__exchange_rates = {}
