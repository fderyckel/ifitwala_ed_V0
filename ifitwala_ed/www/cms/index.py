# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ifitwala_ed.utils import utils 

no_cache = 1

#always get context first for portal
def get_context(context): 
        context.education_settings = frappe.get_single("Education Settings") 
        if not context.education_settings.enable_cms: 
                frappe.local.flags.redirect_location = '/' 
                raise.frappe.Redirect
                
        context.featured_programs = get_featured_programs() 
        
def get_featured_programs(): 
        return utils.get_portal_programs()
  
  
