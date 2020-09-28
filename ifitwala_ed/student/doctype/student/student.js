// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student', {
	
	setup: function(frm) {
		frm.add_fetch('guardian', 'guardian_name', 'guardian_name');
		frm.add_fetch('student', 'student_full_name', 'sibling_name');
		frm.add_fetch('student', 'student_gender', 'sibling_gender');
		frm.add_fetch('student', 'student_date_of_birth', 'sibling_date_of_birth');

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
		frm.fields_dict['student_guardians'].grid.get_field('guardian').get_query = function(doc){
			let guardian_list = [];
			if(!doc.__islocal) guardian_list.push(doc.guardian);
			$.each(doc.student_guardians, function(idx, val){
				if (val.guardian) guardian_list.push(val.guardian);
			});
			return { filters: [['Guardian', 'name', 'not in', guardian_list]] };
		};
	}
});

// in student sibling child table, do filter out already present siblings. 
frappe.ui.form.on('Student Sibling', {
	siblings_add: function(frm){
		frm.fields_dict['siblings'].grid.get_field('student').get_query = function(doc){
			let sibling_list = [frm.doc.name];
			$.each(doc.siblings, function(idx, val){
				if (val.student) sibling_list.push(val.student);
			});
			return { filters: [['Student', 'name', 'not in', sibling_list]] };
		};
	}
});
