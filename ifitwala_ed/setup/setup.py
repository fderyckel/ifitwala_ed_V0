# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, json
from frappe import _
from ifitwala_ed.setup.utils import insert_record
from frappe.desk.doctype.global_search_settings.global_search_settings import update_global_search_doctypes

def setup_education():
	disable_desk_access_for_guardian_role()
	create_designations()
	create_log_type()
	create_attendance_code()
	create_location_type()
	add_other_records()
	add_uom_data()
	update_global_search_doctypes()


def disable_desk_access_for_guardian_role():
	try:
		guardian_role = frappe.get_doc("Role", "Guardian")
	except frappe.DoesNotExistError:
		create_guardian_role()
		return

	guardian_role.desk_access = 0
	guardian_role.save()

def create_guardian_role():
	guardian_role = frappe.get_doc({
		"doctype": "Role",
		"role_name": "Guardian",
		"desk_access": 0
	})
	guardian_role.insert()

def create_designations():
	data = [
		{"doctype": "Designation", "designation_name": "Director"},
		{"doctype": "Designation", "designation_name": "Principal"},
		{"doctype": "Designation", "designation_name": "Assistant Principal"},
		{"doctype": "Designation", "designation_name": "Nurse"},
		{"doctype": "Designation", "designation_name": "Teacher"},
		{"doctype": "Designation", "designation_name": "Teacher Assistant"}
	]
	insert_record(data)

def create_log_type():
	data = [
			{"doctype": "Student Log Type", "log_type": "Behaviour"},
			{"doctype": "Student Log Type", "log_type": "Academic"},
			{"doctype": "Student Log Type", "log_type": "Medical"}
	]
	insert_record(data)

def create_attendance_code():
	data = [
			{"doctype": "Student Attendance Code", "attendance_code": "Present"},
			{"doctype": "Student Attendance Code", "attendance_code": "Absent"},
			{"doctype": "Student Attendance Code", "attendance_code": "Tardy"},
			{"doctype": "Student Attendance Code", "attendance_code": "Excused Absence"},
			{"doctype": "Student Attendance Code", "attendance_code": "Field Trip"},
			{"doctype": "Student Attendance Code", "attendance_code": "Excused Tardy"}
	]
	insert_record(data)

def create_location_type():
	data = [
		{"doctype": "Location Type", "location_type_name": "Classroom"},
		{"doctype": "Location Type", "location_type_name": "Office"},
		{"doctype": "Location Type", "location_type_name": "Library"},
		{"doctype": "Location Type", "location_type_name": "Building"},
		{"doctype": "Location Type", "location_type_name": "Storage"},
		{"doctype": "Location Type", "location_type_name": "Sport Court"},
		{"doctype": "Location Type", "location_type_name": "Theatre"},
		{"doctype": "Location Type", "location_type_name": "Auditorium"}, 
		{"doctype": "Location Type", "location_type_name": "Gym"},
		{"doctype": "Location Type", "location_type_name": "Transit"},
	]
	insert_record(data)

def add_uom_data():
	# add UOMs
	uoms = json.loads(open(frappe.get_app_path("ifitwala_ed", "setup", "setup_wizard", "data", "uom_data.json")).read())
	for d in uoms:
		if not frappe.db.exists('UOM', _(d.get("uom_name"))):
			uom_doc = frappe.get_doc({
				"doctype": "UOM",
				"uom_name": _(d.get("uom_name")),
				"name": _(d.get("uom_name")),
				"must_be_whole_number": d.get("must_be_whole_number")
			}).insert(ignore_permissions=True)

		# bootstrap uom conversion factors
	uom_conversions = json.loads(open(frappe.get_app_path("ifitwala_ed", "setup", "setup_wizard", "data", "uom_conversion_data.json")).read())
	for d in uom_conversions:
		if not frappe.db.exists("UOM Category", _(d.get("category"))):
			frappe.get_doc({
				"doctype": "UOM Category",
				"category_name": _(d.get("category"))
			}).insert(ignore_permissions=True)

		if not frappe.db.exists("UOM Conversion Factor", {"from_uom": _(d.get("from_uom")), "to_uom": _(d.get("to_uom"))}):
			uom_conversion = frappe.get_doc({
				"doctype": "UOM Conversion Factor",
				"category": _(d.get("category")),
				"from_uom": _(d.get("from_uom")),
				"to_uom": _(d.get("to_uom")),
				"value": d.get("value")
			}).insert(ignore_permissions=True)

def add_other_records(country=None):
	records = [
		# item group
		{'doctype': 'Item Group', 'item_group_name': _('All Item Groups'), 'is_group': 1, 'parent_item_group': ''},

		# Employment Type
		{'doctype': 'Employment Type', 'employment_type_name': _('Full-time')},
		{'doctype': 'Employment Type', 'employment_type_name': _('Part-time')},
		{'doctype': 'Employment Type', 'employment_type_name': _('Probation')},
		{'doctype': 'Employment Type', 'employment_type_name': _('Contract')},
		{'doctype': 'Employment Type', 'employment_type_name': _('Intern')},
		{'doctype': 'Employment Type', 'employment_type_name': _('Apprentice')},

		{'doctype': 'Mode of Payment', 'mode_of_payment': 'Check' if country=="United States" else _('Cheque'), 'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Cash'), 'type': 'Cash'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Credit Card'), 'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Wire Transfer'), 'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Bank Draft'), 'type': 'Bank'},

		{'doctype': "Party Type", "party_type": "Supplier", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Employee", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Student", "account_type": "Receivable"},

		{'doctype': "UOM Category", "category_name": "Length"},
		{'doctype': "UOM Category", "category_name": "Area"},
		{'doctype': "UOM Category", "category_name": "Volume"},
		{'doctype': "UOM Category", "category_name": "Density"},
		{'doctype': "UOM Category", "category_name": "Mass"},
		{'doctype': "UOM Category", "category_name": "Speed"},
	]
	insert_record(records)
