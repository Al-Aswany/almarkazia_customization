from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)

	columns = get_columns(filters.view_type)
	data = get_data(filters)
	message = get_message(filters)
	report_summary = get_report_summary(filters)
	return columns, data, message, None, report_summary


def validate_filters(filters):
	for fieldname in ("company", "from_date", "to_date", "view_type"):
		if not filters.get(fieldname):
			frappe.throw(_("Filter {0} is required").format(frappe.bold(_(fieldname.replace("_", " ").title()))))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be after To Date"))

	if filters.view_type not in ("Detailed View", "Summary View"):
		frappe.throw(_("Invalid View Type"))


def get_columns(view_type):
	if view_type == "Summary View":
		return [
			{"fieldname": "item", "label": _("Item"), "fieldtype": "Link", "options": "Item", "width": 180},
			{"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 220},
			{
				"fieldname": "item_group",
				"label": _("Item Group"),
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 180,
			},
			{"fieldname": "entry_count", "label": _("Payment Entries"), "fieldtype": "Int", "width": 130},
			{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 140},
		]

	return [
		{
			"fieldname": "payment_entry",
			"label": _("Payment Entry"),
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 180,
		},
		{"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 180},
		{"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 200},
		{"fieldname": "item", "label": _("Item"), "fieldtype": "Link", "options": "Item", "width": 160},
		{"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 200},
		{
			"fieldname": "item_group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 160,
		},
		{"fieldname": "description", "label": _("Description"), "fieldtype": "Small Text", "width": 220},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 130},
		{
			"fieldname": "mode_of_payment",
			"label": _("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"width": 150,
		},
		{
			"fieldname": "treasury_account",
			"label": _("Treasury Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 190,
		},
		{"fieldname": "collector", "label": _("Collector"), "fieldtype": "Link", "options": "User", "width": 160},
		{"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 140},
		{"fieldname": "reference_no", "label": _("Reference No"), "fieldtype": "Data", "width": 140},
		{"fieldname": "reference_date", "label": _("Reference Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "notes", "label": _("Notes"), "fieldtype": "Small Text", "width": 200},
	]


def get_data(filters):
	if filters.view_type == "Summary View":
		return get_summary_data(filters)
	return get_detailed_data(filters)


def get_detailed_data(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			pe.name AS payment_entry,
			pe.posting_date,
			pe.party AS customer,
			pe.party_name AS customer_name,
			ci.item,
			ci.item_name,
			ci.item_group,
			ci.description,
			ci.amount,
			pe.mode_of_payment,
			pe.paid_to AS treasury_account,
			pe.custom_collector AS collector,
			pe.custom_branch AS branch,
			pe.reference_no,
			pe.reference_date,
			ci.notes
		FROM `tabPayment Entry` pe
		INNER JOIN `tabPayment Entry Collection Item` ci
			ON ci.parent = pe.name
			AND ci.parenttype = 'Payment Entry'
			AND ci.parentfield = 'custom_collection_items'
		WHERE {conditions}
		ORDER BY pe.posting_date, pe.name, ci.idx
		""",
		params,
		as_dict=True,
	)


def get_summary_data(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			ci.item,
			MAX(ci.item_name) AS item_name,
			MAX(ci.item_group) AS item_group,
			COUNT(DISTINCT pe.name) AS entry_count,
			SUM(ci.amount) AS amount
		FROM `tabPayment Entry` pe
		INNER JOIN `tabPayment Entry Collection Item` ci
			ON ci.parent = pe.name
			AND ci.parenttype = 'Payment Entry'
			AND ci.parentfield = 'custom_collection_items'
		WHERE {conditions}
		GROUP BY ci.item
		ORDER BY amount DESC, ci.item
		""",
		params,
		as_dict=True,
	)


def get_conditions(filters):
	conditions = [
		"pe.docstatus = 1",
		"pe.payment_type = 'Receive'",
		"pe.party_type = 'Customer'",
		"pe.company = %(company)s",
		"pe.posting_date BETWEEN %(from_date)s AND %(to_date)s",
	]
	params = {
		"company": filters.company,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}

	optional_filters = {
		"customer": ("pe.party", filters.get("customer")),
		"item": ("ci.item", filters.get("item")),
		"item_group": ("ci.item_group", filters.get("item_group")),
		"mode_of_payment": ("pe.mode_of_payment", filters.get("mode_of_payment")),
		"treasury_account": ("pe.paid_to", filters.get("treasury_account")),
		"collector": ("pe.custom_collector", filters.get("collector")),
		"branch": ("pe.custom_branch", filters.get("branch")),
	}

	for param, (column, value) in optional_filters.items():
		if value:
			conditions.append(f"{column} = %({param})s")
			params[param] = value

	return " AND ".join(conditions), params


def get_report_summary(filters):
	return [
		{
			"label": _("Total Received"),
			"value": get_total(filters),
			"indicator": "Green",
			"datatype": "Currency",
		}
	]


def get_total(filters):
	conditions, params = get_conditions(filters)
	result = frappe.db.sql(
		f"""
		SELECT SUM(ci.amount)
		FROM `tabPayment Entry` pe
		INNER JOIN `tabPayment Entry Collection Item` ci
			ON ci.parent = pe.name
			AND ci.parenttype = 'Payment Entry'
			AND ci.parentfield = 'custom_collection_items'
		WHERE {conditions}
		""",
		params,
	)
	return flt(result[0][0]) if result else 0


def get_message(filters):
	rows = get_breakdown_rows(filters)
	if not rows:
		return ""

	return """
		<div class="row">
			<div class="col-md-4">{mode_of_payment}</div>
			<div class="col-md-4">{treasury_account}</div>
			<div class="col-md-4">{item}</div>
		</div>
	""".format(
		mode_of_payment=render_breakdown(_("By Mode of Payment"), rows, "mode_of_payment"),
		treasury_account=render_breakdown(_("By Treasury Account"), rows, "treasury_account"),
		item=render_breakdown(_("By Item"), rows, "item"),
	)


def get_breakdown_rows(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			COALESCE(pe.mode_of_payment, '') AS mode_of_payment,
			COALESCE(pe.paid_to, '') AS treasury_account,
			COALESCE(ci.item_name, ci.item, '') AS item,
			ci.amount
		FROM `tabPayment Entry` pe
		INNER JOIN `tabPayment Entry Collection Item` ci
			ON ci.parent = pe.name
			AND ci.parenttype = 'Payment Entry'
			AND ci.parentfield = 'custom_collection_items'
		WHERE {conditions}
		""",
		params,
		as_dict=True,
	)


def render_breakdown(title, rows, fieldname):
	totals = defaultdict(float)
	for row in rows:
		totals[row.get(fieldname) or _("Not Set")] += flt(row.amount)

	lines = "".join(
		f"<tr><td>{frappe.utils.escape_html(label)}</td><td class='text-right'>{amount:,.2f}</td></tr>"
		for label, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:8]
	)

	return f"""
		<h5>{frappe.utils.escape_html(title)}</h5>
		<table class="table table-bordered table-condensed">
			<tbody>{lines}</tbody>
		</table>
	"""
