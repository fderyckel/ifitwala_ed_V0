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
		ay = frappe.get_value("Academic Year", self.academic_year) 
		terms = frappe.get_all("Academic Term", filters = {"academic_year":ay},
					fields=["name as term", "term_start_date as start", "term_end_date as end"])
		for term in terms:
			self.append("terms", {
				"term": term.term, "start": term.start, "end": term.end, "length": 12
				})


	def validate(self):
		self.terms = []
