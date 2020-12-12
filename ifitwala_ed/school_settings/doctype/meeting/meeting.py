# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Meeting(Document):

	def validate(self):
		if not self.attendees:
			self.extend("attendees", self.get_attendees())
		self.validate_attendees()

	def validate_attendees(self):
		found = []
		for attendee in self.attendees:
			if attendee.attendee in found:
				frappe.throw(_("Attendee {0} entered twice.").format(attendee.attendee))
			else:
				found.append(attendee.attendee)

	def get_attendees(self):
		return frappe.db.sql("""select member as attendee, member_name as full_name from `tabDepartment Member` where parent = %s""", (self.department), as_dict=1)


	def sync_todos(self):
		for minute in self.minutes:
			if not minute.todo:
				todo = frappe.get_doc({
					"doctype": "ToDo",
					"description": minute.discussion,
					"reference_type": self.doctype,
					"reference_name": self.name,
					"owner": minute.assigned_to,
					"assigned_by": self.meeting_organizer
				})
				todo.insert()
