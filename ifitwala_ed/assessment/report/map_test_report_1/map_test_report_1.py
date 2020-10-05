# Copyright (c) 2013, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	return columns, data

def get_columns(): 
	columns = [ 
		_("Academic Year") + ":Link/Academic Year:90", 
		_("Academic Term") + "Link/Academic Term::90", 
		_("Program") + "::90",
		_("Student") + "Link/Student::180",
		_("Math RIT") + "::50",
		_("Math Percentile") + "::50"		
	]
	return columns
