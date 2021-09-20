# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet
from frappe.utils import getdate
from frappe import _
from frappe.utils import getdate, validate_email_address, today, add_years, format_datetime, cstr
from frappe.permissions import add_user_permission, remove_user_permission, set_user_permission_if_allowed, has_permission, get_doc_permissions
from frappe.contacts.address_and_contact import load_address_and_contact
from ifitwala_ed.utilities.transaction_base import delete_events

class EmployeeUserDisabledError(frappe.ValidationError): pass
class EmployeeLeftValidationError(frappe.ValidationError): pass

class Employee(NestedSet):
	nsm_parent_field = 'reports_to'

	def onload(self):
		load_address_and_contact(self)

	def validate(self):
		from ifitwala_ed.controllers.status_updater import validate_status
		validate_status(self.status, ["Active", "Temporary Leave", "Left"])

		self.employee = self.name
		self.employee_full_name = " ".join(filter(None, [self.employee_first_name, self.employee_middle_name, self.employee_last_name]))
		self.validate_date()
		self.validate_email()
		self.validate_status()
		self.validate_reports_to()
		if self.user_id:
			self.validate_user_details()
		else:
			existing_user_id = frappe.db.get_value("Employee", self.name, "user_id")
			if existing_user_id:
				remove_user_permission("Employee", self.name, existing_user_id)

	def after_rename(self, old, new, merge):
		self.db_set("employee", new)

	def on_update(self):
		if self.user_id:
			self.update_user()
			self.update_user_permissions()

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def on_trash(self):
		self.update_nsm_model()
		delete_events(self.doctype, self.name)

	# call on validate.  Broad check to make sure birtdhdate, joining date are making sense.
	def validate_date(self):
		if self.employee_date_of_birth and getdate(self.employee_date_of_birth) > getdate(today()):
			frappe.throw(_("Date of Birth cannot be after today."))
		if self.employee_date_of_birth and self.date_of_joining and getdate(self.employee_date_of_birth) >= getdate(self.date_of_joining):
			frappe.throw(_("Date of Joining must be after Date of Birth"))
		if self.notice_date and self.relieving_date and getdate(self.relieving_date) <  getdate(self.notice_date):
			frappe.throw(_("Date of Notice {0} should be before Relieving Date {1}. Please adjust dates.").format(getdate(self.notice_date), getdate(self.relieving_date)))
		if self.relieving_date and self.date_of_joining and getdate(self.relieving_date) <  getdate(self.date_of_joining):
			frappe.throw(_("Date of Joining {0} should be before Relieving Date {1}. Please adjust dates.").format(getdate(self.date_of_joining), getdate(self.relieving_date)))

	# call on validate. Broad check to make sure the email address has an appropriate format.
	def validate_email(self):
		if self.employee_professional_email:
			validate_email_address(self.employee_professional_email, True)
		if self.employee_personal_email:
			validate_email_address(self.employee_personal_email, True)

	# call on validate.  If status is set to left, then need to put relieving date.
	# also you can not be set as left if there are people reporting to you.
	def validate_status(self):
		if self.status == 'Left':
			reports_to = frappe.db.get_all('Employee', filters={'reports_to': self.name, 'status': "Active"}, fields=['name','employee_full_name'])
			if reports_to:
				link_to_employees = [frappe.utils.get_link_to_form('Employee', employee.name, label=employee.employee_full_name) for employee in reports_to]
				message = _("The following employees are currently still reporting to {0}:").format(frappe.bold(self.employee_name))
				message += "<br><br><ul><li>" + "</li><li>".join(link_to_employees)
				message += "</li></ul><br>"
				message += _("Please make sure the employees above report to another Active employee.")
				frappe.throw(message, EmployeeLeftValidationError, _("Cannot Relieve Employee"))
			if not self.relieving_date:
				frappe.throw(_("Please enter relieving date."))

	# call on validate.  You cannot report to yourself.
	def validate_reports_to(self):
		if self.reports_to == self.name:
			frappe.throw(_("Employee cannot report to her/himself."))

	# call on validate.  Check that if there is already a user, a few more checks to do.
	def validate_user_details(self):
		data = frappe.db.get_value('User', self.user_id, ['enabled', 'user_image'], as_dict=1)
		if data.get("user_image"):
			self.employee_image = data.get("user_image")
		self.validate_for_enabled_user_id(data.get("enabled", 0))
		self.validate_duplicate_user_id()

	# call on validate through validate_user_details().
	# If employee is referring to a user, that user has to be active.
	def validate_for_enabled_user_id(self, enabled):
		if not self.status == 'Active':
			return
		if enabled is None:
			frappe.throw(_("User {0} does not exist").format(self.user_id))
		if enabled == 0:
			frappe.throw(_("User {0} is disabled").format(self.user_id), EmployeeUserDisabledError)

	# call on validate through validate_user_details().
	def validate_duplicate_user_id(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where user_id=%s and status='Active' and name!=%s""", (self.user_id, self.name))
		if employee:
			frappe.throw(_("User {0} is already assigned to Employee {1}").format(self.user_id, employee[0]), frappe.DuplicateEntryError)


	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.user_id)
		privacy = frappe.get_single("Privacy Settings")
		user.flags.ignore_permissions = True

		if "Employee" not in user.get("roles"):
			user.append_roles("Employee")

		user.first_name = self.employee_first_name
		user.middle_name = self.employee_middle_name
		user.last_name = self.employee_last_name
		user.full_name = self.employee_full_name


		if self.employee_date_of_birth and privacy.dob_to_user==1:
			user.birth_date = self.employee_date_of_birth
		if self.employee_mobile_phone and privacy.mobile_to_user==1:
			user.mobile_no = self.employee_mobile_phone
		if self.employee_image:
			if not user.user_image:
				user.user_image = self.employee_image
				try:
					img = frappe.get_doc({"doctype": "File", "file_url": self.employee_image,
						"attached_to_doctype": "User",
						"attached_to_name": self.user_id
						})
					img.insert(ignore_permissions=True)
				except frappe.DuplicateEntryError:
					# already exists
					pass
		user.save()

	def update_user_permissions(self):
		if not self.create_user_permission: return
		if not has_permission('User Permission', ptype='write', raise_exception=False): return

		employee_user_permission_exists = frappe.db.exists('User Permission', {
			'allow': 'Employee',
			'for_value': self.name,
			'user': self.user_id
		})

		if employee_user_permission_exists: return

		add_user_permission("Employee", self.name, self.user_id)
		set_user_permission_if_allowed("Organization", self.organization, self.user_id)




@frappe.whitelist()
def create_user(employee, user = None, email=None):
	emp = frappe.get_doc("Employee", employee)
	privacy = frappe.get_single("Privacy Settings")
	birth_date = None
	phone = None
	if emp.employee_date_of_birth and privacy.dob_to_user==1:
		birth_date = emp.employee_date_of_birth
	if emp.employee_mobile_phone and privacy.mobile_to_user==1:
		phone = emp.employee_mobile_phone

	user = frappe.new_doc("User")
	user.update({
		"name": emp.employee_full_name,
		"email": emp.employee_professional_email,
		"enabled": 1,
		"first_name": emp.employee_first_name,
		"middle_name": emp.employee_middle_name,
		"last_name": emp.employee_last_name,
		"gender": emp.employee_gender,
		"birth_date": birth_date,
		"mobile_no": phone
	})
	user.insert()
	return user.name

@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False, is_tree=False):

	filters = [['status', '!=', 'Left']]
	if organization and organization != 'All Organizations':
		filters.append(['organization', '=', organization])

	fields = ['name as value', 'employee_full_name as title']

	if is_root:
		parent = ''
	if parent and organization and parent!=organization:
		filters.append(['reports_to', '=', parent])
	else:
		filters.append(['reports_to', '=', ''])

	employees = frappe.get_list(doctype, fields=fields,
		filters=filters, order_by='name')

	for employee in employees:
		is_expandable = frappe.get_all(doctype, filters=[
			['reports_to', '=', employee.get('value')]
		])
		employee.expandable = 1 if is_expandable else 0

	return employees


def on_doctype_update():
	frappe.db.add_index("Employee", ["lft", "rgt"])

def validate_employee_role(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("roles")]:
		if not frappe.db.get_value("Employee", {"user_id": doc.name}):
			frappe.msgprint(_("Please set User ID field in the Employee record to set Employee Role"))
			doc.get("roles").remove(doc.get("roles", {"role": "Employee"})[0])

def update_user_permissions(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("roles")]:
		if not has_permission('User Permission', ptype='write', raise_exception=False): return
		employee = frappe.get_doc("Employee", {"user_id": doc.name})
		employee.update_user_permissions()


def has_upload_permission(doc, ptype='read', user=None):
	if not user:
		user = frappe.session.user
	if get_doc_permissions(doc, user=user, ptype=ptype).get(ptype):
		return True
	return doc.user_id == user

def get_employee_emails(employee_doc):
	return employee_doc.get("user_id") or employee_doc.get("employee_professional_email") or employee_doc.get("employee_personal_email")
