# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from .operations import install_fixtures as fixtures, organization_setup

def get_setup_stages(args=None):
	if frappe.db.sql("select name from tabOrganization"):
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
				'status': _('Setting up organization'),
				'fail_msg': _('Failed to setup organization'),
				'tasks': [
					{
						'fn': setup_organization,
						'args': args,
						'fail_msg': _("Failed to setup organization")
					}
				]
			},
			{
				'status': _('Setting defaults'),
				'fail_msg': 'Failed to set defaults',
				'tasks': [
					{
						'fn': setup_post_organization_fixtures,
						'args': args,
						'fail_msg': _("Failed to setup post organization fixtures")
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

def setup_organization(args):
	fixtures.install_organization(args)

def setup_post_organization_fixtures(args):
	fixtures.install_post_organization_fixtures(args)

def setup_defaults(args):
	fixtures.install_defaults(frappe._dict(args))

def stage_four(args):
	organization_setup.create_website(args)
	organization_setup.create_logo(args)


def fin(args):
	frappe.local.message_log = []
	login_as_first_user(args)

def login_as_first_user(args):
	if args.get("email") and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(args.get("email"))


# Only for programmatical use
def setup_complete(args=None):
	stage_fixtures(args)
	setup_organization(args)
	setup_post_organization_fixtures(args)
	setup_defaults(args)
	stage_four(args)
	fin(args)
