# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils  import getdate, get_link_to_form
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.document import Document

class LearningUnit(Document):
	def validate(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("The start of the unit {0} cannot be after its end {1}.  Please adjust the dates").format(self.start_date, self.end_date))
		if self.program and self.course:
			courses = frappe.get_list("Program Course", fields = ["course_name"], filters = {"parent": self.program})
			course_list = [course.course_name for course in courses]
			if self.course not in course_list:
				frappe.throw(_("Course {0} not part of program {1}. Select Course and Program appropriately.").format(self.course, get_link_to_form("Program", self.program)))


@frappe.whitelist()
def add_lu_to_courses(lu, courses, mandatory=False):
	courses = json.loads(courses)
	for c in courses:
		course = frappe.get_doc("Course", c)
		course.append("units", {"learning_unit": lu})
		course.flags.ignore_mandatory = True
		course.save()
	frappe.db.commit()
	frappe.msgprint(_("Learning Unit {0} has been added to the selected courses successfully.").format(frappe.bold(lu)), title = _("Course updated"), indicator = "green")

# use as a filter to choose which potential courses one can add a given LU to
@frappe.whitelist()
def get_courses_without_given_lu(lu):
	courses = []
	for c in frappe.get_all("Course", filters = {"status": "Active"}):
		course = frappe.get_doc("Course", c.name)
		units = [u.learning_unit for u in course.units]
		if not units or lu not in units:
			courses.append(course.name)
	return courses


# from JS. to filter out course that are only present in the program list of courses.
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_courses(doctype, txt, searchfield, start, page_len, filters):
	if filters.get('program'):
		return frappe.db.sql("""select course, course_name from `tabProgram Course`
			where  parent = %(program)s and course like %(txt)s {match_cond}
			order by
				if(locate(%(_txt)s, course), locate(%(_txt)s, course), 99999),
				idx desc,
				`tabProgram Course`.course asc
			limit {start}, {page_len}""".format(
				match_cond=get_match_cond(doctype),
				start=start,
				page_len=page_len), {
					"txt": "%{0}%".format(txt),
					"_txt": txt.replace('%', ''),
					"program": filters['program']
				})
