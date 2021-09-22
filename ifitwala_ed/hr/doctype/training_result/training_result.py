# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from ifitwala_ed.hr.doctype.employee.employee import get_employee_emails

class TrainingResult(Document):
	def validate(self):
		training_event = frappe.get_doc("Training Event", self.training_event)
		if training_event.docstatus != 1:
			frappe.throw(_("Training Event {0} must first be submitted in order to register results.").fromat(_("Training Event")))

		self.employee_emails = ', '.join(get_employee_emails([d.employee for d in self.employees]))

	def on_submit(self):
		training_event = frappe.get_doc("Training Event", self.training_event)
		training_event.status = "Completed"
		for e in self.employees:
			for e1 in training_event.employees:
				if e1.employee = e.employee:
					e1.status = 'Completed'
					break
		training_event.save()

@frappe.whitelist()
def get_employees(training_event):
	return frappe.get_doc("Training Event", training_event).employees
