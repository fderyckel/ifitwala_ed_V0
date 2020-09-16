// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt


frappe.treeview_settings['Employee'] = {
	get_tree_nodes: "ifitwala_dev.hr.doctype.employee.employee.get_children",
	filters: [
		{
			fieldname: "school",
			fieldtype:"Select",
			options: ['All Schools'].concat(ifitwala_dev.utils.get_tree_options("school")),
			label: __("Schools"),
			default: ifitwala_dev.utils.get_tree_default("school")
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
