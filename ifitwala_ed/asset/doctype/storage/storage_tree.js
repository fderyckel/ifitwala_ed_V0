// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.treeview_settings['Storage'] = {
	get_tree_nodes: "ifitwala_ed.asset.doctype.storage.storage.get_children",
	add_tree_node: "ifitwala_ed.asset.doctype.storage.storage.add_node",
	get_tree_root: false,
	root_label: "Storages",
	filters: [{
		fieldname: "school",
		fieldtype:"Select",
		options: ifitwala_ed.utils.get_tree_options("school"),
		label: __("School"),
		default: ifitwala_ed.utils.get_tree_default("school")
	}],
	fields:[
		{fieldtype:'Data', fieldname: 'storage_name',
			label:__('New Storage Name'), reqd:true},
		{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
			description: __("Child nodes can be only created under 'Group' type nodes")}
	],
	ignore_fields:["parent_storage"],
	onrender: function(node) {
		if (node.data && node.data.balance!==undefined) {
			$('<span class="balance-area pull-right">'
			+ format_currency(Math.abs(node.data.balance), node.data.school_currency)
			+ '</span>').insertBefore(node.$ul);
		}
	}
}
