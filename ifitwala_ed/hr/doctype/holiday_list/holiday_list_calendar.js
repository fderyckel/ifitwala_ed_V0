// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.views.calendar['Holiday List'] = {
  field_map:{
    start: 'holiday_date',
    end: 'holiday_date',
    id:  'name',
    title: 'description',
    allDay: 'allDay'
  },
  order_by: 'from_date', 
  gantt: true,
  get_events_method: 'ifitwala_ed.hr.doctype.holiday_list.holiday_list.get_events',
  filters: [
		{
			'fieldtype': 'Link',
			'fieldname': 'holiday_list',
			'options': 'Holiday List',
			'label': __('Holiday List')
		}
	]
}
