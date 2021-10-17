# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class HRSettings(Document):
	pass

@frappe.whitelist()
def set_proceed_with_frequency_change():
	'''Enables proceed with frequency change'''
	global PROCEED_WITH_FREQUENCY_CHANGE
	PROCEED_WITH_FREQUENCY_CHANGE = True
