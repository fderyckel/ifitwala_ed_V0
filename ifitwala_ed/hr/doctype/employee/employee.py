# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe import _ 
from frappe.utils import getdate, validate_email_address, today, add_years, format_datetime, cstr
from frappe.permissions import add_user_permission, remove_user_permission, set_user_permission_if_allowed, has_permission

class EmployeeUserDisabledError(frappe.ValidationError): pass
class EmployeeLeftValidationError(frappe.ValidationError): pass

class Employee(Document): 
		
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
	
	def on_update(self):
		if self.user_id:
			self.update_user()
			self.update_user_permissions()
			
		
		
	# call on validate.  Broad check to make sure birtdhdate, joining date are making sense. 
	def validate_date(self):
		if self.employee_date_of_birth and getdate(self.employee_date_of_birth) > getdate(today()):
			frappe.throw(_("Date of Birth cannot be after today."))
		if self.employee_date_of_birth and self.date_of_joining and getdate(self.employee_date_of_birth) >= getdate(self.date_of_joining):
			frappe.throw(_("Date of Joining must be after Date of Birth"))
	
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
			reports_to = frappe.db.get_all('Employee',
				filters={'reports_to': self.name, 'status': "Active"},
				fields=['name','employee_full_name']
			)
			if reports_to:
				link_to_employees = [frappe.utils.get_link_to_form('Employee', employee.name, label=employee.employee_full_name) for employee in reports_to]
				frappe.throw(_("Employee status cannot be set to 'Left' as following employees are currently reporting to this employee.")
					+ ', '.join(link_to_employees), EmployeeLeftValidationError)
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
	
	
	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self) 
	
	
	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.user_id)
		user.flags.ignore_permissions = True

		if "Employee" not in user.get("roles"):
			user.append_roles("Employee")

		# copy details like Fullname, DOB and Image to User
		if self.employee_full_name and not (user.first_name and user.last_name):
			employee_name = self.employee_full_name.split(" ")
			if len(employee_name) >= 3:
				user.last_name = " ".join(employee_name[2:])
				user.middle_name = employee_name[1]
			elif len(employee_name) == 2:
				user.last_name = employee_name[1]
			user.first_name = employee_name[0]

		if self.employee_date_of_birth:
			user.birth_date = self.employee_date_of_birth
		if self.employee_gender:
			user.gender = self.employee_gender
		#if self.image:
		#	if not user.user_image:
		#		user.user_image = self.image
		#		try:
		#			frappe.get_doc({
		#				"doctype": "File",
		#				"file_name": self.image,
		#				"attached_to_doctype": "User",
		#				"attached_to_name": self.user_id
		#			}).insert()
		#		except frappe.DuplicateEntryError:
		#			# already exists
		#			pass
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
		set_user_permission_if_allowed("School", self.school, self.user_id)
		
		
	

	
@frappe.whitelist()
def create_user(employee, user = None, email=None):
	emp = frappe.get_doc("Employee", employee)

	employee_name = emp.employee_full_name.split(" ")
	middle_name = last_name = ""

	if len(employee_name) >= 3:
		last_name = " ".join(employee_name[2:])
		middle_name = employee_name[1]
	elif len(employee_name) == 2:
		last_name = employee_name[1]

	first_name = employee_name[0]

	if email:
		emp.employee_professional_email = email

	user = frappe.new_doc("User")
	user.update({
		"name": emp.employee_full_name,
		"email": emp.employee_professional_email,
		"enabled": 1,
		"first_name": first_name,
		"middle_name": middle_name,
		"last_name": last_name,
		"gender": emp.employee_gender,
		"birth_date": emp.employee_date_of_birth,
		"phone": emp.employee_mobile_phone
	})
	user.insert()
	return user.name
