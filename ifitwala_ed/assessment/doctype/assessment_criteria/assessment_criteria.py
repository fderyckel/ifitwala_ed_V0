# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssessmentCriteria(Document):  
	STD_CRITERIA = ["total", "total score", "total grade", "maximum score", "score", "grade"]
	
	def validate(self):
		if self.assessment_criteria.lower() in STD_CRITERIA:
			frappe.throw(_("This is a poor name for a criteria. Please rename the criteria"))
