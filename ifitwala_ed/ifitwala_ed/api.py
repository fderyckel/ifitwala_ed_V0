# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
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
