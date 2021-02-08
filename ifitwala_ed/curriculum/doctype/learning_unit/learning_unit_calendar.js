// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.views.calendar['Learning Unit'] = {
  field_map: {
    start: 'start_date',
    end: 'end_date',
    id: 'name',
    title: 'unit_name',
    allDay: 'allDay'
  },
  gantt: true,
  filters: [
    {
      'fieldtype': 'Link',
      'fieldname': 'course',
      'options': 'Course',
      'label': __('Course')
    },
    {
      'fieldtype': 'Link',
      'fieldname': 'program',
      'options': 'Program',
      'label': __('Program')
    }
  ]
};
