import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


CUSTOMER_COLLECTION_DEPENDS_ON = "eval:doc.payment_type == 'Receive' && doc.party_type == 'Customer'"


def setup_customer_collections():
	create_payment_entry_collection_fields()


def create_payment_entry_collection_fields():
	custom_fields = {
		"Payment Entry": [
			{
				"fieldname": "custom_manual_receipt_no",
				"label": "Manual Receipt No",
				"fieldtype": "Data",
				"insert_after": "received_amount",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_received_from_text",
				"label": "Received From",
				"fieldtype": "Data",
				"insert_after": "custom_manual_receipt_no",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_payment_for",
				"label": "Payment For",
				"fieldtype": "Small Text",
				"insert_after": "custom_received_from_text",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_collector",
				"label": "Collector",
				"fieldtype": "Link",
				"options": "User",
				"insert_after": "custom_payment_for",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_amount_in_words_arabic",
				"label": "Amount in Words Arabic",
				"fieldtype": "Data",
				"insert_after": "custom_collector",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
				"read_only": 1,
			},
			{
				"fieldname": "custom_receipt_notes",
				"label": "Receipt Notes",
				"fieldtype": "Small Text",
				"insert_after": "custom_amount_in_words_arabic",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_branch",
				"label": "Branch",
				"fieldtype": "Link",
				"options": "Branch",
				"insert_after": "custom_receipt_notes",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
			{
				"fieldname": "custom_collection_items",
				"label": "Collection Items",
				"fieldtype": "Table",
				"options": "Payment Entry Collection Item",
				"insert_after": "custom_branch",
				"depends_on": CUSTOMER_COLLECTION_DEPENDS_ON,
			},
		],
	}

	create_custom_fields(custom_fields, ignore_validate=True, update=True)
	frappe.db.commit()
