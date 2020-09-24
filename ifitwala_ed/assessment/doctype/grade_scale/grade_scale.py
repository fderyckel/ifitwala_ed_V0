# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _ 
from frappe.utils import cint 
from frappe.model.document import Document

class GradeScale(Document): 
	def validate(self): 
		boundary_intervals = [] 
		for d in self.boundaries: 
			if d.boundary_interval in boundary_intervals: 
				frappe.throw(_("Boundary {0} appears more than once. Please change boundary.").format(d.boundary_interval)) 
			else: 
				boundary_intervals.append(cint(d.boundary_interval))
				
		if 0 not in boundary_intervals: 
			frappe.throw(_("Please define grade for 0.")) 
			
		#if self.maximum_grade not in boundary_intervals: 
		#	frappe.throw(_("You need to define your maximum grade of {0} in the boundary interval.").format(self.maximum_grade))
				
	

