# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_years, date_diff, nowdate
from frappe.model.document import Document

class StudentApplicant(Document):
	def validate(self):
		self.validate_dates()

	def on_update_after_submit(self):
		student = frappe.get_doc("Student", filters = {"student_applicant", self.name})
		if student:
			frappe.throw(_("You cannot change fields as student {0} is linked with application {1}").format(get_link_to_form("Student", student[0].name), self.name))

	def validate_dates(self):
		if self.date_of_birth and getdate(self.date_of_birth) >= getdate():
			frappe.throw(_("The date of birth {0} cannot be after today.  Please adjust the dates.").format(self.date_of_birth))

		self.title = " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

		if self.student_admission and self.program and self.date_of_birth:
			self.validate_admission_age()

	def validate_admission_age(self):
		student_admission = get_student_admission_data(self.student_admission, self.program)
		if student_admission and student_admission.cutoff_birthdate and getdate(self.date_of_birth) > getdate(student_admission.cutoff_birthdate):
			frappe.throw(_("{0} is not eligible for admission to this program as per date of birth.").format(self.title))
		if student_admission and student_admission.maximum_age and date_diff(nowdate(), add_years(get_date(self.date_of_birth), student_admission.maximum_age)) > 0:
			frappe.throw(_("{0} is not eligible for admission to this program as per date of birth.").format(self.title))


def get_student_admission_data(student_admission, program):
	student_admission = frappe.db.sql("""select sa.admission_start_date, sa.admission_end_date,
	 		sap.program, sap.cutoff_birthdate, sap.maximum_age
			from `tabStudent Admission` sa, `tabStudent Admission Program`sap
			where sa.name = sap.parent and sa.name = %s and sap.program = %s """, (student_admission, program), as_dict=1)

	if student_admission:
		return student_admission[0]

	else:
		return None
