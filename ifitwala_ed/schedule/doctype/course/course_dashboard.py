# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'course',
		'transactions': [
			{
				'label': _('Student'),
				'items': ['Student Group']
			},
			{
				'label': _('Program and Course'),
				'items': ['Program', 'Course Enrollment', 'Course Schedule']
			},
			{
				'label': _('Curriculum'),
				'items': ['Learning Unit']
			} 						
		]
	}
