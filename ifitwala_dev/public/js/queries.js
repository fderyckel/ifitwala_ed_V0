// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

// searches for enabled users
frappe.provide("ifitwala_dev.queries");
$.extend(ifitwala_dev.queries, { 
         user: function() { 
		 return { query: "frappe.core.doctype.user.user.user_query" };
	 }, 
	
	employee: function() {
		return { query: "erpnext.controllers.queries.employee_query" }
	},
         
         
