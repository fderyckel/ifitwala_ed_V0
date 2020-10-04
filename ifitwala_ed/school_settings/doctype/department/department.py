# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Department(Document):
	
	def autoname(self): 
		self.name = self.department_name + " - {}".format(self.school_abbreviation) if self.school_abbreviation else ""
	
	def validate(self): 
		# You cannot have 2 dpt. of the same within the same school. OK in 2 different school. 
		self.validate_duplicate() 
		self.title = self.department_name + " - {}".format(self.school_abbreviation) if self.school_abbreviation else "" 
		found = [] 
		for member in self.members: 
			if member.employee in found: 
				frappe.throw(_("You have already added the employee {0} to the Department. Please remove it.").format(member.employee))
			found.append(member.employee)
	
	def validate_duplicate(self): 
    		dpt = frappe.db.sql("""select name from `tabDepartment` where school= %s and department_name= %s and docstatus<2 and name != %s""", (self.school, self.department_name, self.name))
    		if dpt: 
       			frappe.throw(_("An department within this school {0} and this name {1} already exisit. Please adjust the name as necessary.").format(self.school, self.department_name))

		
