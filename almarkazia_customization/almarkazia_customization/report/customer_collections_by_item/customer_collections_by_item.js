frappe.query_reports["Customer Collections by Item"] = {
	onload(report) {
		report.page.add_inner_button(__("طباعة التقرير"), () => {
			let filters;
			try {
				filters = report.get_filter_values(true);
			} catch (e) {
				return;
			}

			const url = frappe.urllib.get_full_url(
				"/api/method/almarkazia_customization.almarkazia_customization.report.customer_collections_by_item.customer_collections_by_item.get_print_html" +
					"?filters=" +
					encodeURIComponent(JSON.stringify(filters))
			);
			window.open(url, "_blank");
		});
	},
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "view_type",
			label: __("View Type"),
			fieldtype: "Select",
			options: "Detailed View\nSummary View",
			default: "Detailed View",
			reqd: 1,
		},
		{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "item", label: __("Item"), fieldtype: "Link", options: "Item" },
		{ fieldname: "item_group", label: __("Item Group"), fieldtype: "Link", options: "Item Group" },
		{
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			options: "Mode of Payment",
		},
		{
			fieldname: "treasury_account",
			label: __("Treasury Account"),
			fieldtype: "Link",
			options: "Account",
			get_query() {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
						is_group: 0,
					},
				};
			},
		},
	],
};
