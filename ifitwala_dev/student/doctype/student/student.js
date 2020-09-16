// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student', {
	
	setup: function(frm) {
		frm.add_fetch('guardian', 'guardian_name', 'guardian_name');
		frm.add_fetch('student', 'title', 'full_name');
		frm.add_fetch('student', 'gender', 'gender');
		frm.add_fetch('student', 'date_of_birth', 'date_of_birth');

		frm.set_query('student', 'siblings', function(doc) {
			return {
				'filters': {
					'name': ['!=', doc.name]
				}
			};
		})
	},
	
	refresh: function(frm) {

    }
});

// in student guardian child table, do filter out already present guardian. 
frappe.ui.form.on('Student Guardian', {
	guardians_add: function(frm){
		frm.fields_dict['guardians'].grid.get_field('guardian').get_query = function(doc){
			let guardian_list = [];
			if(!doc.__islocal) guardian_list.push(doc.guardian);
			$.each(doc.guardians, function(idx, val){
				if (val.guardian) guardian_list.push(val.guardian);
			});
			return { filters: [['Guardian', 'name', 'not in', guardian_list]] };
		};
	}
});
