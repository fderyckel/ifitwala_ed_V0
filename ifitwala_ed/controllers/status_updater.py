# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import comma_or
from frappe.model.document import Document


def validate_status(status, options):
	if status not in options:
		frappe.throw(_("Status must be one of {0}").format(comma_or(options)))
