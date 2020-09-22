# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'academic_year',
		'transactions': [
			{
				'label': _('Student'),
				'items': ['Student Group', 'Student Log']
			},
			{
				'label': _('Academic Term and Program'),
				'items': ['Academic Term', 'Program Enrollment']
			}
		]
	}
