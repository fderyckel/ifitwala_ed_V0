# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, getdate
from .default_website import website_maker
from ifitwala_ed.accounting.doctype.account.account import RootNotEditable



def create_fiscal_year_and_school(args):
	if (args.get('fy_start_date')):
		curr_fiscal_year = get_fy_details(args.get('fy_start_date'), args.get('fy_end_date'))
		frappe.get_doc({
			"doctype":"Fiscal Year",
			'year': curr_fiscal_year,
			'year_start_date': args.get('fy_start_date'),
			'year_end_date': args.get('fy_end_date'),
		}).insert()

	if (args.get('school_name')):
		frappe.get_doc({
			"doctype":"School",
			'school_name':args.get('school_name'),
			'enable_perpetual_inventory': 1,
			'abbr':args.get('school_abbr'),
			'default_currency':args.get('currency'),
			'country': args.get('country'),
			'create_chart_of_accounts_based_on': 'Standard Template',
			'chart_of_accounts': args.get('chart_of_accounts'),
			'domain': args.get('domains')[0]
		}).insert()

def create_bank_account(args):
	if args.get("bank_account"):
		school_name = args.get('school_name')
		bank_account_group =  frappe.db.get_value("Account",
			{"account_type": "Bank", "is_group": 1, "root_type": "Asset",
				"school": school_name})
		if bank_account_group:
			bank_account = frappe.get_doc({
				"doctype": "Account",
				'account_name': args.get("bank_account"),
				'parent_account': bank_account_group,
				'is_group':0,
				'school': school_name,
				"account_type": "Bank",
			})
			try:
				return bank_account.insert()
			except RootNotEditable:
				frappe.throw(_("Bank account cannot be named as {0}").format(args.get("bank_account")))
			except frappe.DuplicateEntryError:
				# bank account same as a CoA entry
				pass


def create_logo(args):
	if args.get("attach_logo"):
		attach_logo = args.get("attach_logo").split(",")
		if len(attach_logo)==3:
			filename, filetype, content = attach_logo
			_file = frappe.get_doc({
				"doctype": "File",
				"file_name": filename,
				"attached_to_doctype": "Website Settings",
				"attached_to_name": "Website Settings",
				"decode": True})
			_file.save()
			fileurl = _file.file_url
			frappe.db.set_value("Website Settings", "Website Settings", "brand_html",
				"<img src='{0}' style='max-width: 40px; max-height: 25px;'> {1}".format(fileurl, args.get("school_name")))

def create_website(args):
	website_maker(args)

def get_fy_details(fy_start_date, fy_end_date):
	start_year = getdate(fy_start_date).year
	if start_year == getdate(fy_end_date).year:
		fy = cstr(start_year)
	else:
		fy = cstr(start_year) + '-' + cstr(start_year + 1)
	return fy
