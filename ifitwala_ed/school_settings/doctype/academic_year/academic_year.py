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

    def on_update(self):
        if self.year_start_date and self.year_end_date:
            events = frappe.get_list("School Event", filters =  {"reference_name":  self.name})
            if not events:
                self.create_calendar_events()

    def validate_duplicate(self):
        year = frappe.db.sql("""select name from `tabAcademic Year` where school=%s and academic_year_name=%s and docstatus<2 and name!=%s""", (self.school, self.academic_year_name, self.name))
        if year:
            frappe.throw(_("An academic year with this name {0} and this school already exist.").format(get_link_to_form("Academic Year", self.name)), title=_("Duplicate Entry"))

    def create_calendar_events(self):
        start_year = frappe.get_doc({
            "doctype": "School Event",
        	"owner": frappe.session.user,
        	"subject": "Start of Academic Year",
        	"starts_on": getdate(self.year_start_date),
        	"ends_on": getdate(self.year_start_date),
        	"status": "Closed",
            "school": self.school,
        	"event_category": "Other",
        	"event_type": "Public",
            "all_day": "1",
        	"color": "#7575ff",
            "reference_type": "Academic Year",
            "reference_name": self.name
        	})
        start_year.insert()
        start_year.save()

        end_year = frappe.get_doc({
            "doctype": "School Event",
        	"owner": frappe.session.user,
        	"subject": "End of Academic Year",
        	"starts_on": getdate(self.year_end_date),
        	"ends_on": getdate(self.year_end_date),
        	"status": "Closed",
            "school": self.school,
        	"event_category": "Other",
        	"event_type": "Public",
            "all_day": "1",
        	"color": "#7575ff",
            "reference_type": "Academic Year",
            "reference_name": self.name
        	})
        end_year.insert()
