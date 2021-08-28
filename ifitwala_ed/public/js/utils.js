// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_ed");
frappe.provide("ifitwala_ed.utils");

$.extend(ifitwala_ed, {
	get_currency: function(organization) {
		if(!organization && cur_frm)
			organization = cur_frm.doc.organization;
		if(organization)
			return frappe.get_doc(":Organization", organization).default_currency || frappe.boot.sysdefaults.currency;
		else
			return frappe.boot.sysdefaults.currency;
	},

	get_presentation_currency_list: () => {
		const docs = frappe.boot.docs;
		let currency_list = docs.filter(d => d.doctype === ":Currency").map(d => d.name);
		currency_list.unshift("");
		return currency_list;
	},

	toggle_naming_series: function() {
		if(cur_frm.fields_dict.naming_series) {
			cur_frm.toggle_display("naming_series", cur_frm.doc.__islocal?true:false);
		}
	},

	hide_organization: function() {
		if(cur_frm.fields_dict.organization) {
			var companies = Object.keys(locals[":Organization"] || {});
			if(companies.length === 1) {
				if(!cur_frm.doc.organization) cur_frm.set_value("organization", companies[0]);
				cur_frm.toggle_display("organization", false);
			} else if(ifitwala_ed.last_selected_organization) {
				if(!cur_frm.doc.organization) cur_frm.set_value("organization", ifitwala_ed.last_selected_organization);
			}
		}
	},

	is_perpetual_inventory_enabled: function(organization) {
		if(organization) {
			return frappe.get_doc(":Organization", organization).enable_perpetual_inventory
		}
	},

	stale_rate_allowed: () => {
		return cint(frappe.boot.sysdefaults.allow_stale);
	},

	setup_serial_or_batch_no: function() {
		let grid_row = cur_frm.open_grid_row();
		if (!grid_row || !grid_row.grid_form.fields_dict.serial_no ||
			grid_row.grid_form.fields_dict.serial_no.get_status() !== "Write") return;

		frappe.model.get_value('Item', {'name': grid_row.doc.item_code},
			['has_serial_no', 'has_batch_no'], ({has_serial_no, has_batch_no}) => {
				Object.assign(grid_row.doc, {has_serial_no, has_batch_no});

				if (has_serial_no) {
					attach_selector_button(__("Add Serial No"),
						grid_row.grid_form.fields_dict.serial_no.$wrapper, this, grid_row);
				} else if (has_batch_no) {
					attach_selector_button(__("Pick Batch No"),
						grid_row.grid_form.fields_dict.batch_no.$wrapper, this, grid_row);
				}
			}
		);
	},

	route_to_adjustment_jv: (args) => {
		frappe.model.with_doctype('Journal Entry', () => {
			// route to adjustment Journal Entry to handle Account Balance and Stock Value mismatch
			let journal_entry = frappe.model.get_new_doc('Journal Entry');

			args.accounts.forEach((je_account) => {
				let child_row = frappe.model.add_child(journal_entry, "accounts");
				child_row.account = je_account.account;
				child_row.debit_in_account_currency = je_account.debit_in_account_currency;
				child_row.credit_in_account_currency = je_account.credit_in_account_currency;
				child_row.party_type = "" ;
			});
			frappe.set_route('Form','Journal Entry', journal_entry.name);
		});
	},

	proceed_save_with_reminders_frequency_change: () => {
		frappe.ui.hide_open_dialog();

		frappe.call({
			method: 'ifitwala_ed.hr.doctype.hr_settings.hr_settings.set_proceed_with_frequency_change',
			callback: () => {
				cur_frm.save();
			}
		});
	}
});

