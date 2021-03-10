# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ifitwala_ed.utils as utils

no_cache = 1

def get_context(context):
	try:
		program = frappe.form_dict['program']
		course_name = frappe.form_dict['name']
	except KeyError:
		frappe.local.flags.redirect_location = '/cms'
		raise frappe.Redirect

	context.education_settings = frappe.get_single("Education Settings")
	course = frappe.get_doc('Course', course_name)
	context.program = program
	context.course = course

	context.units = course.get_learning_units()
	context.has_program_access = utils.allowed_program_access(context.program)
	context.has_access =  utils.allowed_course_access(context.course)
