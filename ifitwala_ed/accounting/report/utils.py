from __future__ import unicode_literals

import frappe
from frappe.utils import flt, formatdate, get_datetime_str

from ifitwala_ed import get_organization_currency, get_default_company
from ifitwala_ed.accounting.doctype.fiscal_year.fiscal_year import get_from_and_to_date
from ifitwala_ed.setup.utils import get_exchange_rate

__exchange_rates = {}
