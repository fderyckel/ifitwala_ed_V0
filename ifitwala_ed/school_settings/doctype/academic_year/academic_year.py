# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.utils import getdate, get_link_to_form
from frappe import _
from frappe.model.document import Document


class AcademicYear(Document):

    def autoname(self):
        if self.school:
            sch_abbr = frappe.get_value("School", self.school, "abbr")
        self.name = self.academic_year_name + " ({})".format(sch_abbr) if self.school else ""


    def validate(self):
        self.validate_duplicate()

        if self.school:
            sch_abbr = frappe.get_value("School", self.school, "abbr")

        self.title = self.academic_year_name + " ({})".format(sch_abbr) if self.school else ""

        # The start of the year has to be before the end of the academic year.
        if self.year_start_date and self.year_end_date and getdate(self.year_start_date) > getdate(self.year_end_date):
            frappe.throw(_("The start of the academic year has to be before the end of the acamic year."))

    def validate_duplicate(self):
        year = frappe.db.sql("""select name from `tabAcademic Year` where school=%s and docstatus<2 and name!=%s""", (self.school, self.name))
        if year:
            frappe.throw(_("An academic year with this name {0} and this school already exist.").format(get_link_to_form("Academic Year", self.name)), title=_("Duplicate Entry"))
