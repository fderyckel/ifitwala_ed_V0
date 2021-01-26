# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SchoolEvent(Document):

	def get_permission_query_conditions(user):
		if not user: user = frappe.session.user
		return """(name in (select parent from `tabSchool Event Participant`where participant=%(user)s) or owner=%(user)s)""" % {
				"user": frappe.db.escape(user),
			}

	def event_has_permission(doc, user):
		if doc.is_new():
			return True
		if doc.event_type=="Public" or doc.owner==user:
			return True

		if doc.owner == user or user in [d.participant for d in doc.participants]:
			return True

		return False
