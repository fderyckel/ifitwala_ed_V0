# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document 
from frappe import _

class Meeting(Document):
	
	def validate(self): 
		self.validate_attendees() 
		
	def validate_attendees(self): 
		found = []
		for attendee in self.attendees: 
			if attendee.attendee in found: 
				frappe.throw(_("Attendee {0} entered twice.").format(attendee.attendee))
			found.append(attendee.attendee)
