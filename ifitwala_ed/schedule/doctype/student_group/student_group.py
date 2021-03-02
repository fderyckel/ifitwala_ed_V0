# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from ifitwala_ed.utils import validate_duplicate_student

class StudentGroup(Document):
	def autoname(self):
		if self.group_based_on == "Course" or self.group_based_on == "Activity":
			self.name = self.student_group_abbreviation + "/" + self.academic_term
		else:
			self.name = self.student_group_abbreviation + "/" + self.cohort

	def validate(self):
		self.validate_term()
		self.validate_course()
		self.validate_mandatory_fields()
		self.validate_size()
		self.validate_students()
		self.validate_and_set_child_table_fields()
		validate_duplicate_student(self.students)
		if self.group_based_on == "Course" or self.group_based_on == "Activity":
			self.title = self.student_group_abbreviation + "/" + self.academic_term
		else:
			self.title = self.student_group_abbreviation + "/" + self.cohort

	def validate_term(self):
		term_year = frappe.get_doc("Academic Term", self.academic_term)
		if self.academic_year != term_year.academic_year:
			frappe.throw(_("The term {0} does not belong to the academic year {1}.").format(self.academic_term, self.academic_year))

	def validate_course(self):
		courses = frappe.get_all("Program Course", fields = ["course_name"], filters = {"parent":self.program})
		course_list = [course.course_name for course in courses]
		if self.course not in course_list:
			frappe.throw(_("{0} is not part of the {1} Program. Either select a different coures or the appropriate program.").format(self.course, get_link_to_form("Program", self.program)))

	def validate_mandatory_fields(self):
		if self.group_based_on == "Course" and not self.course:
			frappe.throw(_("Please select a course."))
		if self.group_based_on == "Cohort" and not self.cohort:
			frappe.throw(_("Please select a cohort."))
		if self.group_based_on == "Course" and not self.program:
			frappe.throw(_("Please select a program"))

	# Throwing message if more students than maximum size in the group
	def validate_size(self):
		if cint(self.maximum_size) < 0:
			frappe.throw(_("Max number of student in this group cannot be negative."))
		if self.maximum_size and len(self.students) > cint(self.maximum_size):
			frappe.throw(_("You can only enroll {0} students in this group.").format(self.maximum_size))

	# you should not be able to make a group that include inactive students.
	# this is to ensure students are still active students (aka not graduated or not transferred, etc.)
	def validate_students(self):
		program_enrollment = get_program_enrollment(self.academic_year, self.academic_term, self.program, self.cohort, self.course)
		students = [d.student for d in program_enrollment] if program_enrollment else []
		for d in self.students:
			if not frappe.db.get_value("Student", d.student, "enabled") and d.active and not self.disabled:
				frappe.throw(_("{0} - {1} is inactive student".format(d.group_roll_number, d.student_name)))

	# to input the roll number field in child table
	def validate_and_set_child_table_fields(self):
		roll_numbers = [d.group_roll_number for d in self.students if d.group_roll_number]
		max_roll_no = max(roll_numbers) if roll_numbers else 0
		roll_no_list = []
		for d in self.students:
			if not d.student_name:
				d.student_name = frappe.db.get_value("Student", d.student, "student_full_name")
			if not d.group_roll_number:
				max_roll_no += 1
				d.group_roll_number = max_roll_no
			if d.group_roll_number in roll_no_list:
				frappe.throw(_("Duplicate roll number for student {0}").format(d.student_name))
			else:
				roll_no_list.append(d.group_roll_number)

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	current_user = frappe.get_doc("User", frappe.session.user)
	roles = [role.role for role in current_user.roles]

	if "Student" in roles:
		return """(name in (select parent from `tabStudent Group Student` where user_id=%(user)s))""" % {
			"user": frappe.db.escape(user),
			}

	if "Instructor" in roles:
		return """(name in (select parent from `tabStudent Group Instructor` where user_id=%(user)s))""" % {
				"user": frappe.db.escape(user),
				}
	super_viewer = ["Administrator", "Curriculum Coordinator", "System Manager", "Academic Admin", "Schedule Maker"]
	for role in roles:
		if role in super_viewer:
			return ""


def group_has_permission(user=None, doc):
	current_user = frappe.get_doc("User", user)
	roles = [role.role for role in current_user.roles]
	super_viewer = ["Administrator", "Curriculum Coordinator", "System Manager", "Academic Admin", "Schedule Maker", "Admission Officer"]
	for role in roles:
		if role in super_viewer:
			return True

	if current_user.name in [s.user_id for s in doc.students]:
		return True

	if current_user.name in [i.user_id for i in doc.instructors]:
		return True

	return False

@frappe.whitelist()
def get_students(academic_year, group_based_on, academic_term=None, program=None, cohort=None, course=None):
	enrolled_students = get_program_enrollment(academic_year, academic_term, program, cohort, course)

	if enrolled_students:
		student_list = []
		for s in enrolled_students:
			if frappe.db.get_value("Student", s.student, "enabled"):
				s.update({"active": 1})
			else:
				s.update({"active": 0})
			student_list.append(s)
		return student_list
	else:
		frappe.msgprint(_("No students found"))
		return []



def get_program_enrollment(academic_year, academic_term=None, program=None, cohort=None, course=None):

	condition1 = " "
	condition2 = " "
	if academic_term:
		condition1 += " and pe.academic_term = %(academic_term)s"
	if program:
		condition1 += " and pe.program = %(program)s"
	if cohort:
		condition1 += " and pe.cohort = %(cohort)s"
	if course:
		condition1 += " and pe.name = pec.parent and pec.course = %(course)s"
		condition2 = ", `tabProgram Enrollment Course` pec"

	return frappe.db.sql('''
		select
			pe.student, pe.student_name
		from
			`tabProgram Enrollment` pe {condition2}
		where
			pe.academic_year = %(academic_year)s  {condition1} and pe.docstatus=1
		order by
			pe.student_name asc
		'''.format(condition1=condition1, condition2=condition2),
		({"academic_year": academic_year, "academic_term":academic_term, "program": program, "cohort": cohort, "course": course}), as_dict=1)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def fetch_students(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("group_based_on") != "Activity":
		enrolled_students = get_program_enrollment(filters.get('academic_year'), filters.get('academic_term'),
			filters.get('program'), filters.get('cohort'))
		student_group_student = frappe.db.sql_list('''select student from `tabStudent Group Student` where parent=%s''',
			(filters.get('student_group')))
		students = ([d.student for d in enrolled_students if d.student not in student_group_student]
			if enrolled_students else [""]) or [""]
		return frappe.db.sql("""select name, student_full_name from tabStudent
			where name in ({0}) and (`{1}` LIKE %s or student_full_name LIKE %s)
			order by idx desc, name
			limit %s, %s""".format(", ".join(['%s']*len(students)), searchfield),
			tuple(students + ["%%%s%%" % txt, "%%%s%%" % txt, start, page_len]))
	else:
		return frappe.db.sql("""select name, student_full_name from tabStudent
			where `{0}` LIKE %s or student_full_name LIKE %s
			order by idx desc, name
			limit %s, %s""".format(searchfield),
			tuple(["%%%s%%" % txt, "%%%s%%" % txt, start, page_len]))
