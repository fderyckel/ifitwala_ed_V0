// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.views.calendar['Staff Calendar'] = {
  field_map: {
    start: 'holiday_date',
    end: 'holiday_date',
    id:  'name',
    title: 'description',
    allDay: 'allDay'
  },
  order_by: 'from_date',
  get_events_method: 'ifitwala_ed.hr.doctype.holiday_list.holiday_list.get_events',
  filters: [
		{
			'fieldtype': 'Link',
			'fieldname': 'holiday_list',
			'options': 'Staff Calendar',
			'label': __('Staff Calendar')
		}
	]
}
