# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, getdate

class MAPTest(Document):
	def validate(self):
		self.validate_dates()
		self.validate_duplicate()

	def validate_dates(self):
		if self.academic_term:
			term_dates = frappe.get_doc("Academic Term", self.academic_term)
			if term_dates.academic_year != self.academic_year:
				frappe.throw(_("The term does not belong to that academic year."))
			if self.test_date and getdate(term_dates.term_start_date) and getdate(self.test_date) < getdate(term_dates.term_start_date):
				frappe.throw(_("The test date for this test is before the start of the term.  Please revise the date of the test."))
			if self.test_date and getdate(term_dates.term_end_date) and getdate(self.test_date) > getdate(term_dates.term_end_date):
				frappe.throw(_("The test date for this test is after the start of the term.  Please revise the date of the test."))


	def validate_duplicate(self):
		map_test =  frappe.get_all("MAP Test", filters = {
			"student": self.student,
			"academic_term": self.academic_term,
			"discipline": self.discipline
		})
		if  map_test:
			frappe.throw(_("There is already a MAP test submitted for this student and this term and this subject."))
