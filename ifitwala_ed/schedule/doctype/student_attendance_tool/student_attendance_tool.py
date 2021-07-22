# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StudentAttendanceTool(Document):
	pass

@frappe.whitelist()
def get_student_attendance_records(based_on, date=None, student_group=None, course_schedule=None):
	pass
