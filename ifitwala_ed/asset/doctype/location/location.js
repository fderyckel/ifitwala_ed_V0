// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Location', {
	onload: function(frm) {
		frm.set_query("default_in_transit_warehouse", function() {
			return {
				filters:{
					'warehouse_type' : 'Transit',
					'is_group': 0,
					'company': frm.doc.company
				}
			};
		});
	},

	refresh: function(frm) {
    frm.toggle_display('location_name', frm.doc.__islocal);
		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}

    if (cint(frm.doc.is_group) == 1) {
			frm.add_custom_button(__('Group to Non-Group'),
				function() { convert_to_group_or_ledger(frm); }, 'fa fa-retweet', 'btn-default')
		} else if (cint(frm.doc.is_group) == 0) {
			frm.add_custom_button(__('Non-Group to Group'),
				function() { convert_to_group_or_ledger(frm); }, 'fa fa-retweet', 'btn-default')
		}

    frm.toggle_enable(['is_group', 'organization'], false);

		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Location'};

		frm.fields_dict['parent_location'].get_query = function(doc) {
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
					"organization": frm.doc.organization
				}
			}
		}
	}
});

function convert_to_group_or_ledger(frm){
	frappe.call({
		method:"ifitwala_ed.asset.doctype.location.location.convert_to_group_or_ledger",
		args: {
			docname: frm.doc.name,
			is_group: frm.doc.is_group
		},
		callback: function(){
			frm.refresh();
		}

	})
}
