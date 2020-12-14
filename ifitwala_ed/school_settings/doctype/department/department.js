// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {
	}

});

// to filter out Department Members that have already been picked out.
frappe.ui.form.on('Department Member', {
	members_add: function(frm){
		frm.fields_dict['members'].grid.get_field('member').get_query = function(doc){
			var user_list = [];
			if(!doc.__islocal) user_list.push(doc.name);
			$.each(doc.members, function(idx, val){
				if (val.member) user_list.push(val.member);
			});
			return { filters: [['User', 'name', 'not in', user_list]] };
		};
	}
});
