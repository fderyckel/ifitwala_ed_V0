# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.email.doctype.email_group.email_group import add_subscribers
import json


@frappe.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	""" Return the list of students from a student group"""
	if include_inactive:
		students = frappe.get_list("Student Group Student", fields = ["student", "student_name"], filters = {"parent": student_group}, order_by = "group_roll_number")
	else:
		students = frappe.get_list("Student Group Student", fields = ["student", "student_name"], filters = {"parent": student_group, "active": 1}, order_by = "group_roll_number")

	return students

@frappe.whitelist()
def get_student_guardians(student):
	""" Return the list of guardians from that student"""
	guardians = frappe.get_list("Student Guardian", fields = ["guardian"], filters = {"parent": student})
	return guardians

@frappe.whitelist()
def enroll_student(source_name):
    frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
    student = get_mapped_doc("Student Applicant", source_name, {"Student Applicant": {"doctype": "Student", "field_map": {"name": "student_applicant"}}}, ignore_permissions = True)
    student.save()
    program_enrollment = frappe.new_doc("Program Enrollment")
    program_enrollment.student = student.name
    program_enrollment.student_name = student.title
    program_enrollment.program = frappe.db.get_value("Student Applicant", source_name, "program")
    frappe.publish_realtime('enroll_student_progress', {"progress": [2, 4]}, user=frappe.session.user)
    return program_enrollment

@frappe.whitelist()
def update_email_group(doctype, name):
    if not frappe.db.exists("Email Group", name+"|students"):
        s_mail_group = frappe.new_doc("Email Group")
        s_mail_group.title = name+"|students"
        s_mail_group.save()
    if not frappe.db.exists("Email Group", name+"|guardians"):
        g_mail_group = frappe.new_doc("Email Group")
        g_mail_group.title = name+"|guardians"
        g_mail_group.save()
    student_mail_list = []
    guardian_mail_list = []
    students = []
    if doctype == "Student Group":
        students = get_student_group_students(name)
    for student in students:
        s_mail = frappe.get_value("Student", student.student, "student_email")
        if s_mail:
            student_mail_list.append(s_mail)
        for guardian in get_student_guardians(student.student):
            g_mail = frappe.get_value("Guardian", guardian.guardian, "guardian_email")
            if g_mail:
                guardian_mail_list.append(g_mail)
    add_subscribers(name+"|students", student_mail_list)
    add_subscribers(name+"|guardians", guardian_mail_list)

@frappe.whitelist()
def get_assessment_criteria(course):
	return frappe.get_list('Course Assessment Criteria', fields = ['assessment_criteria', "criteria_weighting"], filters = {"parent": course}, order_by = "idx")
