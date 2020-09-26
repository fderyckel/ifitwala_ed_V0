# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, division
import frappe
from frappe import _

class OverlapError(frappe.ValidationError): pass

def validate_overlap_for(doc, doctype, fieldname, value=None):
	"""Checks overlap for specified field.
	:param fieldname: Checks Overlap for this field
	"""

	existing = get_overlap_for(doc, doctype, fieldname, value)
	if existing:
		frappe.throw(_("This {0} conflicts with {1} for {2} {3}").format(doc.doctype, existing.name,
			doc.meta.get_label(fieldname) if not value else fieldname , value or doc.get(fieldname)), OverlapError)

def get_overlap_for(doc, doctype, fieldname, value=None):
	"""Returns overlaping document for specified field.
	:param fieldname: Checks Overlap for this field
	"""

	existing = frappe.db.sql("""select name, from_time, to_time from `tab{0}`
		where `{1}`=%(val)s and schedule_date = %(schedule_date)s and
		(
			(from_time > %(from_time)s and from_time < %(to_time)s) or
			(to_time > %(from_time)s and to_time < %(to_time)s) or
			(%(from_time)s > from_time and %(from_time)s < to_time) or
			(%(from_time)s = from_time and %(to_time)s = to_time))
		and name!=%(name)s and docstatus!=2""".format(doctype, fieldname),
		{
			"schedule_date": doc.schedule_date,
			"val": value or doc.get(fieldname),
			"from_time": doc.from_time,
			"to_time": doc.to_time,
			"name": doc.name or "No Name"
		}, as_dict=True)

	return existing[0] if existing else None

def validate_duplicate_student(students):
	unique_students= []
	for stud in students:
		if stud.student in unique_students:
			frappe.throw(_("Student {0} - {1} appears Multiple times in row {2} & {3}")
				.format(stud.student, stud.student_name, unique_students.index(stud.student)+1, stud.idx))
		else:
			unique_students.append(stud.student)

		return None
	

# CMS - Course Management

# to return a list of all programs that can be displayed on the portal. 
def get_portal_programs(): 
	published_programs = frappe.get_all("Program", filter = {"is_published", True}) 
	if not published_programs: 
		return None
	program_list = [frappe.get_doc("Program", program) for program in published_programs] 
	portal_programs = [{"Program":program, 'has_access':allowed_program_access(program.name)} for program in program_list if allowed_porgram_access(program.name)]
	
	

# deciding if the current user is a student who has access to program or if it is a super-user
def allowed_program_access(program, student=None):
	if has_super_access():
		return True
	if not student:
		student = get_current_student()
	if student and get_enrollment('program', program, student.name):
		return True
	else:
		return False

# will display all programs and courses for users with certain roles.
def has_super_access():
	current_user = frappe.get_doc("User", frappe.session.user)
	roles = set([role.role for role in current_user.roles])
	return bool(roles & {"Administrator", "Instructor", "Curriculum Coordinator", "System Manager", "Academic Admin", "Schedule Maker", "School IT"}) 

# to get the name of the student who is currently logged-in
def get_current_student():
	email = frappe.session.user
	if email in ('Administrator', 'Guest'):
		return None
	try:
		student_id = frappe.get_all("Student", {"student_email_id": email}, ["name"])[0].name
		return frappe.get_doc("Student", student_id)
	except (IndexError, frappe.DoesNotExistError):
		return None

# for CMS get a list of all enrolled program and or course for the current academic year. 
def get_enrollment(master, document, student):
	current_year = frappe.get_single("Education Settings").get("current_academic_year")
	if master == 'program': 
		enrollments = frappe.get_all("Program Enrollment", filters={'student':student, 'program': document, 'docstatus': 1})
	#enrollments = frappe.get_all("Program Enrollment", filters={'student':student, 'program': document, 'docstatus': 1, 'academic_year':  current_year})
	if master == 'course': 
		enrollments = frappe.get_all("Course Enrollment", filters={'student':student, 'course': document, 'academic_year':  current_year})

	if enrollments:
		return enrollments[0].name
	else:
		return None

