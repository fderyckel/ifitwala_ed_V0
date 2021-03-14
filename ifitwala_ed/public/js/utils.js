// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_ed");
frappe.provide("ifitwala_ed.utils");

$.extend(ifitwala_ed, {
	get_presentation_currency_list: () => {
		const docs = frappe.boot.docs;
		let currency_list = docs.filter(d => d.doctype === ":Currency").map(d => d.name);
		currency_list.unshift("");
		return currency_list;
	},
	is_perpetual_inventory_enabled: function(school) {
		if(school) {
			return frappe.get_doc(":School", school).enable_perpetual_inventory
		}
	}
});

$.extend(ifitwala_ed.utils, {
	get_tree_options: function(option) {
		// get valid options for tree based on user permission & locals dict
		let unscrub_option = frappe.model.unscrub(option);
		let user_permission = frappe.defaults.get_user_permissions();
		let options;

		if(user_permission && user_permission[unscrub_option]) {
			options = user_permission[unscrub_option].map(perm => perm.doc);
		} else {
			options = $.map(locals[`:${unscrub_option}`], function(c) { return c.name; }).sort();
		}
		// filter unique values, as there may be multiple user permissions for any value
		return options.filter((value, index, self) => self.indexOf(value) === index);
	},

	get_tree_default: function(option) {
		// set default for a field based on user permission
		let options = this.get_tree_options(option);
		if(options.includes(frappe.defaults.get_default(option))) {
			return frappe.defaults.get_default(option);
		} else {
			return options[0];
		}
	} 

});

frappe.form.link_formatters['Employee'] = function(value, doc) {
	if(doc && doc.employee_full_name && doc.employee_full_name !== value) {
		return value? value + ': ' + doc.employee_full_name: doc.employee_full_name;
	} else {
		return value;
	}
}
