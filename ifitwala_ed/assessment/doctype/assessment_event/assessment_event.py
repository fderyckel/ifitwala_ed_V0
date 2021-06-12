# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class AssessmentEvent(Document):
	def validate(self):
		self.validate_max_score()
		#self.validate_assessment_criteria()

	def validate_max_score(self):
		max_score = 0
		for d in self.assessment_event_criteria:
			max_score += d.maximum_points
		if max_score != self.maximum_points:
			frappe.throw(_("The sum of the scores of the assessment critera should be {0} and it appears to be {1}").format(self.maximum_points, max_score))

	#def validate_assessment_criteria(self):
	#	assessment_criteria_list = frappe.db.sql("""
	#		SELECT aec.assessment_criteria
	#		FROM `tabAssessment Event` ae, `tabAssessment Event Criteria` aec
	#		WHERE ae.name = aec.parent AND ae.course = %s AND ae.student_group = %s"""(self.course, self.student_group))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_courses(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get('program'):
		frappe.msgprint(_("Please select a Program first."))
		return []

	return frappe.db.sql("""
			SELECT course, course_name
			FROM `tabProgram Course`
			WHERE parent = %(program)s and course like %(txt)s {match_cond}
		order by
			if(locate(%(_txt)s, course), locate(%(_txt)s, course), 99999),
			idx desc,
			`tabProgram Course`.course asc
		limit {start}, {page_len}""".format(
			match_cond=get_match_cond(doctype),
			start=start,
			page_len=page_len), {
				"txt": "%{0}%".format(txt),
				"_txt": txt.replace('%', ''),
				"program": filters['program']
			})