$.extend(ifitwala_ed.utils, {
	set_party_dashboard_indicators: function(frm) {
		if(frm.doc.__onload && frm.doc.__onload.dashboard_info) {
			var organization_wise_info = frm.doc.__onload.dashboard_info;
			if(organization_wise_info.length > 1) {
				organization_wise_info.forEach(function(info) {
					ifitwala_ed.utils.add_indicator_for_multiorganization(frm, info);
				});
			} else if (organization_wise_info.length === 1) {
				frm.dashboard.add_indicator(__('Annual Billing: {0}',
					[format_currency(organization_wise_info[0].billing_this_year, organization_wise_info[0].currency)]), 'blue');
				frm.dashboard.add_indicator(__('Total Unpaid: {0}',
					[format_currency(organization_wise_info[0].total_unpaid, organization_wise_info[0].currency)]),
				organization_wise_info[0].total_unpaid ? 'orange' : 'green');

				if(organization_wise_info[0].loyalty_points) {
					frm.dashboard.add_indicator(__('Loyalty Points: {0}',
						[organization_wise_info[0].loyalty_points]), 'blue');
				}
			}
		}
	},

	add_indicator_for_multiorganization: function(frm, info) {
		frm.dashboard.stats_area.removeClass('hidden');
		frm.dashboard.stats_area_row.addClass('flex');
		frm.dashboard.stats_area_row.css('flex-wrap', 'wrap');

		var color = info.total_unpaid ? 'orange' : 'green';

		var indicator = $('<div class="flex-column col-xs-6">'+
			'<div style="margin-top:10px"><h6>'+info.organization+'</h6></div>'+

			'<div class="badge-link small" style="margin-bottom:10px"><span class="indicator blue">'+
			'Annual Billing: '+format_currency(info.billing_this_year, info.currency)+'</span></div>'+

			'<div class="badge-link small" style="margin-bottom:10px">'+
			'<span class="indicator '+color+'">Total Unpaid: '
			+format_currency(info.total_unpaid, info.currency)+'</span></div>'+


			'</div>').appendTo(frm.dashboard.stats_area_row);

		if(info.loyalty_points){
			$('<div class="badge-link small" style="margin-bottom:10px"><span class="indicator blue">'+
			'Loyalty Points: '+info.loyalty_points+'</span></div>').appendTo(indicator);
		}

		return indicator;
	},

	get_party_name: function(party_type) {
		var dict = {'Customer': 'customer_name', 'Supplier': 'supplier_name', 'Employee': 'employee_name',
			'Member': 'member_name'};
		return dict[party_type];
	},

	copy_value_in_all_rows: function(doc, dt, dn, table_fieldname, fieldname) {
		var d = locals[dt][dn];
		if(d[fieldname]){
			var cl = doc[table_fieldname] || [];
			for(var i = 0; i < cl.length; i++) {
				if(!cl[i][fieldname]) cl[i][fieldname] = d[fieldname];
			}
		}
		refresh_field(table_fieldname);
	},

	add_dimensions: function(report_name, index) {
		let filters = frappe.query_reports[report_name].filters;

		frappe.call({
			method: "ifitwala_ed.accounting.doctype.accounting_dimension.accounting_dimension.get_dimensions",
			callback: function(r) {
				let accounting_dimensions = r.message[0];
				accounting_dimensions.forEach((dimension) => {
					let found = filters.some(el => el.fieldname === dimension['fieldname']);

					if (!found) {
						filters.splice(index, 0, {
							"fieldname": dimension["fieldname"],
							"label": __(dimension["label"]),
							"fieldtype": "Link",
							"options": dimension["document_type"]
						});
					}
				});
			}
		});
	},

	/**
	* Checks if the first row of a given child table is empty
	* @param child_table - Child table Doctype
	* @return {Boolean}
	**/
	first_row_is_empty: function(child_table){
		if($.isArray(child_table) && child_table.length > 0) {
			return !child_table[0].item_code;
		}
		return false;
	},

	/**
	* Removes the first row of a child table if it is empty
	* @param {_Frm} frm - The current form
	* @param {String} child_table_name - The child table field name
	* @return {Boolean}
	**/
	remove_empty_first_row: function(frm, child_table_name){
		const rows = frm['doc'][child_table_name];
		if (this.first_row_is_empty(rows)){
			frm['doc'][child_table_name] = rows.splice(1);
		}
		return rows;
	},

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
	overrides_parent_value_in_all_rows: function(doc, dt, dn, table_fieldname, fieldname, parent_fieldname) {
		if (doc[parent_fieldname]) {
			let cl = doc[table_fieldname] || [];
			for (let i = 0; i < cl.length; i++) {
				cl[i][fieldname] = doc[parent_fieldname];
			}
			frappe.refresh_field(table_fieldname);
		}
	},
	create_new_doc: function (doctype, update_fields) {
		frappe.model.with_doctype(doctype, function() {
			var new_doc = frappe.model.get_new_doc(doctype);
			for (let [key, value] of Object.entries(update_fields)) {
				new_doc[key] = value;
			}
			frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
		});
	}

});

