# Copyright (c) 2026, Ambibuzz Technologies LLP and Contributors
# See license.txt

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

# Initialize logger for this module
logger = frappe.logger("ampower_kj.order_ledger_sync", allow_site=True, file_count=50)


def create_order_ledger_on_submit(doc, method=None) -> None:
	"""
	Create Order Ledger entries from Sales Order items on submit.
	Creates one Order Ledger entry per Sales Order Item (1:1 mapping).

	Uses automatic field copying based on Order Ledger's valid DB columns,
	ensuring custom fields are included without manual mapping.

	Transaction Handling:
	- Frappe automatically wraps each request in a DB transaction
	- If this function raises an exception, Frappe rolls back the entire transaction
	  (including the Sales Order submission)
	- Manual rollback via delete_doc() is a best-effort cleanup but may be unreliable
	  if commits have occurred mid-loop (Frappe's auto-commit behavior)

	Args:
		doc: Sales Order document
		method: Event method name (passed by Frappe, e.g., 'on_submit')

	Raises:
		Exception: If Order Ledger creation fails, preventing Sales Order submission
	"""

	# System fields to exclude from auto-copy
	EXCLUDE_FIELDS = {
		"name",
		"owner",
		"creation",
		"modified",
		"modified_by",
		"parent",
		"parentfield",
		"parenttype",
		"idx",
		"docstatus",
		"doctype",
		# Fields we set manually with different logic
		"item",
		"item_code",
		"sales_order",
		"sales_order_item",
		"order_date",
		"order_status",
	}

	try:
		logger.info(f"Starting Order Ledger creation for Sales Order: {doc.name} ({len(doc.items)} items)")

		# Get fresh Order Ledger meta to include recently added custom fields
		ol_meta = frappe.get_meta("Order Ledger", cached=False)

		created_ledgers = []  # Track created entries for rollback
		created_count = 0
		skipped_count = 0

		for item in doc.items:
			try:
				# Check if Order Ledger already exists for this item
				existing = frappe.db.exists("Order Ledger", {"sales_order_item": item.name})
				if existing:
					skipped_count += 1
					continue

				# Get Sales Order Item as dict (includes all custom fields)
				item_dict = item.as_dict()

				# Create base dict for Order Ledger with doctype
				ledger_dict = {"doctype": "Order Ledger"}

				# AUTO COPY: Iterate Order Ledger fields and copy from item dict or parent doc
				# This ensures we only set fields that exist in Order Ledger's schema
				for df in ol_meta.fields:
					fieldname = df.fieldname

					# Skip system/child-table fields and manually handled fields
					if fieldname in EXCLUDE_FIELDS:
						continue

					# Try to get value from item dict first, then from parent Sales Order
					if fieldname in item_dict and item_dict[fieldname] is not None:
						ledger_dict[fieldname] = item_dict[fieldname]
					elif doc.get(fieldname) is not None:
						ledger_dict[fieldname] = doc.get(fieldname)

				# Set/override required relationship fields (manual mapping)
				ledger_dict["sales_order"] = doc.name
				ledger_dict["sales_order_item"] = item.name
				ledger_dict["item"] = item.item_code  # Maps SOI.item_code -> OL.item
				ledger_dict["order_date"] = doc.transaction_date

				# Safely set order_status default if not already set
				if not ledger_dict.get("order_status") and ol_meta.has_field("order_status"):
					df = ol_meta.get_field("order_status")
					if df.fieldtype == "Select" and df.options:
						valid_options = [o.strip() for o in df.options.split("\n") if o.strip()]
						if "Unassigned" in valid_options:
							ledger_dict["order_status"] = "Unassigned"
						elif valid_options:
							ledger_dict["order_status"] = valid_options[0]

				# Debug log for custom field verification
				logger.debug(
					f"Creating Order Ledger for item {item.name}: "
					f"soi_die={item_dict.get('soi_die')} -> {ledger_dict.get('soi_die')}"
				)

				# Create doc from dict and insert
				order_ledger = frappe.get_doc(ledger_dict)
				order_ledger.insert(ignore_permissions=True)

				# Track for potential rollback
				created_ledgers.append(order_ledger.name)
				created_count += 1

			except Exception as item_error:
				# CRITICAL FAILURE - Rollback all created Order Ledgers
				logger.error(
					f"CRITICAL: Order Ledger creation failed for SO Item {item.name}. "
					f"Item Code: {item.item_code}, Item Name: {item.get('item_name', 'N/A')}. "
					f"Error: {item_error!s}. "
					f"Rolling back {len(created_ledgers)} created entries."
				)

				# Rollback: Delete all Order Ledgers created in this transaction
				# Note: This is best-effort. Frappe's transaction will ultimately roll back everything.
				rollback_count = 0
				for ledger_name in created_ledgers:
					try:
						frappe.delete_doc("Order Ledger", ledger_name, force=True, ignore_permissions=True)
						rollback_count += 1
					except Exception as rollback_error:
						logger.error(f"Rollback failed for {ledger_name}: {rollback_error}")

				# Log detailed error using logger
				logger.error(
					f"Order Ledger creation failed - SO: {doc.name}. "
					f"Failed Item: {item.name} ({item.item_code}). "
					f"Created: {created_count}, Rolled Back: {rollback_count}. "
					f"Traceback: {frappe.get_traceback()}"
				)

				# STOP Sales Order submission
				frappe.throw(
					f"Failed to create Order Ledger for item '{item.item_code}'. "
					f"Sales Order submission cancelled. Please fix the error and try again."
				)

		# Log summary
		if created_count > 0 or skipped_count > 0:
			logger.info(
				f"Order Ledger creation complete for SO {doc.name}: "
				f"{created_count} created, {skipped_count} skipped"
			)

	except Exception as e:
		# Log overall failure
		error_msg = f"Order Ledger creation failed for Sales Order: {doc.name}"
		logger.error(f"{error_msg}: {e}. Total Items: {len(doc.items)}. Traceback: {frappe.get_traceback()}")
		# Re-raise to prevent Sales Order submission
		frappe.throw("Failed to create Order Ledger entries. Please contact system administrator.")


