"""
Server Script: Create Order Ledger from Sales Order
Event: After Insert on Sales Order
Description: Automatically creates Order Ledger entries for each Sales Order item
Relationship: 1 Sales Order Item → 1 Order Ledger entry (with same qty)
"""

import frappe


def execute(doc, method=None):
	"""
	Create Order Ledger entries from Sales Order items.
	Creates one Order Ledger entry per Sales Order Item (1:1 mapping).
	Uses frappe.copy_doc to copy all compatible fields from Sales Order Item.

	Args:
		doc: Sales Order document
		method: Event method (not used, required by hook signature)
	"""
	for item in doc.items:
		existing = frappe.db.exists("Order Ledger", {"sales_order_item": item.name})
		if existing:
			continue

		# Copy the entire Sales Order Item
		order_ledger_copy = frappe.copy_doc(item)

		# Get Order Ledger DocType meta to know valid fields
		target_meta = frappe.get_meta("Order Ledger")
		valid_fields = {df.fieldname for df in target_meta.fields}

		# Create new document with only compatible fields
		order_ledger_dict = {"doctype": "Order Ledger"}

		# Copy ALL fields that exist in both DocTypes automatically
		for fieldname in valid_fields:
			if hasattr(order_ledger_copy, fieldname):
				value = order_ledger_copy.get(fieldname)
				if value is not None:
					order_ledger_dict[fieldname] = value


		# Override ONLY fields that need different values or come from parent Sales Order
		order_ledger_dict["sales_order"] = doc.name
		order_ledger_dict["die"] = item.get("soi_die")
		order_ledger_dict["karigar"] = item.get("soi_karigar")
		order_ledger_dict["customer_notes"] = item.get("soi_customer_notes")
		order_ledger_dict["planned_dispatch_date"] = item.get("soi_planned_dispatch_date")

 
		order_ledger_dict["sales_order_item"] = item.name
		order_ledger_dict["customer_notes"] = doc.get("customer_notes")
		order_ledger_dict["order_type"] = doc.get("order_type")
		order_ledger_dict["order_date"] = doc.transaction_date
		# Field mappings where source/target field names differ
 
		order_ledger_dict["order_status"] = "Unassigned"

		order_ledger_dict["item"] = item.item_code
		order_ledger_dict["order_weight"] = item.get("weight_per_unit")
		order_ledger_dict["planned_dispatch_date"] = item.get("delivery_date")

		# Create and insert
		order_ledger = frappe.get_doc(order_ledger_dict)
		order_ledger.insert(ignore_permissions=True)
