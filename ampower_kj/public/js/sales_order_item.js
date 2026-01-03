frappe.ui.form.on('Sales Order Item', {
	item_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.item_code) {
			// Use setTimeout to ensure this runs after Frappe's default item_code handler
			setTimeout(() => {
				// Set soi_die to the selected item code (only if not already set)
				if (!row.soi_die) {
					frappe.model.set_value(cdt, cdn, 'soi_die', row.item_code);
				}

				// Fetch and set weight from Item master (only if not already set)
				if (!row.soi_order_weight) {
					frappe.db.get_value('Item', row.item_code, 'item_weight_per_unit')
						.then(r => {
							if (r.message && r.message.item_weight_per_unit) {
								frappe.model.set_value(cdt, cdn, 'soi_order_weight', r.message.item_weight_per_unit);
							}
						});
				}
			}, 100);
		}
	}
});

