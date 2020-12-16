# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ifitwala_ed"
app_title = "Ifitwala ed"
app_publisher = "ifitwala"
app_description = "manage student data"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "f.deryckel@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/ifitwala_ed/css/ifitwala_ed.css"
app_include_js = "/assets/ifitwala_ed/js/ifitwala_ed.js"

# include js, css files in header of web template
web_include_css = "/assets/ifitwala_ed/css/ifitwala_ed.css"
web_include_js = "/assets/ifitwala_ed/js/ifitwala_ed.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

update_website_context  = ["ifitwala_ed.school_settings.doctype.education_settings.education_settings.update_website_context"]

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "ifitwala_ed.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ifitwala_ed.install.before_install"
after_install = "ifitwala_ed.setup.setup_education"


calendars = [ "Holiday List", "Course Schedule", "School Calendar"]
# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ifitwala_ed.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

#permission_query_conditions = {
# 	"Meeting": "ifitwala_ed.school_settings.doctype.meeting.meeting.meeting_has_permission",
# }
#
#has_permission = {
# 	"Meeting": "ifitwala_ed.school_settings.doctype.meeting.meeting.meeting_has_permission",
#}

default_roles = [
	{'role': 'Student', 'doctype':'Student', 'email_field': 'student_email'},
]

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {

	"User": {
		"after_insert": "frappe.contacts.doctype.contact.contact.update_contact"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ifitwala_ed.tasks.all"
# 	],
# 	"daily": [
# 		"ifitwala_ed.tasks.daily"
# 	],
# 	"hourly": [
# 		"ifitwala_ed.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ifitwala_ed.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ifitwala_ed.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "ifitwala_ed.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ifitwala_ed.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ifitwala_ed.task.get_dashboard_data"
# }
