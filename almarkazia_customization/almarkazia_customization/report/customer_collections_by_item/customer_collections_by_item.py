from collections import defaultdict
import json

import frappe
from frappe import _
from frappe.desk.query_report import get_report_doc
from frappe.utils import flt, format_date, now_datetime

from almarkazia_customization.utils import egyptian_money_in_words, format_egyptian_money


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)

	columns = get_columns(filters.view_type)
	data = get_data(filters)
	message = get_message(filters)
	report_summary = get_report_summary(filters)
	return columns, data, message, None, report_summary


def validate_filters(filters):
	required_labels = {
		"company": _("الشركة"),
		"from_date": _("من تاريخ"),
		"to_date": _("إلى تاريخ"),
		"view_type": _("نوع العرض"),
	}
	for fieldname in ("company", "from_date", "to_date", "view_type"):
		if not filters.get(fieldname):
			frappe.throw(_("الفلتر {0} مطلوب").format(frappe.bold(required_labels[fieldname])))

	if filters.from_date > filters.to_date:
		frappe.throw(_("لا يمكن أن يكون تاريخ البداية بعد تاريخ النهاية"))

	if filters.view_type not in ("Detailed View", "Summary View"):
		frappe.throw(_("نوع العرض غير صحيح"))


def get_columns(view_type):
	if view_type == "Summary View":
		return [
			{"fieldname": "item", "label": _("الصنف"), "fieldtype": "Link", "options": "Item", "width": 180},
			{"fieldname": "item_name", "label": _("اسم الصنف"), "fieldtype": "Data", "width": 220},
			{
				"fieldname": "item_group",
				"label": _("مجموعة الصنف"),
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 180,
			},
			{"fieldname": "entry_count", "label": _("عدد الإيصالات"), "fieldtype": "Int", "width": 130},
			{"fieldname": "amount", "label": _("المبلغ المحصل"), "fieldtype": "Currency", "width": 150},
		]

	return [
		{
			"fieldname": "payment_entry",
			"label": _("رقم الإيصال"),
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 180,
		},
		{"fieldname": "posting_date", "label": _("التاريخ"), "fieldtype": "Date", "width": 110},
		{"fieldname": "customer", "label": _("العميل"), "fieldtype": "Link", "options": "Customer", "width": 180},
		{"fieldname": "customer_name", "label": _("اسم العميل"), "fieldtype": "Data", "width": 200},
		{
			"fieldname": "sales_invoice",
			"label": _("فاتورة المبيعات"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 180,
		},
		{"fieldname": "item", "label": _("الصنف"), "fieldtype": "Link", "options": "Item", "width": 160},
		{"fieldname": "item_name", "label": _("اسم الصنف"), "fieldtype": "Data", "width": 200},
		{
			"fieldname": "item_group",
			"label": _("مجموعة الصنف"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 160,
		},
		{"fieldname": "description", "label": _("البيان"), "fieldtype": "Small Text", "width": 220},
		{"fieldname": "qty", "label": _("الكمية"), "fieldtype": "Float", "width": 90},
		{"fieldname": "rate", "label": _("السعر"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "invoice_item_amount", "label": _("قيمة بند الفاتورة"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "amount", "label": _("المبلغ المحصل"), "fieldtype": "Currency", "width": 150},
		{
			"fieldname": "mode_of_payment",
			"label": _("طريقة السداد"),
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"width": 150,
		},
		{
			"fieldname": "treasury_account",
			"label": _("الخزنة / الحساب"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 190,
		},
		{"fieldname": "reference_no", "label": _("رقم المرجع"), "fieldtype": "Data", "width": 140},
		{"fieldname": "reference_date", "label": _("تاريخ المرجع"), "fieldtype": "Date", "width": 120},
		{"fieldname": "notes", "label": _("ملاحظات"), "fieldtype": "Small Text", "width": 200},
	]


def get_data(filters):
	if filters.view_type == "Summary View":
		return get_summary_data(filters)
	return get_detailed_data(filters)


def get_allocated_item_amount_expression():
	return """
		CASE
			WHEN ABS(COALESCE(invoice_totals.invoice_item_total, 0)) > 0
			THEN COALESCE(per.allocated_amount, 0) * sii.net_amount / invoice_totals.invoice_item_total
			ELSE 0
		END
	"""


def get_invoice_joins():
	return """
		INNER JOIN `tabPayment Entry Reference` per
			ON per.parent = pe.name
			AND per.parenttype = 'Payment Entry'
			AND per.reference_doctype = 'Sales Invoice'
		INNER JOIN `tabSales Invoice` si
			ON si.name = per.reference_name
			AND si.docstatus = 1
		INNER JOIN `tabSales Invoice Item` sii
			ON sii.parent = si.name
			AND sii.parenttype = 'Sales Invoice'
		INNER JOIN (
			SELECT parent, SUM(net_amount) AS invoice_item_total
			FROM `tabSales Invoice Item`
			WHERE parenttype = 'Sales Invoice'
			GROUP BY parent
		) invoice_totals
			ON invoice_totals.parent = si.name
	"""


def get_detailed_data(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			sii.idx AS item_row,
			pe.name AS payment_entry,
			pe.posting_date,
			pe.party AS customer,
			COALESCE(c.customer_name, pe.party_name, si.customer_name) AS customer_name,
			si.name AS sales_invoice,
			sii.item_code AS item,
			sii.item_name,
			sii.item_group,
			sii.description,
			sii.qty,
			sii.rate,
			sii.net_amount AS invoice_item_amount,
			per.allocated_amount AS invoice_allocated_amount,
			{get_allocated_item_amount_expression()} AS amount,
			pe.mode_of_payment,
			pe.paid_to AS treasury_account,
			pe.reference_no,
			pe.reference_date,
			pe.remarks AS notes,
			pe.remarks
		FROM `tabPayment Entry` pe
		{get_invoice_joins()}
		LEFT JOIN `tabCustomer` c
			ON c.name = pe.party
		WHERE {conditions}
		ORDER BY pe.posting_date, pe.name, si.name, sii.idx
		""",
		params,
		as_dict=True,
	)


def get_summary_data(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			sii.item_code AS item,
			MAX(sii.item_name) AS item_name,
			MAX(sii.item_group) AS item_group,
			COUNT(DISTINCT pe.name) AS entry_count,
			SUM({get_allocated_item_amount_expression()}) AS amount
		FROM `tabPayment Entry` pe
		{get_invoice_joins()}
		WHERE {conditions}
		GROUP BY sii.item_code
		ORDER BY amount DESC, sii.item_code
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
		"item": ("sii.item_code", filters.get("item")),
		"item_group": ("sii.item_group", filters.get("item_group")),
		"mode_of_payment": ("pe.mode_of_payment", filters.get("mode_of_payment")),
		"treasury_account": ("pe.paid_to", filters.get("treasury_account")),
	}

	for param, (column, value) in optional_filters.items():
		if value:
			conditions.append(f"{column} = %({param})s")
			params[param] = value

	return " AND ".join(conditions), params


def get_report_summary(filters):
	return [
		{
			"label": _("إجمالي المحصل"),
			"value": get_total(filters),
			"indicator": "Green",
			"datatype": "Currency",
		}
	]


def get_total(filters):
	conditions, params = get_conditions(filters)
	result = frappe.db.sql(
		f"""
		SELECT SUM({get_allocated_item_amount_expression()})
		FROM `tabPayment Entry` pe
		{get_invoice_joins()}
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
		mode_of_payment=render_breakdown(_("حسب طريقة السداد"), rows, "mode_of_payment"),
		treasury_account=render_breakdown(_("حسب الخزنة / الحساب"), rows, "treasury_account"),
		item=render_breakdown(_("حسب الصنف"), rows, "item"),
	)


def get_breakdown_rows(filters):
	conditions, params = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			COALESCE(pe.mode_of_payment, '') AS mode_of_payment,
			COALESCE(pe.paid_to, '') AS treasury_account,
			COALESCE(sii.item_name, sii.item_code, '') AS item,
			{get_allocated_item_amount_expression()} AS amount
		FROM `tabPayment Entry` pe
		{get_invoice_joins()}
		WHERE {conditions}
		""",
		params,
		as_dict=True,
	)


def render_breakdown(title, rows, fieldname):
	totals = defaultdict(float)
	for row in rows:
		totals[row.get(fieldname) or _("غير محدد")] += flt(row.amount)

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


@frappe.whitelist()
@frappe.read_only()
def get_print_html(filters=None):
	filters = parse_print_filters(filters)
	get_report_doc("Customer Collections by Item")
	validate_filters(filters)

	detailed_rows = get_detailed_data(filters)
	summary_rows = get_summary_data(filters) if filters.view_type == "Summary View" else []
	amount_columns = get_print_amount_columns(detailed_rows)
	currency = get_company_currency(filters.company)
	totals = get_print_totals(detailed_rows, amount_columns)

	context = {
		"filters": filters,
		"filter_rows": get_print_filter_rows(filters),
		"company": filters.company,
		"company_tax_id": frappe.db.get_value("Company", filters.company, "tax_id"),
		"currency": get_currency_label(currency),
		"printed_on": format_date(now_datetime().date()),
		"view_type_label": get_view_type_label(filters.view_type),
		"amount_columns": amount_columns,
		"detailed_rows": get_detailed_print_rows(detailed_rows, amount_columns),
		"summary_rows": get_summary_print_rows(summary_rows, amount_columns),
		"totals": totals,
		"total_in_words": egyptian_money_in_words(totals.total_received),
		"format_amount": format_egyptian_money,
	}

	template_path = frappe.get_app_path(
		"almarkazia_customization",
		"templates",
		"includes",
		"customer_collections_by_item_print.html",
	)
	with open(template_path) as template:
		html = frappe.render_template(template.read(), context)

	frappe.local.response.filename = "customer_collections_by_item.html"
	frappe.local.response.filecontent = html
	frappe.local.response.type = "download"
	frappe.local.response.display_content_as = "inline"
	frappe.local.response.content_type = "text/html; charset=utf-8"


def parse_print_filters(filters):
	if isinstance(filters, str):
		filters = json.loads(filters or "{}")
	return frappe._dict(filters or {})


def get_company_currency(company):
	return frappe.get_cached_value("Company", company, "default_currency")


def get_currency_label(currency):
	if currency == "EGP":
		return _("جنيه مصري")
	return currency


def get_print_amount_columns(rows):
	labels = []
	seen = set()
	for row in rows:
		label = get_amount_column_label(row)
		if label not in seen:
			labels.append(label)
			seen.add(label)

	return [frappe._dict({"key": label, "label": label}) for label in labels]


def get_amount_column_label(row):
	return row.get("item_name") or row.get("item") or _("غير محدد")


def get_detailed_print_rows(rows, amount_columns):
	print_rows = []
	entries = {}

	for row in rows:
		entry = entries.setdefault(
			row.payment_entry,
			frappe._dict(
				{
					"posting_date": format_date(row.posting_date),
					"payment_entry": row.payment_entry,
					"customer": row.customer_name or row.customer or "",
					"description_parts": [],
					"mode_of_payment": row.mode_of_payment or "",
					"treasury_account": row.treasury_account or "",
					"amount_cells": {column.key: 0 for column in amount_columns},
					"amount": 0,
					"remarks": row.remarks or "",
				}
			),
		)

		label = get_amount_column_label(row)
		amount = flt(row.amount)
		entry.amount_cells[label] = flt(entry.amount_cells.get(label)) + amount
		entry.amount += amount

		description = row.description or row.item_name or row.item
		if description and description not in entry.description_parts:
			entry.description_parts.append(description)

	for index, entry in enumerate(entries.values(), start=1):
		entry.serial = index
		entry.description = " / ".join(entry.description_parts)
		print_rows.append(entry)

	return print_rows


def get_summary_print_rows(rows, amount_columns):
	print_rows = []
	for index, row in enumerate(rows, start=1):
		label = row.get("item_name") or row.get("item") or _("غير محدد")
		amount = flt(row.amount)
		print_rows.append(
			frappe._dict(
				{
					"serial": index,
					"item": row.item or "",
					"item_name": row.item_name or "",
					"item_group": row.item_group or "",
					"entry_count": row.entry_count or 0,
					"amount_cells": {column.key: amount if column.key == label else 0 for column in amount_columns},
					"amount": amount,
				}
			)
		)
	return print_rows


def get_print_totals(rows, amount_columns):
	amount_by_column = {column.key: 0 for column in amount_columns}
	by_treasury_account = defaultdict(float)
	by_mode_of_payment = defaultdict(float)
	total_received = 0

	for row in rows:
		amount = flt(row.amount)
		label = get_amount_column_label(row)
		amount_by_column[label] += amount
		by_treasury_account[row.get("treasury_account") or _("غير محدد")] += amount
		by_mode_of_payment[row.get("mode_of_payment") or _("غير محدد")] += amount
		total_received += amount

	return frappe._dict(
		{
			"amount_by_column": amount_by_column,
			"by_treasury_account": sort_totals(by_treasury_account),
			"by_mode_of_payment": sort_totals(by_mode_of_payment),
			"total_received": total_received,
		}
	)


def sort_totals(totals):
	return [
		frappe._dict({"label": label, "amount": amount})
		for label, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)
	]


def get_print_filter_rows(filters):
	filter_labels = {
		"company": _("الشركة"),
		"from_date": _("من تاريخ"),
		"to_date": _("إلى تاريخ"),
		"view_type": _("نوع العرض"),
		"customer": _("العميل"),
		"item": _("الصنف"),
		"item_group": _("مجموعة الصنف"),
		"mode_of_payment": _("طريقة السداد"),
		"treasury_account": _("الخزنة / الحساب"),
	}
	rows = []
	for fieldname, label in filter_labels.items():
		value = filters.get(fieldname)
		if not value:
			continue

		if fieldname in ("from_date", "to_date"):
			value = format_date(value)
		elif fieldname == "view_type":
			value = get_view_type_label(value)

		rows.append(frappe._dict({"label": label, "value": value}))
	return rows


def get_view_type_label(view_type):
	if view_type == "Summary View":
		return _("عرض ملخص")
	return _("عرض تفصيلي")
