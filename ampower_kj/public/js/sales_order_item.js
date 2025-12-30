frappe.ui.form.on('Sales Order Item', {
	item_code: function(frm, cdt, cdn) {
 		let row = locals[cdt][cdn];

 		if (row.item_code) {
			frappe.model.set_value(cdt, cdn, 'soi_die', row.item_code);

 			frappe.db.get_value('Item', row.item_code, 'custom_item_weight_per_unit')
				.then(r => {
					if (r.message && r.message.custom_item_weight_per_unit) {
 						frappe.model.set_value(cdt, cdn, 'soi_order_weight', r.message.custom_item_weight_per_unit);
					}
				});
		}
	}
});
