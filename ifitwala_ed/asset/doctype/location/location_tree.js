// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.treeview_settings['Location'] = {
	get_tree_nodes: "ifitwala_ed.asset.doctype.location.location.get_children",
	add_tree_node: "ifitwala_ed.asset.doctype.location.location.add_node",
	get_tree_root: false,
	root_label: "Locations",
	filters: [{
		fieldname: "organization",
		fieldtype:"Select",
		options: ifitwala_ed.utils.get_tree_options("organization"),
		label: __("Organization"),
		default: ifitwala_ed.utils.get_tree_default("organization")
	}],
	fields:[
		{fieldtype:'Data', fieldname: 'location_name',
			label:__('New Location Name'), reqd:true},
		{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
			description: __("Child nodes can be only created under 'Group' type nodes")}
	],
	ignore_fields:["parent_location"],
	onrender: function(node) {
		if (node.data && node.data.balance!==undefined) {
			$('<span class="balance-area pull-right">'
			+ format_currency(Math.abs(node.data.balance), node.data.organization_currency)
			+ '</span>').insertBefore(node.$ul);
		}
	}
}
