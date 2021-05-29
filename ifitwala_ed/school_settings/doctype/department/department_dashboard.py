# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'department',
		'transactions': [
			{
				'label': _('Meetings'),
				'items': ['Meeting']
			},
			{
				'label': _('Newsletter'),
				'items': ['Newsletter']
			}
		]
	}
