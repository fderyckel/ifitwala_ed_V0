# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from .operations import install_fixtures as fixtures, school_setup

def get_setup_stages(args=None):
	if frappe.db.sql("select name from tabSchool"):
		stages = [
			{
				'status': _('Wrapping up'),
				'fail_msg': _('Failed to login'),
				'tasks': [
					{
						'fn': fin,
						'args': args,
						'fail_msg': _("Failed to login")
					}
				]
			}
		]
	else:
		stages = [
			{
				'status': _('Installing presets'),
				'fail_msg': _('Failed to install presets'),
				'tasks': [
					{
						'fn': stage_fixtures,
						'args': args,
						'fail_msg': _("Failed to install presets")
					}
				]
			},
			{
				'status': _('Setting up school'),
				'fail_msg': _('Failed to setup school'),
				'tasks': [
					{
						'fn': setup_school,
						'args': args,
						'fail_msg': _("Failed to setup school")
					}
				]
			},
			{
				'status': _('Setting defaults'),
				'fail_msg': 'Failed to set defaults',
				'tasks': [
					{
						'fn': setup_post_school_fixtures,
						'args': args,
						'fail_msg': _("Failed to setup post school fixtures")
					},
					{
						'fn': setup_defaults,
						'args': args,
						'fail_msg': _("Failed to setup defaults")
					},
					{
						'fn': stage_four,
						'args': args,
						'fail_msg': _("Failed to create website")
					},
				]
			},
			{
				'status': _('Wrapping up'),
				'fail_msg': _('Failed to login'),
				'tasks': [
					{
						'fn': fin,
						'args': args,
						'fail_msg': _("Failed to login")
					}
				]
			}
		]

	return stages

def stage_fixtures(args):
	fixtures.install(args.get('country'))

def setup_school(args):
	fixtures.install_school(args)

def setup_post_school_fixtures(args):
	fixtures.install_post_school_fixtures(args)

def setup_defaults(args):
	fixtures.install_defaults(frappe._dict(args))

def stage_four(args):
	company_setup.create_website(args)
	company_setup.create_email_digest()
	company_setup.create_logo(args)

def fin(args):
	frappe.local.message_log = []
	login_as_first_user(args)

	make_sample_data(args.get('domains'))

def make_sample_data(domains):
	try:
		sample_data.make_sample_data(domains)
	except:
		# clear message
		if frappe.message_log:
			frappe.message_log.pop()
		pass

def login_as_first_user(args):
	if args.get("email") and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(args.get("email"))


# Only for programmatical use
def setup_complete(args=None):
	stage_fixtures(args)
	setup_company(args)
	setup_post_company_fixtures(args)
	setup_defaults(args)
	stage_four(args)
	fin(args)

def set_active_domains(args):
	domain_settings = frappe.get_single('Domain Settings')
	domain_settings.set_active_domains(args.get('domains'))
