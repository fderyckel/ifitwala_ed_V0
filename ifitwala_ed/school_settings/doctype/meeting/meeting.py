# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document
from frappe import _
from frappe.utils import today, getdate, get_time, now_datetime, get_datetime
from frappe.permissions import add_user_permission, remove_user_permission, set_user_permission_if_allowed, has_permission

class Meeting(Document):

	def validate(self):
		if not self.attendees:
			self.extend("attendees", self.get_attendees())
		self.validate_attendees()
		self.validate_date()
		self.validate_time()

	def on_update(self):
		self.sync_todos()
		if self.attendees:
			self.create_calendar_events()

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
			frappe.throw(_("The start time of your meeting {0} has to be earlier than its end {1}. Please adjust the time.").format(self.from_time, self.to_time))

	def create_calendar_events(self):
		if self.school_event:
			return
		meeting_event = frappe.get_doc({
			"doctype": "School Event",
			"owner": self.meeting_organizer,
			"subject": self.meeting_name,
			"starts_on": datetime.datetime.combine(getdate(self.date), get_time(self.from_time)),
			"ends_on": datetime.datetime.combine(getdate(self.date), get_time(self.to_time)),
			"status": "Open",
			"event_category": "Meeting",
			"type": "Private"
		})
		for attendee in self.attendees:
			meeting_event.append("participants", {user = attendee.attendee})
		meeting_event.insert(ignore_permissions=True)
		self.school_event = meeting_event.name
		self.save(ignore_permissions=True)

	def sync_todos(self):
		default_color = frappe.get_single("Education Settings")
		for minute in self.minutes:
			if minute.assigned_to and minute.status=="Open":
				if minute.todo:
					todo = frappe.get_doc({
						"doctype": "ToDo",
						"name": minute.todo
						})
					todo.description = minute.discussion,
					todo.assigned_by = self.meeting_organizer,
					todo.date = minute.completed_by
					todo.save(ignore_permissions = True)

				if not minute.todo:
					todo = frappe.get_doc({
						"doctype": "ToDo",
						"description": minute.discussion,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"owner": minute.assigned_to,
						"assigned_by": self.meeting_organizer,
						"date": minute.completed_by,
						"color": default_color.default_todo_meeting_color
						})
					todo.insert()
					minute.db_set("todo", todo.name, update_modified = False)


	def set_status(self):
		endtime = datetime.datetime.combine(getdate(self.date), get_time(self.to_time))
		starttime = datetime.datetime.combine(getdate(self.date), get_time(self.from_time))
		if get_datetime(endtime) < get_datetime(now_datetime()):
			self.status = "Completed"
		elif get_datetime(starttime) <= get_datetime(now_datetime()) <= get_datetime(endtime):
			self.status = "In Progress"


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	return """(name in (select parent from `tabMeeting Attendee`where attendee=%(user)s) or owner=%(user)s)""" % {
			"user": frappe.db.escape(user),
		}

def meeting_has_permission(doc, user):
	if doc.is_new():
		return True

	if doc.owner == user or user in [d.attendee for d in doc.attendees]:
		return True

	return False


def update_minute_status(doc, method = None):
	if doc.reference_type != "Meeting" or doc.flags.from_meeting:
		return

	if method == "on_trash" or doc.status == "Closed":
		meeting = frappe.get_doc(doc.reference_type, doc.reference_name)
		for minute in meeting.minutes:
			if minute.todo == doc.name:
				minute.db_set("status", "Close", update_modified = False)

def update_meeting_status():
	# update the status of appointments daily
	meetings = frappe.get_all('Meeting', {
		'status': ('not in', ['Completed', 'Cancelled'])
	}, as_dict=1)

	for meeting in meetings:
		frappe.get_doc('Meeting', meeting.name).set_status()


#	def update_attendee_permission(self):
#		#if not has_permission('User Permission', ptype='write', raise_exception=False): return
#		for attendee in self.attendees:
#			attendee_user_permission_exists = frappe.db.exists('User Permission', {
#					'allow': 'Meeting',
#					'for_value': self.name,
#					'user': attendee.attendee
#			})
#			if attendee_user_permission_exists: return
#			add_user_permission("Meeting", self.name, attendee.attendee)
#			set_user_permission_if_allowed("Meeting", self.name, attendee.attendee)