ifitwala_ed.utils.map_current_doc = function(opts) {
	function _map() {
		if($.isArray(cur_frm.doc.items) && cur_frm.doc.items.length > 0) {
			// remove first item row if empty
			if(!cur_frm.doc.items[0].item_code) {
				cur_frm.doc.items = cur_frm.doc.items.splice(1);
			}

			// find the doctype of the items table
			var items_doctype = frappe.meta.get_docfield(cur_frm.doctype, 'items').options;

			// find the link fieldname from items table for the given
			// source_doctype
			var link_fieldname = null;
			frappe.get_meta(items_doctype).fields.forEach(function(d) {
				if(d.options===opts.source_doctype) link_fieldname = d.fieldname; });

			// search in existing items if the source_name is already set and full qty fetched
			var already_set = false;
			var item_qty_map = {};

			$.each(cur_frm.doc.items, function(i, d) {
				opts.source_name.forEach(function(src) {
					if(d[link_fieldname]==src) {
						already_set = true;
						if (item_qty_map[d.item_code])
							item_qty_map[d.item_code] += flt(d.qty);
						else
							item_qty_map[d.item_code] = flt(d.qty);
					}
				});
			});

			if(already_set) {
				opts.source_name.forEach(function(src) {
					frappe.model.with_doc(opts.source_doctype, src, function(r) {
						var source_doc = frappe.model.get_doc(opts.source_doctype, src);
						$.each(source_doc.items || [], function(i, row) {
							if(row.qty > flt(item_qty_map[row.item_code])) {
								already_set = false;
								return false;
							}
						})
					})

					if(already_set) {
						frappe.msgprint(__("You have already selected items from {0} {1}",
							[opts.source_doctype, src]));
						return;
					}

				})
			}
		}

		return frappe.call({
			// Sometimes we hit the limit for URL length of a GET request
			// as we send the full target_doc. Hence this is a POST request.
			type: "POST",
			method: 'frappe.model.mapper.map_docs',
			args: {
				"method": opts.method,
				"source_names": opts.source_name,
				"target_doc": cur_frm.doc,
				"args": opts.args
			},
			callback: function(r) {
				if(!r.exc) {
					var doc = frappe.model.sync(r.message);
					cur_frm.dirty();
					cur_frm.refresh();
				}
			}
		});
	}

	let query_args = {};
	if (opts.get_query_filters) {
		query_args.filters = opts.get_query_filters;
	}

	if (opts.get_query_method) {
		query_args.query = opts.get_query_method;
	}

	if (query_args.filters || query_args.query) {
		opts.get_query = () => query_args;
	}

	if (opts.source_doctype) {
		const d = new frappe.ui.form.MultiSelectDialog({
			doctype: opts.source_doctype,
			target: opts.target,
			date_field: opts.date_field || undefined,
			setters: opts.setters,
			get_query: opts.get_query,
			add_filters_group: 1,
			action: function(selections, args) {
				let values = selections;
				if(values.length === 0){
					frappe.msgprint(__("Please select {0}", [opts.source_doctype]))
					return;
				}
				opts.source_name = values;
				opts.setters = args;
				d.dialog.hide();
				_map();
			},
		});

		return d;
	}

	if (opts.source_name) {
		opts.source_name = [opts.source_name];
		_map();
	}
}

frappe.form.link_formatters['Employee'] = function(value, doc) {
	if(doc && doc.employee_full_name && doc.employee_full_name !== value) {
		return value? value + ': ' + doc.employee_full_name: doc.employee_full_name;
	} else {
		return value;
	}
};

// add description on posting time
$(document).on('app_ready', function() {
	if(!frappe.datetime.is_timezone_same()) {
		$.each(["Stock Reconciliation", "Stock Entry", "Stock Ledger Entry",
			"Delivery Note", "Purchase Receipt", "Sales Invoice"], function(i, d) {
			frappe.ui.form.on(d, "onload", function(frm) {
				cur_frm.set_df_property("posting_time", "description",
					frappe.sys_defaults.time_zone);
			});
		});
	}
});


function attach_selector_button(inner_text, append_loction, context, grid_row) {
	let $btn_div = $("<div>").css({"margin-bottom": "10px", "margin-top": "10px"})
		.appendTo(append_loction);
	let $btn = $(`<button class="btn btn-sm btn-default">${inner_text}</button>`)
		.appendTo($btn_div);

	$btn.on("click", function() {
		context.show_serial_batch_selector(grid_row.frm, grid_row.doc, "", "", true);
	});
}
