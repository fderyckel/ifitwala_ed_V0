# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today, getdate

class Meeting(Document):

	def validate(self):
		if not self.attendees:
			self.extend("attendees", self.get_attendees())
		self.validate_attendees()
		self.validate_date()
		self.validate_time()

	def on_update(self):
		self.sync_todos()

	def validate_attendees(self):
		found = []
		for attendee in self.attendees:
			if attendee.attendee in found:
				frappe.throw(_("Attendee {0} entered twice.").format(attendee.attendee))
			else:
				found.append(attendee.attendee)

	def get_attendees(self):
		return frappe.db.sql("""select member as attendee, member_name as full_name from `tabDepartment Member` where parent = %s""", (self.department), as_dict=1)

	def validate_date(self):
		if getdate(self.date) < getdate(today()):
			frappe.throw(_("The date {0} of the meeting has to be in the future. Please adjust the date.").format(self.date))

	def validate_time(self):
		if self.from_time >= self.to_time:
			frappe.throw(_("The start time of your meeting {0} has to be earlier than its end {1}. Please adjust the time.").format(self.from_timme, self.to_time))

	def sync_todos(self):
		todos_added = [todo.name for todo in
				frappe.get_all("ToDo",
						filters = {
									"reference_type": self.doctype,
									"reference_name": self.name
						})
				]

		for minute in self.minutes:
			if minute.assigned_to and minute.status=="Open":
				if not minute.todo:
					todo = frappe.get_doc({
						"doctype": "ToDo",
						"description": minute.discussion,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"owner": minute.assigned_to,
						"assigned_by": self.meeting_organizer,
						"date": minute.completed_by
						})
					todo.insert()
					minute.db_set("todo", todo.name, update_modified=False)

				else:
					todos_added.remove(minute.todo)

			else:
				minute.db_set("todo", None, update_modified=False)

		for todo in todos_added:
			todo=frappe.get_doc("ToDo", todo)
			todo.flags.from_meeting = True,
			todo.delete()


def meeting_has_permission(doc, user=None, permission_type=None):
	attendees = frappe.get_all("Meeting Attendee", filters = {"parent": doc}, fields = ["attendee"])
	attendee_list = [d.attendee for d in attendees]
	#user = frappe.get_doc('User', frappe.session.user)

	if permission_type == "read" and (user in attendee_list):
		return True

	if permission_type == "write" and doc.meeting_organizer == user:
		return True

	return False
