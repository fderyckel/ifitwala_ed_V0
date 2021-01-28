# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import get_datetime, getdate, today, now_datetime
from frappe.model.document import Document

class SchoolEvent(Document):
	def validate(self):
		self.validate_time()

	def on_update(self):
		self.validate_date()

	def validate_date(self):
		if get_datetime(self.starts_on) < get_datetime(now_datetime()):
			frappe.throw(_("The date {0} of the event has to be in the future. Please adjust the date.").format(self.starts_on))

	def validate_time(self):
		if get_datetime(self.starts_on) >= get_datetime(self.ends_on):
			frappe.throw(_("The start time of your meeting {0} has to be earlier than its end {1}. Please adjust the time.").format(self.starts_on, self.ends_on))


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	return """(name in (select parent from `tabSchool Event Participant`where participant=%(user)s) or owner=%(user)s)""" % {
			"user": frappe.db.escape(user),
		}

def event_has_permission(doc, user):
	if doc.is_new():
		return True
	if doc.event_type=="Public":
		return True
	if doc.owner == user or user in [d.participant for d in doc.participants]:
		return True

	return False
