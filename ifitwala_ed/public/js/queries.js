// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

// searches for enabled users
frappe.provide("ifitwala_ed.queries");
$.extend(ifitwala_ed.queries, {
         user: function() {
		 return { query: "frappe.core.doctype.user.user.user_query" };
	 },

	employee: function() {
		return { query: "ifitwala_ed.controllers.queries.employee_query" }
	},

	supplier: function() {
		return { query: "ifitwala_ed.controllers.queries.supplier_query" };
	},

	customer_filter: function(doc) {
		if(!doc.customer) {
			frappe.throw(__("Please set {0}", [__(frappe.meta.get_label(doc.doctype, "customer", doc.name))]));
		}

		return { filters: { customer: doc.customer } };
	},

	contact_query: function(doc) {
		if(frappe.dynamic_link) {
			if(!doc[frappe.dynamic_link.fieldname]) {
				frappe.throw(__("Please set {0}",
					[__(frappe.meta.get_label(doc.doctype, frappe.dynamic_link.fieldname, doc.name))]));
			}

			return {
				query: 'frappe.contacts.doctype.contact.contact.contact_query',
				filters: {
					link_doctype: frappe.dynamic_link.doctype,
					link_name: doc[frappe.dynamic_link.fieldname]
				}
			};
		}
	},

	address_query: function(doc) {
		if(frappe.dynamic_link) {
			if(!doc[frappe.dynamic_link.fieldname]) {
				frappe.throw(__("Please set {0}",
					[__(frappe.meta.get_label(doc.doctype, frappe.dynamic_link.fieldname, doc.name))]));
			}

			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: frappe.dynamic_link.doctype,
					link_name: doc[frappe.dynamic_link.fieldname]
				}
			};
		}
	},

	organization_address_query: function(doc) {
		return {
			query: 'frappe.contacts.doctype.address.address.address_query',
			filters: { is_your_organization_address: 1, link_doctype: 'Organization', link_name: doc.organization || '' }
		};
	},

	supplier_filter: function(doc) {
		if(!doc.supplier) {
			frappe.throw(__("Please set {0}", [__(frappe.meta.get_label(doc.doctype, "supplier", doc.name))]));
		}

		return { filters: { supplier: doc.supplier } };
	},


});
