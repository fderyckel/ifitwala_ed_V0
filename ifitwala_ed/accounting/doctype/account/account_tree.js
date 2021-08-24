// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.provide("frappe.treeview_settings")

frappe.treeview_settings["Account"] = {
	breadcrumb: "Accounts",
	title: __("Chart of Accounts"),
	get_tree_root: false,
	filters: [
		{
			fieldname: "organization",
			fieldtype:"Select",
			options: ifitwala_ed.utils.get_tree_options("organization"),
			label: __("Organization"),
			default: ifitwala_ed.utils.get_tree_default("organization"),
			on_change: function() {
				var me = frappe.treeview_settings['Account'].treeview;
				var organization = me.page.fields_dict.organization.get_value();
				if (!organization) {
					frappe.throw(__("Please set a Organization"));
				}
				frappe.call({
					method: "ifitwala_ed.accounts.doctype.account.account.get_root_organization",
					args: {
						organization: organization,
					},
					callback: function(r) {
						if(r.message) {
							let root_organization = r.message.length ? r.message[0] : "";
							me.page.fields_dict.root_organization.set_value(root_organization);

							frappe.db.get_value("Organization", {"name": organization}, "allow_account_creation_against_child_organization", (r) => {
								frappe.flags.ignore_root_organization_validation = r.allow_account_creation_against_child_organization;
							});
						}
					}
				});
			}
		},
		{
			fieldname: "root_organization",
			fieldtype:"Data",
			label: __("Root Organization"),
			hidden: true,
			disable_onchange: true
		}
	],
	root_label: "Accounts",
	get_tree_nodes: 'ifitwala_ed.accounts.utils.get_children',
	add_tree_node: 'ifitwala_ed.accounts.utils.add_ac',
	menu_items:[
		{
			label: __('New Organization'),
			action: function() { frappe.new_doc("Organization", true) },
			condition: 'frappe.boot.user.can_create.indexOf("Organization") !== -1'
		}
	],
	fields: [
		{fieldtype:'Data', fieldname:'account_name', label:__('New Account Name'), reqd:true,
			description: __("Name of new Account. Note: Please don't create accounts for Customers and Suppliers")},
		{fieldtype:'Data', fieldname:'account_number', label:__('Account Number'),
			description: __("Number of new Account, it will be included in the account name as a prefix")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
			description: __('Further accounts can be made under Groups, but entries can be made against non-Groups')},
		{fieldtype:'Select', fieldname:'root_type', label:__('Root Type'),
			options: ['Asset', 'Liability', 'Equity', 'Income', 'Expense'].join('\n'),
			depends_on: 'eval:doc.is_group && !doc.parent_account'},
		{fieldtype:'Select', fieldname:'account_type', label:__('Account Type'),
			options: frappe.get_meta("Account").fields.filter(d => d.fieldname=='account_type')[0].options,
			description: __("Optional. This setting will be used to filter in various transactions.")
		},
		{fieldtype:'Float', fieldname:'tax_rate', label:__('Tax Rate'),
			depends_on: 'eval:doc.is_group==0&&doc.account_type=="Tax"'},
		{fieldtype:'Link', fieldname:'account_currency', label:__('Currency'), options:"Currency",
			description: __("Optional. Sets organization's default currency, if not specified.")}
	],
	ignore_fields:["parent_account"],
	onload: function(treeview) {
		frappe.treeview_settings['Account'].treeview = {};
		$.extend(frappe.treeview_settings['Account'].treeview, treeview);
		function get_organization() {
			return treeview.page.fields_dict.organization.get_value();
		}

		// tools
		treeview.page.add_inner_button(__("Chart of Cost Centers"), function() {
			frappe.set_route('Tree', 'Cost Center', {organization: get_organization()});
		}, __('View'));

		treeview.page.add_inner_button(__("Opening Invoice Creation Tool"), function() {
			frappe.set_route('Form', 'Opening Invoice Creation Tool', {organization: get_organization()});
		}, __('View'));

		treeview.page.add_inner_button(__("Period Closing Voucher"), function() {
			frappe.set_route('List', 'Period Closing Voucher', {organization: get_organization()});
		}, __('View'));


		treeview.page.add_inner_button(__("Journal Entry"), function() {
			frappe.new_doc('Journal Entry', {organization: get_organization()});
		}, __('Create'));
		treeview.page.add_inner_button(__("Organization"), function() {
			frappe.new_doc('Organization');
		}, __('Create'));

		// financial statements
		for (let report of ['Trial Balance', 'General Ledger', 'Balance Sheet',
			'Profit and Loss Statement', 'Cash Flow Statement', 'Accounts Payable', 'Accounts Receivable']) {
			treeview.page.add_inner_button(__(report), function() {
				frappe.set_route('query-report', report, {organization: get_organization()});
			}, __('Financial Statements'));
		}

	},
	post_render: function(treeview) {
		frappe.treeview_settings['Account'].treeview["tree"] = treeview.tree;
		treeview.page.set_primary_action(__("New"), function() {
			let root_organization = treeview.page.fields_dict.root_organization.get_value();

			if(root_organization) {
				frappe.throw(__("Please add the account to root level Organization - ") + root_organization);
			} else {
				treeview.new_node();
			}
		}, "add");
	},
	onrender: function(node) {
		if (frappe.boot.user.can_read.indexOf("GL Entry") !== -1) {

			// show Dr if positive since balance is calculated as debit - credit else show Cr
			let balance = node.data.balance_in_account_currency || node.data.balance;
			let dr_or_cr = balance > 0 ? "Dr": "Cr";

			if (node.data && node.data.balance!==undefined) {
				$('<span class="balance-area pull-right">'
					+ (node.data.balance_in_account_currency ?
						(format_currency(Math.abs(node.data.balance_in_account_currency),
							node.data.account_currency) + " / ") : "")
					+ format_currency(Math.abs(node.data.balance), node.data.organization_currency)
					+ " " + dr_or_cr
					+ '</span>').insertBefore(node.$ul);
			}
		}
	},
	toolbar: [
		{
			label:__("Add Child"),
			condition: function(node) {
				return frappe.boot.user.can_create.indexOf("Account") !== -1
					&& (!frappe.treeview_settings['Account'].treeview.page.fields_dict.root_organization.get_value()
					|| frappe.flags.ignore_root_organization_validation)
					&& node.expandable && !node.hide_add;
			},
			click: function() {
				var me = frappe.treeview_settings['Account'].treeview;
				me.new_node();
			},
			btnClass: "hidden-xs"
		},
		{
			condition: function(node) {
				return !node.root && frappe.boot.user.can_read.indexOf("GL Entry") !== -1
			},
			label: __("View Ledger"),
			click: function(node, btn) {
				frappe.route_options = {
					"account": node.label,
					"from_date": frappe.sys_defaults.year_start_date,
					"to_date": frappe.sys_defaults.year_end_date,
					"organization": frappe.treeview_settings['Account'].treeview.page.fields_dict.organization.get_value()
				};
				frappe.set_route("query-report", "General Ledger");
			},
			btnClass: "hidden-xs"
		}
	],
	extend_toolbar: true
}
