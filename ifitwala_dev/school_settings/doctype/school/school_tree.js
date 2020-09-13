frappe.treeview_settings["School"] = {
	ignore_fields:["parent_school"],
	get_tree_nodes: 'ifitwala_dev.school_settings.doctype.school.school.get_children',
	add_tree_node: 'ifitwala_dev.school_settings.doctype.school.school.add_node',
	filters: [
		{
			fieldname: "school",
			fieldtype:"Link",
			options: "School",
			label: __("School"),
			get_query: function() {
				return {
					filters: [["School", 'is_group', '=', 1]]
				};
			}
		},
	],
	breadcrumb: "School Settings",
	root_label: "All Schools",
	get_tree_root: false,
	menu_items: [
		{
			label: __("New School"),
			action: function() {
				frappe.new_doc("School", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("School") !== -1'
		}
	],
	onload: function(treeview) {
		treeview.make_tree();
	}
};
