// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("ifitwala_ed.organization");

frappe.ui.form.on("Organization", {
	onload: function(frm) {
		if (frm.doc.__islocal && frm.doc.parent_organization) {
			frappe.db.get_value('Organization', frm.doc.parent_organization, 'is_group', (r) => {
				if (!r.is_group) {
					frm.set_value('parent_organization', '');
				}
			});
		}
	},
	setup: function(frm) {
		ifitwala_ed.organization.setup_queries(frm);
		frm.set_query("parent_organization", function() {
			return {
				filters: {"is_group": 1}
			}
		});
	},

	organization_name: function(frm) {
		if(frm.doc.__islocal) {
			// add missing " " arg in split method
			let parts = frm.doc.organization_name.split(" ");
			let abbr = $.map(parts, function (p) {
				return p? p.substr(0, 1) : null;
			}).join("");
			frm.set_value("abbr", abbr);
		}
	},

	parent_organization: function(frm) {
		var bool = frm.doc.parent_organization ? true : false;
		frm.set_value('create_chart_of_accounts_based_on', bool ? "Existing Organization" : "");
		frm.set_value('existing_organization', bool ? frm.doc.parent_organization : "");
		disbale_coa_fields(frm, bool);
	},

	date_of_commencement: function(frm) {
		if(frm.doc.date_of_commencement<frm.doc.date_of_incorporation) {
			frappe.throw(__("Date of Commencement should be greater than Date of Incorporation"));
		}

		if(!frm.doc.date_of_commencement) {
			frm.doc.date_of_incorporation = ""
		}
	},

	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.doc.abbr && frm.set_df_property("abbr", "read_only", 1);
			frm.set_df_property("parent_organization", "read_only", 1);
			disbale_coa_fields(frm);
		}

		frm.toggle_display('address_html', !frm.doc.__islocal);
		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);

			frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Organization'}

			frm.toggle_enable("default_currency", (frm.doc.__onload &&
				!frm.doc.__onload.transactions_exist));

			if (frm.has_perm('write')) {
				frm.add_custom_button(__('Create Tax Template'), function() {
					frm.trigger("make_default_tax_template");
				});
			}

			if (frappe.perm.has_perm("Cost Center", 0, 'read')) {
				frm.add_custom_button(__('Cost Centers'), function() {
					frappe.set_route('Tree', 'Cost Center', {'organization': frm.doc.name});
				}, __("View"));
			}

			if (frappe.perm.has_perm("Account", 0, 'read')) {
				frm.add_custom_button(__('Chart of Accounts'), function() {
					frappe.set_route('Tree', 'Account', {'organization': frm.doc.name});
				}, __("View"));
			}

			if (frappe.perm.has_perm("Sales Taxes and Charges Template", 0, 'read')) {
				frm.add_custom_button(__('Sales Tax Template'), function() {
					frappe.set_route('List', 'Sales Taxes and Charges Template', {'organization': frm.doc.name});
				}, __("View"));
			}

			if (frappe.perm.has_perm("Purchase Taxes and Charges Template", 0, 'read')) {
				frm.add_custom_button(__('Purchase Tax Template'), function() {
					frappe.set_route('List', 'Purchase Taxes and Charges Template', {'organization': frm.doc.name});
				}, __("View"));
			}

			if (frm.has_perm('write')) {
				frm.add_custom_button(__('Default Tax Template'), function() {
					frm.trigger("make_default_tax_template");
				}, __('Create'));
			}
		}

		ifitwala_ed.organization.set_chart_of_accounts_options(frm.doc);

		if (!frappe.user.has_role('System Manager')) {
			frm.get_field("delete_organization_transactions").hide();
		}
	},

	make_default_tax_template: function(frm) {
		frm.call({
			method: "create_default_tax_template",
			doc: frm.doc,
			freeze: true,
			callback: function() {
				frappe.msgprint(__("Default tax templates for sales, purchase and items are created."));
			}
		})
	},

	country: function(frm) {
		ifitwala_ed.organization.set_chart_of_accounts_options(frm.doc);
	},

});


ifitwala_ed.organization.set_chart_of_accounts_options = function(doc) {
	var selected_value = doc.chart_of_accounts;
	if(doc.country) {
		return frappe.call({
			method: "ifitwala_ed.accounting.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country",
			args: {
				"country": doc.country,
				"with_standard": true
			},
			callback: function(r) {
				if(!r.exc) {
					set_field_options("chart_of_accounts", [""].concat(r.message).join("\n"));
					if(in_list(r.message, selected_value))
						cur_frm.set_value("chart_of_accounts", selected_value);
				}
			}
		})
	}
}

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
			method: "ifitwala_ed.setup.doctype.organization.organization.enqueue_replace_abbr",
			args: {
				"organization": cur_frm.doc.name,
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

ifitwala_ed.organization.setup_queries = function(frm) {
	$.each([
		["default_bank_account", {"account_type": "Bank"}],
		["default_cash_account", {"account_type": "Cash"}],
		["default_receivable_account", {"account_type": "Receivable"}],
		["default_payable_account", {"account_type": "Payable"}],
		["default_expense_account", {"root_type": "Expense"}],
		["default_income_account", {"root_type": "Income"}],
		["default_payroll_payable_account", {"root_type": "Liability"}],
		["round_off_account", {"root_type": "Expense"}],
		["write_off_account", {"root_type": "Expense"}],
		["discount_allowed_account", {"root_type": "Expense"}],
		["discount_received_account", {"root_type": "Income"}],
		["exchange_gain_loss_account", {"root_type": "Expense"}],
		["unrealized_exchange_gain_loss_account", {"root_type": "Expense"}],
		["accumulated_depreciation_account", {"root_type": "Asset", "account_type": "Accumulated Depreciation"}],
		["depreciation_expense_account", {"root_type": "Expense", "account_type": "Depreciation"}],
		["disposal_account", {"report_type": "Profit and Loss"}],
		["default_inventory_account", {"account_type": "Stock"}],
		["cost_center", {}],
		["round_off_cost_center", {}],
		["depreciation_cost_center", {}],
		["default_employee_advance_account", {"root_type": "Asset"}],
		["expenses_included_in_asset_valuation", {"account_type": "Expenses Included In Asset Valuation"}],
		["capital_work_in_progress_account", {"account_type": "Capital Work in Progress"}],
		["asset_received_but_not_billed", {"account_type": "Asset Received But Not Billed"}],
		["unrealized_profit_loss_account", {"root_type": "Liability"}]
	], function(i, v) {
		ifitwala_ed.organization.set_custom_query(frm, v);
	});

	if (frm.doc.enable_perpetual_inventory) {
		$.each([
			["stock_adjustment_account", {"root_type": "Expense", "account_type": "Stock Adjustment"}],
			["expenses_included_in_valuation", {"root_type": "Expense", "account_type": "Expenses Included in Valuation"}],
			["stock_received_but_not_billed", {"root_type": "Liability", "account_type": "Stock Received But Not Billed"}],
			["service_received_but_not_billed", {"root_type": "Liability", "account_type": "Service Received But Not Billed"}],
		], function(i, v) {
			ifitwala_ed.organization.set_custom_query(frm, v);
		});
	}
}

ifitwala_ed.organization.set_custom_query = function(frm, v) {
	var filters = {
		"organization": frm.doc.name,
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
	frm.set_df_property("existing_organization", "read_only", bool);
}
