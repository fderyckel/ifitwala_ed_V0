// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.views.calendar['School Calendar'] = {
  field_map: {
    start: 'holiday_date',
    end: 'holiday_date',
    id: 'name',
    title: 'description',
    allDay: 'allDay',
    eventColor: 'color'
  },
  order_by: 'from_date',
  get_events_method: 'ifitwala_ed.school_settings.doctype.school_calendar.school_calendar.get_events',
  filters: [
    {
      'fieldtype': 'Link',
      'fieldname': 'academic_year',
      'options': 'Academic Year',
      'label': __('Academic Year')
    }
  ]
}; 
