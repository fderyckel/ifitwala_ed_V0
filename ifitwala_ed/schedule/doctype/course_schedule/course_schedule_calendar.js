// Copyright (c) 2020, ifitwala and contributors
// For license information, please see license.txt

frappe.views.calendar['Course Schedule'] = {
  field_map:{
    start: 'from_datetime',
    end: 'to_datetime',
    id:  'name',
    title: 'course',
    allDay: 'allDay'
  },
  gantt: false,
  order_by: 'schedule_date',
  get_events_method: 'ifitwala_ed.schedule.doctype.course_schedule.course_schedule.get_course_schedule_events',
  filters: [
    {
      "fieldtype": "Link",
      "fieldname": "student_group",
      "options": "Student Group",
      "label": __("Student Group")
    },
    {
      "fieldtype": "Link",
      "fieldname": "course",
      "options": "Course",
      "label": __("Course")
    },
    {
      "fieldtype": "Link",
      "fieldname": "instructor",
      "options": "Instructor",
      "label": __("Instructor")
    },
    {
      "fieldtype": "Link",
      "fieldname": "room",
      "options": "Room",
      "label": __("Room")
    }
  ]

}
