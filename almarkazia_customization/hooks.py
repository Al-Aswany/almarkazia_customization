app_name = "almarkazia_customization"
app_title = "Almarkazia Customization"
app_publisher = "Mahmoud Hussein"
app_description = "app for Almarkazia Customization"
app_email = "mahmudhussain2001ab@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "almarkazia_customization",
# 		"logo": "/assets/almarkazia_customization/logo.png",
# 		"title": "Almarkazia Customization",
# 		"route": "/almarkazia_customization",
# 		"has_permission": "almarkazia_customization.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/almarkazia_customization/css/almarkazia_customization.css"
# app_include_js = "/assets/almarkazia_customization/js/almarkazia_customization.js"

# include js, css files in header of web template
# web_include_css = "/assets/almarkazia_customization/css/almarkazia_customization.css"
# web_include_js = "/assets/almarkazia_customization/js/almarkazia_customization.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "almarkazia_customization/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "almarkazia_customization/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "almarkazia_customization.utils.jinja_methods",
# 	"filters": "almarkazia_customization.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "almarkazia_customization.install.before_install"
# after_install = "almarkazia_customization.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "almarkazia_customization.uninstall.before_uninstall"
# after_uninstall = "almarkazia_customization.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "almarkazia_customization.utils.before_app_install"
# after_app_install = "almarkazia_customization.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "almarkazia_customization.utils.before_app_uninstall"
# after_app_uninstall = "almarkazia_customization.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "almarkazia_customization.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "almarkazia_customization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"almarkazia_customization.tasks.all"
# 	],
# 	"daily": [
# 		"almarkazia_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"almarkazia_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"almarkazia_customization.tasks.weekly"
# 	],
# 	"monthly": [
# 		"almarkazia_customization.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "almarkazia_customization.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "almarkazia_customization.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "almarkazia_customization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "almarkazia_customization.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["almarkazia_customization.utils.before_request"]
# after_request = ["almarkazia_customization.utils.after_request"]

# Job Events
# ----------
# before_job = ["almarkazia_customization.utils.before_job"]
# after_job = ["almarkazia_customization.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"almarkazia_customization.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

