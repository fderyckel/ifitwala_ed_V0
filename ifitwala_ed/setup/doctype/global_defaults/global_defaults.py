# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import cint
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.document import Document

keydict = {
	# "key in defaults": "key in Global Defaults"
	"fiscal_year": "current_fiscal_year",
	'organization': 'default_organization',
	'currency': 'default_currency',
	"country": "country",
	'hide_currency_symbol':'hide_currency_symbol',
	'account_url':'account_url',
	'disable_rounded_total': 'disable_rounded_total',
	'disable_in_words': 'disable_in_words',
}

class GlobalDefaults(Document):
	def on_update(self):
		for key in keydict:
			frappe.db.set_default(key, self.get(keydict[key], ''))

		# update year start date and year end date from fiscal_year
		year_start_end_date = frappe.db.sql("""SELECT year_start_date, year_end_date FROM `tabFiscal Year` WHERE name=%s""", self.current_fiscal_year)
		if year_start_end_date:
			ysd = year_start_end_date[0][0] or ''
			yed = year_start_end_date[0][1] or ''

			if ysd and yed:
				frappe.db.set_default('year_start_date', ysd.strftime('%Y-%m-%d'))
				frappe.db.set_default('year_end_date', yed.strftime('%Y-%m-%d'))

		# enable default currency
		if self.default_currency:
			frappe.db.set_value("Currency", self.default_currency, "enabled", 1)

		# clear cache
		frappe.clear_cache()

	@frappe.whitelist()
	def get_defaults(self):
		return frappe.defaults.get_defaults()
