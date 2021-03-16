# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
import frappe

from frappe import _
from frappe.utils import cint
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def after_install():
	frappe.get_doc({'doctype': "Role", "role_name": "Analytics"}).insert()
	add_school_to_session_defaults()
	add_standard_navbar_items()
	add_all_roles_to("Administrator")
	add_app_name()
	frappe.db.commit()


def check_setup_wizard_not_completed():
	if cint(frappe.db.get_single_value('System Settings', 'setup_complete') or 0):
		message = """Ifitwala  Ed can only be installed on a fresh site where the setup wizard is not completed.
You can reinstall this site (after saving your data) using: bench --site [sitename] reinstall"""
		frappe.throw(message)


def add_school_to_session_defaults():
	settings = frappe.get_single("Session Default Settings")
	settings.append("session_defaults", {"ref_doctype": "School"})
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
