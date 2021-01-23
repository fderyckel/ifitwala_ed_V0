# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import getdate, get_link_to_form

class ProgramEnrollment(Document):

	def validate(self):
		self.validate_duplicate_course()
		self.validate_duplication()
		if not self.student_name:
			self.student_name = frappe.db.get_value("Student", self.student, "student_full_name")
		if not self.courses:
			self.extend("courses", self.get_courses())

		if self.academic_term:
			term_dates = frappe.get_doc("Academic Term", self.academic_term)
			if term_dates.academic_year != self.academic_year:
				frappe.throw(_("The term does not belong to that academic year."))
			if self.enrollment_date and getdate(term_dates.term_start_date) and getdate(self.enrollment_date) < getdate(term_dates.term_start_date):
				frappe.throw(_("The enrollment date for this program is before the start of the term.  Please revise the date or change the term {0}.").format(get_link_to_form("Academic Term", self.academic_term)))
			if self.enrollment_date and getdate(term_dates.term_end_date) and getdate(self.enrollment_date) > getdate(term_dates.term_end_date):
				frappe.throw(_("The enrollment date for this program is after the end the term.  Pease revise the joining date or change the term {0}.").format(get_link_to_form("Academic Term", self.academic_term)))

	def on_submit(self):
		self.update_student_joining_date()
		self.create_course_enrollment()

	# you cannot enrolled twice for a same program, same year, same term.
	def validate_duplication(self):
		enrollment = frappe.get_all("Program Enrollment", filters = {
			"student": self.student,
			"academic_year": self.academic_year,
			"academic_term": self.academic_term,
			"program": self.program,
			"docstatus": ("<", 2),
			"name": ("!=", self.name)
		})
		if enrollment:
			frappe.throw(_("This student is already enrolled in this program for this term."))

	# If a student is in a program and that program has required courses (non elective), then these courses are loaded automatically.
	def get_courses(self):
		return frappe.db.sql("""select course from `tabProgram Course` where parent = %s and required = 1""", (self.program), as_dict=1)

	def validate_duplicate_course(self):
		found = []
		pc = frappe.get_list("Program Course", fields = ["Course"], filters = [["parent", "=", self.program]])
		pc_list = [c.Course for c in pc]
		for course in self.courses:
			if course.course in found:
				frappe.throw(_("Course {0} entered twice.").format(course.course))
			elif course.course in pc_list:
				frappe.throw(_("Course {0} is not part of program {1}").format(get_link_to_form("Course", course.course), get_link_to_form("Program", self.program)))
			else:
				found.append(course.course)

	# This will update the joining date on the student doctype in function of the joining date of the program.
	def update_student_joining_date(self):
		date = frappe.db.sql("""select min(enrollment_date) from `tabProgram Enrollment` where student= %s""", self.student)
		frappe.db.set_value("Student", self.student, "student_joining_date", date)

	def create_course_enrollment(self):
		program = frappe.get_doc("Program", self.program)
		student = frappe.get_doc("Student", self.student)
		course_list = [course.course for course in self.courses]
		for course_name in course_list:
			student.enroll_in_course(course_name=course_name, program_enrollment=self.name, enrollment_date = self.enrollment_date)

	# used (later) below with quiz and assessment
	def get_all_course_enrollments(self):
		course_enrollment_names = frappe.get_list("Course Enrollment", filters={'program_enrollment': self.name})
		return [frappe.get_doc('Course Enrollment', course_enrollment.name) for course_enrollment in course_enrollment_names]



# from JS. to filter out course that are only present in the program list of courses.
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_program_courses(doctype, txt, searchfield, start, page_len, filters):
	#if not filters.get('program'):
	#	frappe.msgprint(_("Please select a Program first."))
	#	return []

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

# from JS to filter out students that have already been enrolled for a given year and/or term
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_students(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("academic_term"):
		filters["academic_term"] = frappe.defaults.get_defaults().academic_term

	if not filters.get("academic_year"):
		filters["academic_year"] = frappe.defaults.get_defaults().academic_year

	enrolled_students = frappe.get_list("Program Enrollment", filters={
		"academic_term": filters.get('academic_term'),
		"academic_year": filters.get('academic_year')
	}, fields=["student"])

	students = [d.student for d in enrolled_students] if enrolled_students else [""]

	return frappe.db.sql("""select
			name, student_full_name from tabStudent
		where
			name not in (%s)
		and
			`%s` LIKE %s
		order by
			idx desc, name
		limit %s, %s"""%(
			", ".join(['%s']*len(students)), searchfield, "%s", "%s", "%s"),
			tuple(students + ["%%%s%%" % txt, start, page_len]
		)
	)
