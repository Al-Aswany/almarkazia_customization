import frappe

from almarkazia_customization.customer_collections_setup import setup_customer_collections


def execute():
	setup_customer_collections()
	backfill_existing_collection_receipts()


def backfill_existing_collection_receipts():
	if not frappe.db.has_column("Payment Entry", "custom_is_collection_receipt"):
		return

	frappe.db.sql(
		"""
		UPDATE `tabPayment Entry` pe
		SET pe.custom_is_collection_receipt = 1
		WHERE pe.payment_type = 'Receive'
			AND pe.party_type = 'Customer'
			AND (pe.custom_is_collection_receipt IS NULL OR pe.custom_is_collection_receipt = 0)
			AND EXISTS (
				SELECT 1
				FROM `tabPayment Entry Collection Item` ci
				WHERE ci.parent = pe.name
					AND ci.parenttype = 'Payment Entry'
					AND ci.parentfield = 'custom_collection_items'
			)
		"""
	)
	frappe.db.commit()
