# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SchoolCalendar(Document):

	    def __setup__(self):
			self.onload()

		def onload(self):
			self.load_terms()

		def load_terms(self):
			self.terms = []
			terms = frappe.get_all("Academic Term",
						fields=["name as term", "term_start_date as start", "term_end_date as end"],
						filters = {'academic_year':self.academic_year})
			for term in terms:
				self.append("terms", {
					"term": term.term, "start": term.start, "end": term.end 
					})


		def validate(self):
			self.terms = []
