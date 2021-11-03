frappe.pages['organizational-chart'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Organizational Chart',
		single_column: true
	});
}