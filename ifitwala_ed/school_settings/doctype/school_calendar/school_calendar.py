# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SchoolCalendar(Document):

	def validate(self):
		if not self.terms:
			self.extend("terms", self.get_terms())

	def get_terms(self):
		return frappe.db.sql("""select name from `tabAcademic Term` where academic_year = %s""", (self.academic_year), as_dict=1)
