# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, cstr, get_link_to_form
from frappe.model.document import Document

class AcademicTerm(Document):
    # create automatically the name of the term.
    def autoname(self):
        self.name = self.academic_year + " ({})".format(self.term_name) if self.term_name else ""

    def validate(self):
        # first, we'll check that there are no other terms that are the same.
        self.validate_duplicate()

        self.title = self.academic_year + " ({})".format(self.term_name) if self.term_name else ""

        # start of term cannot be after end of term (or vice versa)
        if self.term_start_date and self.term_end_date and getdate(self.term_start_date) > getdate(self.term_end_date):
            frappe.throw(_("The start of the term has to be before its end. "))

        year = frappe.get_doc("Academic Year", self.academic_year)
        # start of term can not be before start of academic year
        if self.term_start_date and getdate(year.year_start_date) and getdate(self.term_start_date) < getdate(year.year_start_date):
            frappe.throw(_("The start of the term cannot be before the start of the linked academic year. The start of the academic year {0} has been set to {1}.  Please adjust the dates").format(self.academic_year, year.year_start_date))

        # end of term can not be after end of academic year
        if self.term_end_date and getdate(year.year_end_date) and getdate(self.term_end_date) > getdate(year.year_end_date):
            frappe.throw(_("The end of the term cannot be after the end of the linked academic year.  The end of the academic year {0} has been set to {1}. Pleae adjust the dates.").format(self.academic_year, year.year_end_date))

    def on_update(self):
        if self.term_start_date and self.term_end_date:
            self.create_calendar_events()


    def validate_duplicate(self):
        term = frappe.db.sql("""select name from `tabAcademic Term` where academic_year= %s and term_name= %s and docstatus<2 and name != %s""", (self.academic_year, self.term_name, self.name))
        if term:
            frappe.throw(_("An academic term with this academic year {0} and this name {1} already exisit. Please adjust the name if necessary.").format(self.academic_year, self.term_name))

    def create_calendar_events(self):
        if self.at_start:
            start_at = frappe.get_doc("School Event", self.at_start)
            if getdate(start_at.starts_on) != getdate(self.term_start_date):
                start_at.db_set("starts_on", self.term_start_date)
                start_at.db_set("ends_on", self.term_start_date)
                frappe.msgprint(_("Date for the start of the term {0} has been updated on the School Event Calendar {1}").format(self.term_start_date, get_link_to_form("School Event", start_at.name)))

        if self.at_end:
            end_at = frappe.get_doc("School Event", self.at_end)
            if getdate(end_at.ends_on) != getdate(self.term_end_date):
                end_at.db_set("starts_on", self.term_end_date)
                end_at.db_set("ends_on", self.term_end_date)
                frappe.msgprint(_("Date for the end of the term {0} has been updated on the School Event Calendar {1}").format(self.term_end_date, get_link_to_form("School Event", end_at.name)))

        if not self.at_start:
            start_term = frappe.get_doc({
                "doctype": "School Event",
        	    "owner": frappe.session.user,
                "subject": "Start of the " + cstr(self.name) + " Academic Term",
                "starts_on": getdate(self.term_start_date),
                "ends_on": getdate(self.term_start_date),
                "school": self.school,
        	    "event_category": "Other",
        	    "event_type": "Public",
                "all_day": "1",
        	    "color": "#7575ff",
                "reference_type": "Academic Term",
                "reference_name": self.name
        	})
            start_term.insert()
            self.db_set("at_start", start_term.name)
            frappe.msgprint(_("Date for the start of the term {0} has been created on the School Event Calendar {1}").format(self.term_start_date, get_link_to_form("School Event", start_term.name)))

        if not self.at_end:
            end_term = frappe.get_doc({
                "doctype": "School Event",
                "owner": frappe.session.user,
        	    "subject": "End of the " + cstr(self.name) + " Academic Term",
        	    "starts_on": getdate(self.term_end_date),
        	    "ends_on": getdate(self.term_end_date),
                "school": self.school,
                "event_category": "Other",
                "event_type": "Public",
                "all_day": "1",
        	    "color": "#7575ff",
                "reference_type": "Academic Term",
                "reference_name": self.name
        	})
            end_term.insert()
            self.db_set("at_end", end_term.name)
            frappe.msgprint(_("Date for the end of the term {0} has been created on the School Event Calendar {1}").format(self.term_end_date, get_link_to_form("School Event", end_term.name)))
