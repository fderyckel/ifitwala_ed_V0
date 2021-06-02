// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.treeview_settings['Employee'] = {
	get_tree_nodes: "ifitwala_ed.hr.doctype.employee.employee.get_children",
	filters: [
		{
			fieldname: "organization",
			fieldtype:"Select",
			options: ['All Organizations'].concat(ifitwala_ed.utils.get_tree_options("organization")),
			label: __("Organization"),
			default: ifitwala_ed.utils.get_tree_default("organization")
		}
	],
	breadcrumb: "Hr",
	disable_add_node: true,
	get_tree_root: false,
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				frappe.set_route("Form", "Employee", node.data.value);
			}
		}
	],
	menu_items: [
		{
			label: __("New Employee"),
			action: function() {
				frappe.new_doc("Employee", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Employee") !== -1'
		}
	],
};
