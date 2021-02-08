# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

class ProgramEnrollmentTool(Document):

	# called by the button get_students on the form
	def get_students(self):
		students = []
		if not self.get_students_from:
			frappe.throw(_("Fill first the mandatory field: Get Students From.  Also fill, if not already done, Academic Year and Program."))
		elif not self.program:
			frappe.throw(_("Fill first the mandatory field: Program.  Also fill, if not already done, Program and Get Students From."))
		elif not self.academic_year:
			frappe.throw(_("Fill first the mandatory field: Academic Year.  Also fill, if not already done, Program and Get Students From."))

		else:
			condition1 = 'and academic_term=%(academic_term)s' if self.academic_term else " "
			if self.get_students_from == "Others":
				frappe.throw(_("Not yet developped. Choose another option"))
			elif self.get_students_from == "Program Enrollment":
				condition2 = 'and cohort=%(student_cohort)s' if self.student_cohort else " "
				students = frappe.db.sql('''select student, student_name, cohort AS student_cohort
					from
						`tabProgram Enrollment`
					where
						program=%(program)s and academic_year=%(academic_year)s {0} {1} and docstatus=1'''.format(condition1, condition2), self.as_dict(), as_dict = 1)

				# remove inactive students from students list.
				student_list = [d.student for d in students]
				if student_list:
					inactive_students = frappe.db.sql('''select name as student, student_full_name as student_name
					from
						`tabStudent`
					where
						name in (%s) and enabled = 0''' %
										', '.join(['%s']*len(student_list)), tuple(student_list), as_dict = 1)

					for student in students:
						if student.student in [d.student for d in inactive_students]:
							students.remove(student)
		if students:
			return students
		else:
			frappe.throw(_("There isn't any student enrolled for the mentioned academic year and program"))

	def enroll_students(self):
		total = len(self.students)	# note how this gives the length (number of row) of a child table
		term_start = frappe.get_doc("Academic Term", self.new_academic_term)
		year_start = frappe.get_doc("Academic Year", self.new_academic_year)
		enrdate = getdate(today())
		if self.new_academic_year:
			enrdate = getdate(year_start.year_start_date)
		if self.new_academic_term:
			enrdate = getdate(term_start.term_start_date)

		for i, stud in enumerate(self.students):
			frappe.publish_realtime("program_enrollment_tool", dict(progress = [i+1, total]), user = frappe.session.user)
			if stud.student:
				pe = frappe.new_doc("Program Enrollment")
				pe.student = stud.student
				pe.student_name = stud.student_name
				pe.cohort = stud.student_cohort if stud.student_cohort else self.new_student_cohort
				pe.program = self.new_program
				pe.academic_year = self.new_academic_year
				pe.academic_term = self.new_academic_term if self.new_academic_term else ""
				pe.enrollment_date = enrdate
				pe.save()
		frappe.msgprint(_("{0} students have been enrolled").format(total))
