# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_years, cstr
from dateutil.relativedelta import relativedelta
from frappe.model.document import Document

class FiscalYearIncorrectDate(frappe.ValidationError): pass

class FiscalYear(Document):
	@frappe.whitelist()
	def set_as_default(self):
		frappe.db.set_value("Global Defaults", None, "current_fiscal_year", self.name)
		global_defaults = frappe.get_doc("Global Defaults")
		global_defaults.check_permission("write")
		global_defaults.on_update()

		# clear cache
		frappe.clear_cache()

		frappe.msgprint(_("{0} is now the default Fiscal Year. Please refresh your browser for the change to take effect.").format(self.name))

	def validate(self):
		self.validate_dates()
		self.validate_overlap()

		if not self.is_new():
			year_start_end_dates = frappe.db.sql("""SELECT year_start_date, year_end_date FROM `tabFiscal Year` WHERE name=%s""", (self.name))

			if year_start_end_dates:
				if getdate(self.year_start_date) != year_start_end_dates[0][0] or getdate(self.year_end_date) != year_start_end_dates[0][1]:
					frappe.throw(_("Cannot change Fiscal Year Start Date and Fiscal Year End Date once the Fiscal Year is saved."))

	def on_update(self):
		check_duplicate_fiscal_year(self)
		frappe.cache().delete_value("fiscal_years")

	def on_trash(self):
		global_defaults = frappe.get_doc("Global Defaults")
		if global_defaults.current_fiscal_year == self.name:
			frappe.throw(_("You cannot delete Fiscal Year {0}. Fiscal Year {0} is set as default in Global Settings").format(self.name))
		frappe.cache().delete_value("fiscal_years")

#######################STARTING def called earlier############

	def validate_dates(self):
		if self.is_short_year:
			return

		if getdate(self.year_start_date) > getdate(self.year_end_date):
			frappe.throw(_("Fiscal Year Start Date should be one year earlier than Fiscal Year End Date"), FiscalYearIncorrectDate)

		date = getdate(self.year_start_date) + relativedelta(years=1) - relativedelta(days=1)

		if getdate(self.year_end_date) != date:
			frappe.throw(_("Fiscal Year End Date should be one year after Fiscal Year Start Date"), FiscalYearIncorrectDate)

	def validate_overlap(self):
		existing_fiscal_years = frappe.db.sql("""select name from `tabFiscal Year`
			where (
				(%(year_start_date)s between year_start_date and year_end_date)
				or (%(year_end_date)s between year_start_date and year_end_date)
				or (year_start_date between %(year_start_date)s and %(year_end_date)s)
				or (year_end_date between %(year_start_date)s and %(year_end_date)s)
			) and name!=%(name)s""",
			{
				"year_start_date": self.year_start_date,
				"year_end_date": self.year_end_date,
				"name": self.name or "No Name"
			}, as_dict=True)

		if existing_fiscal_years:
			for existing in existing_fiscal_years:
				organization_for_existing = frappe.db.sql_list("""SELECT organization FROM `tabFiscal Year Organization` WHERE parent=%s""", existing.name)

				overlap = False
				if not self.get("organizations") or not organization_for_existing:
					overlap = True

				for d in self.get("organizations"):
					if d.organization in organization_for_existing:
						overlap = True

				if overlap:
					frappe.throw(_("Year start date or end date is overlapping with {0}. To avoid please set organization").format(existing.name), frappe.NameError)

@frappe.whitelist()
def check_duplicate_fiscal_year(doc):
	year_start_end_dates = frappe.db.sql("""select name, year_start_date, year_end_date from `tabFiscal Year` where name!=%s""", (doc.name))
	for fiscal_year, ysd, yed in year_start_end_dates:
		if (getdate(doc.year_start_date) == ysd and getdate(doc.year_end_date) == yed) and (not frappe.flags.in_test):
					frappe.throw(_("Fiscal Year Start Date and Fiscal Year End Date are already set in Fiscal Year {0}").format(fiscal_year))


@frappe.whitelist()
def auto_create_fiscal_year():
	for d in frappe.db.sql("""select name from `tabFiscal Year` where year_end_date = date_add(current_date, interval 3 day)"""):
		try:
			current_fy = frappe.get_doc("Fiscal Year", d[0])

			new_fy = frappe.copy_doc(current_fy, ignore_no_copy=False)

			new_fy.year_start_date = add_days(current_fy.year_end_date, 1)
			new_fy.year_end_date = add_years(current_fy.year_end_date, 1)

			start_year = cstr(new_fy.year_start_date.year)
			end_year = cstr(new_fy.year_end_date.year)
			new_fy.year = start_year if start_year==end_year else (start_year + "-" + end_year)
			new_fy.auto_created = 1

			new_fy.insert(ignore_permissions=True)
		except frappe.NameError:
			pass

def get_from_and_to_date(fiscal_year):
	fields = [
		"year_start_date as from_date",
		"year_end_date as to_date"
	]
	return frappe.db.get_value("Fiscal Year", fiscal_year, fields, as_dict=1)
