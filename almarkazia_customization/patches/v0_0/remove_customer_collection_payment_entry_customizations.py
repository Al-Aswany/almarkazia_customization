import frappe


CUSTOM_FIELDS = (
	"Payment Entry-custom_is_collection_receipt",
	"Payment Entry-custom_manual_receipt_no",
	"Payment Entry-custom_received_from_text",
	"Payment Entry-custom_payment_for",
	"Payment Entry-custom_collector",
	"Payment Entry-custom_amount_in_words_arabic",
	"Payment Entry-custom_receipt_notes",
	"Payment Entry-custom_branch",
	"Payment Entry-custom_collection_items",
	"Payment Entry-custom_section_break_y3478",
)


def execute():
	for fieldname in CUSTOM_FIELDS:
		if frappe.db.exists("Custom Field", fieldname):
			frappe.delete_doc("Custom Field", fieldname, force=True, ignore_permissions=True)

	if frappe.db.exists("DocType", "Payment Entry Collection Item"):
		frappe.delete_doc("DocType", "Payment Entry Collection Item", force=True, ignore_permissions=True)

	frappe.clear_cache(doctype="Payment Entry")
	frappe.db.commit()
