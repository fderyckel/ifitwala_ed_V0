// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

// searches for enabled users
frappe.provide("erpnext.queries");
$.extend(erpnext.queries, { 
         user: function() {
		          return { query: "frappe.core.doctype.user.user.user_query" };
         }, 
         
         
