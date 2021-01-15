# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.wrapper import get_mapped_doc
import json


def get_student_group_students(student_group, include_inactive=0):
    """ Return the list of students from a student group
    """
    if include_inactive:
        students = frappe.get_list("Student Group Student", fields = ["student", "student_name"],
                filters = {"parent": student_group}, order_by = "group_roll_number")
    else:
        students = frappe.get_list("Student Group Student", fields = ["student", "student_name"],
                filters = {"parent": student_group, "active": 1}, order_by = "group_roll_number")

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
