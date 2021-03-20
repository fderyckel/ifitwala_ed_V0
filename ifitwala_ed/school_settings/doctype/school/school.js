// Copyright (c) 2020, flipo and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_ed.school");

frappe.ui.form.on('School', {
	onload: function(frm) {
		if (frm.doc.__islocal && frm.doc.parent_school) {
			frappe.db.get_value('School', frm.doc.parent_school, 'is_group', (r) => {
				if (!r.is_group) {
					frm.set_value('parent_school', '');
				}
			});
		}
	},

	setup: function(frm) {
		ifitwala_ed.school.setup_queries(frm);
		frm.set_query("parent_school", function() {
			return {
				filters: {"is_group": 1}
			}
		);

	},

	school_name: function(frm) {
		if(frm.doc.__islocal) {
			let parts = frm.doc.school_name.split();
			let abbr = $.map(parts, function (p) {
				return p? p.substr(0, 1) : null;
			}).join("");
			frm.set_value("abbr", abbr);
		}
	},

	parent_school: function(frm) {
		var bool = frm.doc.parent_school ? true : false;
		frm.set_value('create_chart_of_accounts_based_on', bool ? "Existing School" : "");
		frm.set_value('existing_school', bool ? frm.doc.parent_school : "");
		disbale_coa_fields(frm, bool);
	},

	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.doc.abbr && frm.set_df_property("abbr", "read_only", 1);
			frm.set_df_property("parent_school", "read_only", 1);
			disbale_coa_fields(frm);
		}

		frm.toggle_display('address_html', !frm.doc.__islocal);
		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);
		}
	}
});

cur_frm.cscript.change_abbr = function() {
	var dialog = new frappe.ui.Dialog({
		title: "Replace Abbr",
		fields: [
			{"fieldtype": "Data", "label": "New Abbreviation", "fieldname": "new_abbr",
				"reqd": 1 },
			{"fieldtype": "Button", "label": "Update", "fieldname": "update"},
		]
	});



	dialog.fields_dict.update.$input.click(function() {
		var args = dialog.get_values();
		if(!args) return;
		frappe.show_alert(__("Update in progress. It might take a while."));
		return frappe.call({
			method: "ifitwala_ed.school_settings.doctype.school.school.enqueue_replace_abbr",
			args: {
				"school": cur_frm.doc.name,
				"old": cur_frm.doc.abbr,
				"new": args.new_abbr
			},
			callback: function(r) {
				if(r.exc) {
					frappe.msgprint(__("There were errors."));
					return;
				} else {
					cur_frm.set_value("abbr", args.new_abbr);
				}
				dialog.hide();
				cur_frm.refresh();
			},
			btn: this
		})
	});
	dialog.show();
}



ifitwala_ed.school.setup_queries = function(frm) {
	$.each([
		["default_bank_account", {"account_type": "Bank"}],
		["default_cash_account", {"account_type": "Cash"}],
		["default_receivable_account", {"account_type": "Receivable"}],
		["default_payable_account", {"account_type": "Payable"}],
		["default_expense_account", {"root_type": "Expense"}],
		["default_income_account", {"root_type": "Income"}],
		["round_off_account", {"root_type": "Expense"}],
		["write_off_account", {"root_type": "Expense"}],
		["exchange_gain_loss_account", {"root_type": "Expense"}],
		["unrealized_exchange_gain_loss_account", {"root_type": "Expense"}],
		["accumulated_depreciation_account", {"root_type": "Asset", "account_type": "Accumulated Depreciation"}],
		["depreciation_expense_account", {"root_type": "Expense", "account_type": "Depreciation"}],
		["disposal_account", {"report_type": "Profit and Loss"}],
		["default_inventory_account", {"account_type": "Stock"}],
		["cost_center", {}],
		["round_off_cost_center", {}],
		["depreciation_cost_center", {}],
		["expenses_included_in_asset_valuation", {"account_type": "Expenses Included In Asset Valuation"}],
		["capital_work_in_progress_account", {"account_type": "Capital Work in Progress"}],
		["asset_received_but_not_billed", {"account_type": "Asset Received But Not Billed"}],
		["unrealized_profit_loss_account", {"root_type": "Liability"}]
	], function(i, v) {
		ifitwala_ed.school.set_custom_query(frm, v);
	});

	if (frm.doc.enable_perpetual_inventory) {
		$.each([
			["stock_adjustment_account",
				{"root_type": "Expense", "account_type": "Stock Adjustment"}],
			["expenses_included_in_valuation",
				{"root_type": "Expense", "account_type": "Expenses Included in Valuation"}],
			["stock_received_but_not_billed",
				{"root_type": "Liability", "account_type": "Stock Received But Not Billed"}],
			["service_received_but_not_billed",
				{"root_type": "Liability", "account_type": "Service Received But Not Billed"}],

		], function(i, v) {
			ifitwala_ed.school.set_custom_query(frm, v);
		});
	}
}

ifitwala_ed.school.set_custom_query = function(frm, v) {
	var filters = {
		"school": frm.doc.name,
		"is_group": 0
	};

	for (var key in v[1]) {
		filters[key] = v[1][key];
	}

	frm.set_query(v[0], function() {
		return {
			filters: filters
		}
	});
}

var disbale_coa_fields = function(frm, bool=true) {
	frm.set_df_property("create_chart_of_accounts_based_on", "read_only", bool);
	frm.set_df_property("chart_of_accounts", "read_only", bool);
	frm.set_df_property("existing_school", "read_only", bool);
}
