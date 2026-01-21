frappe.ui.form.on('Item', {
	weight_uom: function (frm) {
		if (frm.doc.weight_uom) {
			// When weight_uom is updated, set the same value to soi_weight_per_unit
			frm.set_value('soi_weight_per_unit', frm.doc.weight_uom);
		}
	},

	soi_weight_per_unit: function (frm) {
		if (frm.doc.soi_weight_per_unit) {
			// When soi_weight_per_unit is updated, set the same value to weight_uom
			frm.set_value('weight_uom', frm.doc.soi_weight_per_unit);
		}
	}
});
