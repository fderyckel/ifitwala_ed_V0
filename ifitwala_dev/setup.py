from __future__ import unicode_literals
import frappe

def disable_desk_access_for_student_role():
	try:
		student_role = frappe.get_doc("Role", "Student")
	except frappe.DoesNotExistError:
		create_student_role()
		return

	student_role.desk_access = 0
	student_role.save()

def create_student_role():
	student_role = frappe.get_doc({
		"doctype": "Role",
		"role_name": "Student",
		"desk_access": 0
	})
	student_role.insert()
