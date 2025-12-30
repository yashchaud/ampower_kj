"""
Server Script: Create Order Ledger from Sales Order
Events: on_submit, on_cancel on Sales Order
Description:
  - on_submit: Creates Order Ledger entries when Sales Order is submitted
  - on_cancel: Disables Order Ledger entries when Sales Order is cancelled
Relationship: 1 Sales Order Item → 1 Order Ledger entry (with same qty)

Note: These hooks are additive and do not override any existing Sales Order doc events.
Frappe's doc_events system appends handlers rather than replacing them.
"""

import frappe


def create_order_ledger_on_submit(doc, method=None):
	"""
	Create Order Ledger entries from Sales Order items on submit.
	Creates one Order Ledger entry per Sales Order Item (1:1 mapping).

	Args:
		doc: Sales Order document
		method: Event method name (passed by Frappe, e.g., 'on_submit')
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
		order_ledger_dict["sales_order_item"] = item.name
		order_ledger_dict["customer_notes"] = doc.get("customer_notes")
		order_ledger_dict["order_type"] = doc.get("order_type")
		order_ledger_dict["order_date"] = doc.transaction_date

		order_ledger_dict["order_status"] = "Unassigned"

		order_ledger_dict["item"] = item.item_code
		order_ledger_dict["order_weight"] = item.get("soi_order_weight") or item.get("weight_per_unit")
		order_ledger_dict["planned_dispatch_date"] = item.get("delivery_date")

		# Create and insert
		order_ledger = frappe.get_doc(order_ledger_dict)
		order_ledger.insert(ignore_permissions=True)


def disable_order_ledger_on_cancel(doc, method=None):
	"""
	Disable all Order Ledger entries linked to a cancelled Sales Order.
	Sets disabled=1 for all Order Ledger entries referencing this Sales Order.

	Args:
		doc: Sales Order document
		method: Event method name (passed by Frappe, e.g., 'on_cancel')
	"""
	order_ledgers = frappe.get_all(
		"Order Ledger",
		filters={"sales_order": doc.name},
		pluck="name"
	)

	for ledger_name in order_ledgers:
		frappe.db.set_value("Order Ledger", ledger_name, "disabled", 1)
