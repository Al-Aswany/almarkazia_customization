import frappe
from frappe import _
from frappe.model.meta import get_field_precision
from frappe.utils import flt


COLLECTION_TOTAL_ERROR = "إجمالي بنود التحصيل يجب أن يساوي إجمالي المبلغ المستلم."


def validate_customer_collection(doc, method=None):
	if not is_customer_collection(doc):
		return

	set_amount_in_words_arabic(doc)
	validate_collection_items_total(doc)


def is_customer_collection(doc):
	return doc.get("payment_type") == "Receive" and doc.get("party_type") == "Customer"


def validate_collection_items_total(doc):
	items = doc.get("custom_collection_items") or []
	precision = get_payment_currency_precision(doc)
	items_total = flt(sum(flt(row.get("amount"), precision) for row in items), precision)
	received_amount = flt(doc.get("received_amount"), precision)

	if not items or items_total != received_amount:
		frappe.throw(_(COLLECTION_TOTAL_ERROR))


def set_amount_in_words_arabic(doc):
	precision = get_payment_currency_precision(doc)
	amount = flt(doc.get("received_amount"), precision)
	doc.custom_amount_in_words_arabic = get_amount_in_words_arabic(amount, precision)


def get_payment_currency_precision(doc):
	try:
		company_currency = frappe.get_cached_value("Company", doc.company, "default_currency")
		df = doc.meta.get_field("received_amount")
		if df:
			return get_field_precision(df, doc, company_currency)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Customer Collection Currency Precision")

	return 2


def get_amount_in_words_arabic(amount, precision):
	try:
		from num2words import num2words

		value = int(amount) if flt(amount, precision) == int(amount) else amount
		return num2words(value, lang="ar")
	except Exception:
		return str(flt(amount, precision))
