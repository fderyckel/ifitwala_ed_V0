# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.utils import getdate
from frappe import _
from frappe.model.document import Document


class AcademicYear(Document):
    def validate(self):
        # The start of the year has to be before the end of the academic year. 
        if self.year_start_date and self.year_end_date and getdate(self.year_start_date) > getdate(self.year_end_date): 
            frappe.throw(_("The start of the academic year has to be before the end of the acamic year."))
	
