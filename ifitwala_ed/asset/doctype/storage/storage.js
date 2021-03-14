// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Storage', {
	refresh: function(frm) {
    frm.toggle_display('storage_name', frm.doc.__islocal);
    frm.toggle_enable(['is_group', 'school'], false);

		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Storage'};

		frm.fields_dict['parent_storage'].get_query = function(doc) {
			return {
				filters: {
					"is_group": 1,
				}
			}
		}

		frm.fields_dict['account'].get_query = function(doc) {
			return {
				filters: {
					"is_group": 0,
					"account_type": "Stock",
					"school": frm.doc.school
				}
			}
		}
	}
});
