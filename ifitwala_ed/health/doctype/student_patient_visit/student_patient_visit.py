# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StudentPatientVisit(Document):
	
	def on_submit(self): 
		self.create_student_log() 
		
	def create_student_log(self): 
		student = frappe.db.get_value("Student Patient", self.student_patient,  "student")
		term = frappe.get_single("Education Settings").get("current_academic_term")
		log_en = frappe.get_doc({ 
			"doctype": "Student Log", 
			"student": student,  
			"academic_term": term, 
			"date": self.date, 
			"log_type": "Medical", 
			"author_name": frappe.session.user, #This need to be changed to employee full name.
			"log": " ".join(filter(None,["Today between,", self.time_of_arrival, "and", self.time_of_discharge, "the above student visit the health office. Reason: ", self.note]))
		})
		log_en.save()
		log_en.docstatus = 2
		
