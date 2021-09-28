# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class TrainingFeedback(Document):
	def validate(self):
		training_event = frappe.get_doc("Training Event", self.training_event)
		if training_event.status != 1:
			frappe.throw(_("{0} must first be submitted").format(_("Training Event")))

		emp_event_details = frappe.db.get_value("Training Event Employee", {
			"parent": self.training_event,
			"employee": self.employee
			}, ["name", "attendance"], as_dict=True)
