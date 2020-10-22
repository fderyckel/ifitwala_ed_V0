# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'program_enrollment',
		'transactions': [
			{
				'label': _('Course'),
				'items': ['Course Enrollment']
			}
		]
	}
