# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

def get_data():
	return {
		'fieldname': 'program',
		'transactions': [
			{
				'label': _('Enrollment'),
				'items': ['Program Enrollment']
			},
			{
				'label': _('Student Activity'),
				'items': ['Student Group', 'Student Log']
			}
		]
	}
