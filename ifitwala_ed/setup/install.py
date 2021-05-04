# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.installer import update_site_config
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from six import iteritems

def after_install():
	frappe.get_doc({'doctype': "Role", "role_name": "Analytics"}).insert()
	add_organization_to_session_defaults()
	add_standard_navbar_items()
	add_all_roles_to("Administrator")
	add_app_name()
	add_non_standard_user_types()
	frappe.db.commit()


def check_setup_wizard_not_completed():
	if cint(frappe.db.get_single_value('System Settings', 'setup_complete') or 0):
		message = """Ifitwala  Ed can only be installed on a fresh site where the setup wizard is not completed.
You can reinstall this site (after saving your data) using: bench --site [sitename] reinstall"""
		frappe.throw(message)


def add_organization_to_session_defaults():
	settings = frappe.get_single("Session Default Settings")
	settings.append("session_defaults", {"ref_doctype": "Organization"})
	settings.save()


def add_standard_navbar_items():
	navbar_settings = frappe.get_single("Navbar Settings")

	ifitwala_ed_navbar_items = [
		{
			'item_label': 'Documentation',
			'item_type': 'Route',
			'route': 'http://docs.ifitwala.com/',
			'is_standard': 1
		},
		{
			'item_label': 'Ifitwala Educaton Site',
			'item_type': 'Route',
			'route': 'http://ifitwala.com',
			'is_standard': 1
		},
		{
			'item_label': 'Report an Issue',
			'item_type': 'Route',
			'route': 'https://github.com/fderyckel/ifitwala_ed/issues',
			'is_standard': 1
		}
	]

	current_nabvar_items = navbar_settings.help_dropdown
	navbar_settings.set('help_dropdown', [])

	for item in ifitwala_ed_navbar_items:
		navbar_settings.append('help_dropdown', item)

	for item in current_nabvar_items:
		navbar_settings.append('help_dropdown', {
			'item_label': item.item_label,
			'item_type': item.item_type,
			'route': item.route,
			'action': item.action,
			'is_standard': item.is_standard,
			'hidden': item.hidden
		})

	navbar_settings.save()


def add_app_name():
	settings = frappe.get_doc("System Settings")
	settings.app_name = _("Ifitwala Ed")

def add_non_standard_user_types():
	user_types = get_user_types_data()

	user_type_limit = {}
	for user_type, data in iteritems(user_types):
		user_type_limit.setdefault(frappe.scrub(user_type), 10)

	update_site_config('user_type_doctype_limit', user_type_limit)

	for user_type, data in iteritems(user_types):
		create_custom_role(data)
		create_user_type(user_type, data)

def get_user_types_data():
	return {
		'Employee Self Service': {
			'role': 'Employee Self Service',
			'apply_user_permission_on': 'Employee',
			'user_id_field': 'user_id',
			'doctypes': {
				'Employee': ['read', 'write']
			}
		}
	}

def create_custom_role(data):
	if data.get('role') and not frappe.db.exists('Role', data.get('role')):
		frappe.get_doc({
			'doctype': 'Role',
			'role_name': data.get('role'),
			'desk_access': 1,
			'is_custom': 1
		}).insert(ignore_permissions=True)

def create_user_type(user_type, data):
	if frappe.db.exists('User Type', user_type):
		doc = frappe.get_cached_doc('User Type', user_type)
		doc.user_doctypes = []
	else:
		doc = frappe.new_doc('User Type')
		doc.update({
			'name': user_type,
			'role': data.get('role'),
			'user_id_field': data.get('user_id_field'),
			'apply_user_permission_on': data.get('apply_user_permission_on')
		})

	create_role_permissions_for_doctype(doc, data)
	doc.save(ignore_permissions=True)

def create_role_permissions_for_doctype(doc, data):
	for doctype, perms in iteritems(data.get('doctypes')):
		args = {'document_type': doctype}
		for perm in perms:
			args[perm] = 1

		doc.append('user_doctypes', args)

def update_select_perm_after_install():
	if not frappe.flags.update_select_perm_after_migrate:
		return

	frappe.flags.ignore_select_perm = False
	for row in frappe.get_all('User Type', filters= {'is_standard': 0}):
		print('Updating user type :- ', row.name)
		doc = frappe.get_doc('User Type', row.name)
		doc.save()

	frappe.flags.update_select_perm_after_migrate = False
