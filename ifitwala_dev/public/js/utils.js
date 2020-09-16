// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_dev");
frappe.provide("ifitwala_dev.utils");


$.extend(ifitwala_dev, {

});

$.extend(ifitwala_dev.utils, { 
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
	},
          
});
          