def disable_order_ledger_on_cancel(doc, method=None) -> None:
	"""
	Disable all Order Ledger entries linked to a cancelled Sales Order.
	Sets disabled=1 for all Order Ledger entries referencing this Sales Order.

	Transaction Handling:
	- Frappe automatically wraps this in a DB transaction
	- If this function raises an exception, Frappe rolls back the entire transaction
	  (including the Sales Order cancellation)

	Args:
		doc: Sales Order document
		method: Event method name (passed by Frappe, e.g., 'on_cancel')

	Raises:
		Exception: If disabling Order Ledgers fails, preventing Sales Order cancellation
	"""

	try:
		logger.info(f"Disabling Order Ledgers for cancelled Sales Order: {doc.name}")

		# Get all Order Ledger entries for this Sales Order
		order_ledgers = frappe.get_all("Order Ledger", filters={"sales_order": doc.name}, pluck="name")

		if not order_ledgers:
			logger.warning(f"No Order Ledger entries found for Sales Order: {doc.name}")
			return

		# Disable all Order Ledger entries
		disabled_ledgers = []  # Track for rollback
		disabled_count = 0

		for ledger_name in order_ledgers:
			try:
				frappe.db.set_value("Order Ledger", ledger_name, "disabled", 1)
				disabled_ledgers.append(ledger_name)
				disabled_count += 1

			except Exception:
				# CRITICAL FAILURE - Rollback all disabled entries
				logger.error(
					f"CRITICAL: Failed to disable Order Ledger {ledger_name}. "
					f"Rolling back {len(disabled_ledgers)} disabled entries."
				)

				# Rollback: Re-enable all Order Ledgers disabled in this transaction
				# Note: This is best-effort. Frappe's transaction will ultimately roll back everything.
				rollback_count = 0
				for disabled_ledger in disabled_ledgers:
					try:
						frappe.db.set_value("Order Ledger", disabled_ledger, "disabled", 0)
						rollback_count += 1
					except Exception as rollback_error:
						logger.error(f"Rollback failed for {disabled_ledger}: {rollback_error}")

				# Log detailed error using logger
				logger.error(
					f"Failed to disable Order Ledger: {ledger_name}. "
					f"Sales Order: {doc.name}. "
					f"Disabled: {disabled_count}, Rolled Back: {rollback_count}. "
					f"Traceback: {frappe.get_traceback()}"
				)

				# STOP Sales Order cancellation
				frappe.throw(
					"Failed to disable Order Ledger entries. "
					"Sales Order cancellation prevented. Please contact system administrator."
				)

		logger.info(f"Disabled {disabled_count} Order Ledger entries for Sales Order: {doc.name}")

	except Exception as e:
		# Log overall failure
		error_msg = f"Failed to disable Order Ledgers for Sales Order: {doc.name}"
		logger.error(f"{error_msg}: {e}. Traceback: {frappe.get_traceback()}")
		# Re-raise to prevent Sales Order cancellation
		frappe.throw("Failed to disable Order Ledger entries. Please contact system administrator.")
