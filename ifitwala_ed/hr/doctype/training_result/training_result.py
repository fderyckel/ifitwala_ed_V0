# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingResult(Document):
	pass

@frappe.whitelist()
def get_employees(training_event):
	return frappe.get_doc("Training Event", training_event).employees
