const CUSTOMER_COLLECTION_FIELDS = [
	"custom_is_collection_receipt",
	"custom_manual_receipt_no",
	"custom_received_from_text",
	"custom_payment_for",
	"custom_collector",
	"custom_amount_in_words_arabic",
	"custom_receipt_notes",
	"custom_branch",
	"custom_collection_items",
];

function is_customer_collection(frm) {
	return frm.doc.payment_type === "Receive" && frm.doc.party_type === "Customer";
}

function refresh_customer_collection_fields(frm) {
	const show = is_customer_collection(frm);
	CUSTOMER_COLLECTION_FIELDS.forEach((fieldname) => frm.toggle_display(fieldname, show));
	frm.toggle_reqd("custom_collection_items", show);
	refresh_collection_items_total(frm);
}

function refresh_collection_items_total(frm) {
	if (!is_customer_collection(frm)) {
		frm.dashboard.clear_headline();
		return;
	}

	frm.dashboard.clear_headline();

	const total = (frm.doc.custom_collection_items || []).reduce(
		(sum, row) => sum + flt(row.amount),
		0
	);
	const received_amount = flt(frm.doc.received_amount);
	const currency = frm.doc.paid_to_account_currency || frm.doc.company_currency;
	const indicator = total === received_amount ? "green" : "orange";
	frm.dashboard.set_headline_alert(
		__("Collection Items Total: {0}", [format_currency(total, currency)]),
		indicator
	);
}

function set_received_from_text(frm) {
	if (!is_customer_collection(frm) || frm.doc.custom_received_from_text) {
		return;
	}

	const party_name = frm.doc.party_name || frm.doc.party;
	if (party_name) {
		frm.set_value("custom_received_from_text", party_name);
	}
}

frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		refresh_customer_collection_fields(frm);
		set_received_from_text(frm);
	},

	payment_type(frm) {
		refresh_customer_collection_fields(frm);
	},

	party_type(frm) {
		refresh_customer_collection_fields(frm);
	},

	party(frm) {
		set_received_from_text(frm);
	},

	party_name(frm) {
		set_received_from_text(frm);
	},

	received_amount(frm) {
		refresh_collection_items_total(frm);
	},

	custom_collection_items_add(frm) {
		refresh_collection_items_total(frm);
	},

	custom_collection_items_remove(frm) {
		refresh_collection_items_total(frm);
	},
});

frappe.ui.form.on("Payment Entry Collection Item", {
	item(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item) {
			frappe.model.set_value(cdt, cdn, "item_name", "");
			frappe.model.set_value(cdt, cdn, "item_group", "");
			return;
		}

		frappe.db.get_value("Item", row.item, ["item_name", "item_group"]).then((response) => {
			const values = response.message || {};
			frappe.model.set_value(cdt, cdn, "item_name", values.item_name || "");
			frappe.model.set_value(cdt, cdn, "item_group", values.item_group || "");
		});
	},

	amount(frm) {
		refresh_collection_items_total(frm);
	},
});
