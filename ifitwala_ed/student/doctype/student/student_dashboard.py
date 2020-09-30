# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'student',
		'transactions': [
			{
				'label': _('Admission'),
				'items': ['Program Enrollment', 'Course Enrollment']
			},
			{
				'label': _('Student Activity'),
				'items': ['Student Log', 'Student Group']
			},
			{
				'label': _('Assessment'),
				'items': ['MAP Test']
			}
		]
	}
