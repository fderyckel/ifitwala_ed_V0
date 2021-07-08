# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt


from __future__ import unicode_literals

import frappe
import copy
from frappe import _
from frappe.utils import cint, flt, cstr, now, get_link_to_form
from frappe.model.meta import get_field_precision
import json
from six import iteritems

# future reposting
class NegativeStockError(frappe.ValidationError): pass
class SerialNoExistsInFutureTransaction(frappe.ValidationError): pass
