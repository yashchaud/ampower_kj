# Copyright (c) 2025, Ambibuzz Technologies LLP and Contributors
# See license.txt


import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika import Order

# Initialize logger for this module
logger = frappe.logger("ampower_kj.order_ledger", allow_site=True, file_count=50)


class OrderLedger(Document):
	def before_save(self):
		"""Auto-fill qty from Sales Order Item if not set"""
		if self.sales_order_item and not self.qty:
			# Get qty from Sales Order Item
			qty = frappe.db.get_value("Sales Order Item", self.sales_order_item, "qty")
			if qty:
				self.qty = qty

		# Default to 1 if still not set
		if not self.qty:
			self.qty = 1


# Constants
MAX_SEARCH_LENGTH = 100  # Maximum search string length to prevent performance issues


# WORKFLOW STATUS HELPERS
def _get_workflow_statuses() -> list[str]:
	"""
	Returns workflow status options from Order Ledger metadata.
	Fetches fresh data on every call to ensure accuracy.
	Internal use only - use get_workflow_status() for public API.

	Returns:
		list[str]: List of workflow status options

	Raises:
		frappe.ValidationError: If metadata is corrupted or invalid
	"""
	try:
		meta = frappe.get_meta("Order Ledger")

		if not meta:
			error_msg = "Order Ledger DocType metadata not found"
			logger.error(f"{error_msg}. DocType may have been deleted or metadata is corrupted.")
			frappe.throw(error_msg)

		field = meta.get_field("order_status")

		if not field:
			error_msg = "Field 'order_status' not found in Order Ledger DocType"
			logger.error(f"{error_msg}. Please check Order Ledger DocType configuration.")
			frappe.throw(error_msg)

		if field.fieldtype != "Select":
			error_msg = f"Field 'order_status' must be of type Select, found {field.fieldtype}"
			logger.error(f"{error_msg}. Expected: Select, Actual: {field.fieldtype}")
			frappe.throw(error_msg)

		statuses = [s.strip() for s in field.options.split("\n") if s.strip()]

		if not statuses:
			error_msg = "No workflow statuses defined in order_status field"
			logger.error(f"{error_msg}. Please configure workflow statuses in Order Ledger DocType.")
			frappe.throw(error_msg)

		logger.debug(f"Retrieved {len(statuses)} workflow statuses")
		return statuses

	except Exception as e:
		# Unexpected system error (not validation errors which are already raised via frappe.throw())
		logger.error(f"Workflow Status Retrieval - System Error: {e}. Traceback: {frappe.get_traceback()}")
		frappe.throw("System error retrieving workflow statuses. Please contact administrator.")


def status_to_key(status: str) -> str:
	"""
	Convert status label to key (e.g., "Internal QA" -> "internal_qa").
	Centralized to avoid duplication.
	"""
	if not status:
		return ""
	return status.lower().replace(" ", "_")


def key_to_status(key: str, statuses: list[str] | None = None) -> str | None:
	"""
	Convert key to status label (e.g., "internal_qa" -> "Internal QA").
	Returns None if not found.
	"""
	if statuses is None:
		statuses = _get_workflow_statuses()

	for status in statuses:
		if status_to_key(status) == key:
			return status
	return None


def get_workflow_stages() -> list[dict]:
	"""
	Get workflow stages dynamically from Order Ledger DocType metadata.
	Returns list of stage dictionaries with id, label, key, and status.
	"""
	statuses = _get_workflow_statuses()

	# Build stages dynamically
	stages = [
		{"id": idx + 1, "label": status, "key": status_to_key(status), "status": status}
		for idx, status in enumerate(statuses)
	]

	return stages


def get_status_index(status: str, statuses: list[str] | None = None) -> int:
	"""
	Get zero-based index of a status in workflow.
	Returns -1 if not found.
	"""
	if statuses is None:
		statuses = _get_workflow_statuses()

	try:
		return statuses.index(status)
	except ValueError:
		return -1


def get_stage_filters(stage_key: str) -> dict:
	"""Get frappe filters for a specific stage using order_status field."""
	filters = {"disabled": ["!=", 1]}

	# Convert key to status
	status = key_to_status(stage_key)
	if status:
		filters["order_status"] = status

	return filters


# TRANSITION LOGIC (Centralized & Maintainable)


def apply_status_transition_effects(
	order: Document, current_status: str, new_status: str, kwargs: dict | None = None
) -> None:
	"""
	Apply side effects when transitioning between statuses.
	Handles date updates and field changes based on workflow transitions.

	Args:
		order: Order Ledger document
		current_status: Current order status
		new_status: Target order status
		kwargs: Optional parameters (weights, notes, dates, etc.)
	"""
	if kwargs is None:
		kwargs = {}

	statuses = _get_workflow_statuses()
	current_idx = get_status_index(current_status, statuses)
	new_idx = get_status_index(new_status, statuses)

	# Invalid status - skip transition logic
	if current_idx == -1 or new_idx == -1:
		return

	today = frappe.utils.today()

	# ========== FORWARD TRANSITIONS ==========

	# Transition 0→1: Unassigned → Assigned (e.g., Karigar Assignment)
	if current_idx == 0 and new_idx == 1:
		if not order.karigar_assignment_date:
			order.karigar_assignment_date = today

	# Transition to index 2: Any → Incoming
	if new_idx == 2:
		if not order.karigar_incoming_date:
			order.karigar_incoming_date = today

	# Transition 2→3: Incoming → Internal QA (Receiving goods)
	if current_idx == 2 and new_idx == 3:
		if not order.karigar_actual_receive_date:
			order.karigar_actual_receive_date = today

		# Only set karigar_received_weight here if it's a direct weight value (not per-unit calculation)
		if kwargs.get("karigar_received_weight") and not kwargs.get("weight_per_unit"):
			try:
				order.karigar_received_weight = float(kwargs["karigar_received_weight"])
			except (ValueError, TypeError) as e:
				logger.warning(f"Invalid karigar_received_weight value: {kwargs['karigar_received_weight']}")
				frappe.throw("Invalid received weight value. Please enter a valid number.")

		if kwargs.get("receive_notes"):
			order.soi_karigar_notes = kwargs["receive_notes"]

		# Allow manual date override
		if kwargs.get("incoming_to_received"):
			order.karigar_actual_receive_date = kwargs["incoming_to_received"]

	# Transition 3→4: Internal QA → Pending Delivery (QA cleared)
	if current_idx == 3 and new_idx == 4:
		order.is_qa_cleared = 1

	# Transition 4→5: Pending Delivery → Delivered (Dispatch)
	if current_idx == 4 and new_idx == 5:
		if not order.actual_dispatch_date:
			order.actual_dispatch_date = today

		# Handle dispatch weight and QA notes
		# Two modes: direct weight or bulk weight_per_unit (handled at lines 637-640)
		if kwargs.get("dispatch_weight") and not kwargs.get("weight_per_unit"):
			try:
				order.dispatch_weight = float(kwargs["dispatch_weight"])
			except (ValueError, TypeError) as e:
				logger.warning(f"Invalid dispatch_weight value: {kwargs['dispatch_weight']}")
				frappe.throw("Invalid dispatch weight value. Please enter a valid number.")

		if kwargs.get("dispatch_notes"):
			order.qa_notes = kwargs["dispatch_notes"]

	# ========== REVERSE TRANSITIONS (Revert/Undo) ==========
	# Rule: Undo everything done in forward transition, without touching notes

	# Transition 1→0: Assigned → Unassigned
	if current_idx == 1 and new_idx == 0:
		order.karigar_assignment_date = None

	# Transition 2→1: Incoming → Assigned
	if current_idx == 2 and new_idx == 1:
		order.karigar_incoming_date = None

	# Transition 3→2: Internal QA → Incoming (Revert receiving)
	if current_idx == 3 and new_idx == 2:
		order.karigar_received_weight = None
		order.karigar_actual_receive_date = None

	# Transition 4→3: Pending Delivery → Internal QA (Revert QA clearance)
	if current_idx == 4 and new_idx == 3:
		order.is_qa_cleared = 0

	# Transition 5→4: Delivered → Pending Delivery (Revert dispatch)
	if current_idx == 5 and new_idx == 4:
		order.actual_dispatch_date = None
		order.dispatch_weight = None


# API ENDPOINTS


@frappe.whitelist()
def get_workflow_status():
	"""
	Public API to get workflow statuses.
	Returns workflow status options from Order Ledger metadata.
	"""
	return _get_workflow_statuses()


@frappe.whitelist()
def get_all_order_items(
	page=1,
	page_size=10,
	order_status=None,
	search=None,
	customer=None,
	karigar=None,
	item_group=None,
	return_counts_only=False,
) -> dict:
	"""Fetches Order Ledger entries with server-side pagination and filtering.

	Args:
		page: Page number for pagination
		page_size: Number of items per page
		order_status: Filter by specific order status
		search: Search term for order name, sales order, or item
		customer: Filter by customer
		karigar: Filter by karigar
		item_group: Filter by item group/die
		return_counts_only: If True, returns count grouped by status instead of paginated data

	Returns:
		If return_counts_only=True: {"Unassigned": 15, "Assigned": 8, ...}
		If return_counts_only=False: {"data": [...], "total": 100, "page": 1, ...}
	"""
	try:
		logger.debug(
			f"get_all_order_items called: page={page}, page_size={page_size}, return_counts_only={return_counts_only}"
		)

		# Sanitize search input
		if search:
			search = str(search)[:MAX_SEARCH_LENGTH]  # Limit length to prevent performance issues
			# Escape SQL wildcards to prevent injection (% and _ are treated as literals)
			search = frappe.db.escape(search, percent=False).strip("'")  # Remove quotes added by escape()

		# Define DocTypes
		OrderLedger = DocType("Order Ledger")
		SalesOrder = DocType("Sales Order")
		Item = DocType("Item")

		# Handle return_counts_only mode - optimized single query with GROUP BY
		if return_counts_only:
			# Build count query grouped by status
			count_query = (
				frappe.qb.from_(OrderLedger)
				.left_join(SalesOrder)
				.on(OrderLedger.sales_order == SalesOrder.name)
				.left_join(Item)
				.on(OrderLedger.item == Item.name)
				.select(OrderLedger.order_status, Count("*").as_("count"))
				.where(OrderLedger.disabled != 1)
				.groupby(OrderLedger.order_status)
			)

			# Apply filters (excluding order_status filter since we're grouping by it)
			if customer:
				count_query = count_query.where(SalesOrder.customer == customer)
			if karigar:
				count_query = count_query.where(OrderLedger.soi_karigar == karigar)
			if item_group:
				count_query = count_query.where(OrderLedger.soi_die == item_group)
			if search:
				search_condition = (
					(OrderLedger.name.like(f"%{search}%"))
					| (OrderLedger.sales_order.like(f"%{search}%"))
					| (OrderLedger.item.like(f"%{search}%"))
				)
				count_query = count_query.where(search_condition)

			# Execute and format results
			results = count_query.run(as_dict=True)
			counts = {row["order_status"]: row["count"] for row in results}

			# Ensure all workflow statuses are included (even if count is 0)
			all_statuses = _get_workflow_statuses()
			for status in all_statuses:
				if status not in counts:
					counts[status] = 0

			return counts

		# Normal pagination mode
		SalesOrderItem = DocType("Sales Order Item")

		# Convert parameters
		page = int(page) if page else 1
		page_size = int(page_size) if page_size else 10
	
		# Validate page_size to prevent OOM
		MAX_PAGE_SIZE = 1000
		if page_size > MAX_PAGE_SIZE:
			frappe.throw(f"Page size cannot exceed {MAX_PAGE_SIZE} items.")

		# Build base query with joins
		query = (
			frappe.qb.from_(OrderLedger)
			.left_join(SalesOrder)
			.on(OrderLedger.sales_order == SalesOrder.name)
			.left_join(Item)
			.on(OrderLedger.item == Item.name)
			.left_join(SalesOrderItem)
			.on(OrderLedger.sales_order_item == SalesOrderItem.name)
			.select(
				OrderLedger.name,
				OrderLedger.sales_order,
				OrderLedger.item,
				OrderLedger.order_status,
				OrderLedger.karigar_assigned_weight,
				OrderLedger.karigar_received_weight,
				OrderLedger.dispatch_weight,
				OrderLedger.qa_notes,
				OrderLedger.order_date,
				OrderLedger.qty,
				SalesOrder.customer,
				Item.image,
				Item.item_name.as_("item_name"),
				SalesOrderItem.sales_order_image,
				SalesOrderItem.description, 
				SalesOrderItem.texture,
				OrderLedger.soi_order_weight,
				OrderLedger.soi_die,
				OrderLedger.soi_karigar,
				OrderLedger.soi_karigar_notes,
				OrderLedger.soi_customer_notes,
				OrderLedger.soi_planned_dispatch_date,
			)
			.where(OrderLedger.disabled != 1)
		)

		# Count query
		count_query = (
			frappe.qb.from_(OrderLedger)
			.left_join(SalesOrder)
			.on(OrderLedger.sales_order == SalesOrder.name)
			.left_join(Item)
			.on(OrderLedger.item == Item.name)
			.select(Count("*").as_("total"))
			.where(OrderLedger.disabled != 1)
		)

		# Apply filters
		if order_status:
			query = query.where(OrderLedger.order_status == order_status)
			count_query = count_query.where(OrderLedger.order_status == order_status)

		if karigar:
			query = query.where(OrderLedger.soi_karigar == karigar)
			count_query = count_query.where(OrderLedger.soi_karigar == karigar)

		if customer:
			query = query.where(SalesOrder.customer == customer)
			count_query = count_query.where(SalesOrder.customer == customer)

		if item_group:
			query = query.where(OrderLedger.soi_die == item_group)
			count_query = count_query.where(OrderLedger.soi_die == item_group)

		# Apply search filter
		if search:
			search_condition = (
				(OrderLedger.name.like(f"%{search}%"))
				| (OrderLedger.sales_order.like(f"%{search}%"))
				| (OrderLedger.item.like(f"%{search}%"))
			)
			query = query.where(search_condition)
			count_query = count_query.where(search_condition)

		# Get total count
		total_count = count_query.run(as_dict=True)[0].total

		# Add ordering and pagination
		start = (page - 1) * page_size
		query = query.orderby(OrderLedger.modified, order=Order.desc).limit(page_size).offset(start)

		# Execute query
		orders = query.run(as_dict=True)

		# Enrich data with additional fields for frontend compatibility
		for order in orders:
			# Map item fields: item -> item_code
			order["item_code"] = order.get("item") or ""

			# Ensure item_name exists - fetch from Item master if not in query result
			item_code = order.get("item")
			if item_code and not order.get("item_name"):
				# Fetch item_name from Item master to ensure it's populated
				item_name = frappe.db.get_value("Item", item_code, "item_name")
				order["item_name"] = item_name if item_name else item_code
			elif not order.get("item_name"):
				order["item_name"] = ""

			order["qty"] = order.get("qty", 1)
			order["parent"] = order.get("sales_order")
			order["doctype"] = "Order Ledger"

			# Build images array (Sales Order Item image + Item master image)
			images = []
			if order.get("sales_order_image"):
				images.append(order["sales_order_image"])
			if order.get("image"):
				images.append(order["image"])
			order["images"] = images
			order["item_image"] = images[0] if images else None

			# Map SOI fields to frontend field names for consistency
			order["item_weight"] = order.get("soi_order_weight")
			order["karigar"] = order.get("soi_karigar")
			order["item_group"] = order.get("soi_die")
			order["karigar_notes"] = order.get("soi_karigar_notes")
			order["customer_notes"] = order.get("soi_customer_notes")
			order["planned_dispatch_date"] = order.get("soi_planned_dispatch_date")

		return {
			"data": orders,
			"total": total_count,
			"page": page,
			"page_size": page_size,
			"total_pages": (total_count + page_size - 1) // page_size,
		}

	except frappe.PermissionError:
		# Permission errors - let them through to user
		logger.warning(f"Permission denied in get_all_order_items for user {frappe.session.user}")
		raise

	except Exception as e:
		# System error - log once (includes traceback)
		logger.error(
			f"get_all_order_items API Failed: {e}. "
			f"Parameters: page={page}, page_size={page_size}, return_counts_only={return_counts_only}. "
			f"Traceback: {frappe.get_traceback()}"
		)

		# Return empty but valid response structure
		if return_counts_only:
			# Return empty counts for all statuses
			try:
				all_statuses = _get_workflow_statuses()
				return {status: 0 for status in all_statuses}
			except Exception:
				return {}
		else:
			# Return empty pagination response
			return {
				"data": [],
				"total": 0,
				"page": 1,
				"page_size": 10,
				"total_pages": 0,
			}


@frappe.whitelist()
def get_filter_options() -> dict[str, list[str]]:
	"""
	Get unique filter options for autocomplete (customers, karigars, item groups).
	Returns all options across all stages so filtering works regardless of current stage.

	Returns:
		dict with keys: customers, karigars, item_groups (each containing list of unique values)
	"""
	try:
		logger.debug("get_filter_options called")

		# Define DocTypes
		OrderLedger = DocType("Order Ledger")
		SalesOrder = DocType("Sales Order")

		base_condition = OrderLedger.disabled != 1

		# Get unique customers
		customer_query = (
			frappe.qb.from_(OrderLedger)
			.left_join(SalesOrder)
			.on(OrderLedger.sales_order == SalesOrder.name)
			.select(SalesOrder.customer)
			.distinct()
			.where(base_condition)
			.where(SalesOrder.customer.isnotnull())
			.where(SalesOrder.customer != "")
			.orderby(SalesOrder.customer, order=Order.asc)
		)
		customers = [row[0] for row in customer_query.run() if row[0]]

		# Get unique karigars
		karigar_query = (
			frappe.qb.from_(OrderLedger)
			.select(OrderLedger.soi_karigar)
			.distinct()
			.where(base_condition)
			.where(OrderLedger.soi_karigar.isnotnull())
			.where(OrderLedger.soi_karigar != "")
			.orderby(OrderLedger.soi_karigar, order=Order.asc)
		)
		karigars = [row[0] for row in karigar_query.run() if row[0]]

		# Get unique item groups (from soi_die field)
		item_group_query = (
			frappe.qb.from_(OrderLedger)
			.select(OrderLedger.soi_die)
			.distinct()
			.where(base_condition)
			.where(OrderLedger.soi_die.isnotnull())
			.where(OrderLedger.soi_die != "")
			.orderby(OrderLedger.soi_die, order=Order.asc)
		)
		item_groups = [row[0] for row in item_group_query.run() if row[0]]

		logger.debug(
			f"Filter options: {len(customers)} customers, {len(karigars)} karigars, {len(item_groups)} item_groups"
		)
		return {"customers": customers, "karigars": karigars, "item_groups": item_groups}

	except frappe.PermissionError:
		# Permission errors - let them through to user
		logger.warning(f"Permission denied in get_filter_options for user {frappe.session.user}")
		raise

	except Exception as e:
		# System error - log once (includes traceback)
		logger.error(f"get_filter_options API Failed: {e}. Traceback: {frappe.get_traceback()}")
		# Return empty lists - UI will still work
		return {"customers": [], "karigars": [], "item_groups": []}


@frappe.whitelist()
def update_item_status(
	item_names,
	new_status,
	karigar_received_weight=None,
	receive_notes=None,
	incoming_to_received=None,
	received_to_incoming=None,
	dispatch_weight=None,
	dispatch_notes=None,
	weight_per_unit=None,
	weight_field=None,
) -> list[dict]:
	"""
	Updates order_status for one or more Order Ledger entries.
	Applies transition side effects based on workflow logic.

	Returns:
		list[dict]: Results for each item with success status and error messages if any
	"""
	try:
		logger.info(
			f"update_item_status called: new_status={new_status}, items count={len(item_names) if isinstance(item_names, list) else 1}"
		)

		# Parse item_names if it's a JSON string
		if isinstance(item_names, str):
			item_names = frappe.parse_json(item_names)

		if not isinstance(item_names, list):
			item_names = [item_names]

		# Validate new_status against allowed workflow statuses
		allowed_statuses = _get_workflow_statuses()
		if new_status not in allowed_statuses:
			frappe.throw(f"Invalid status '{new_status}'. Must be one of: {', '.join(allowed_statuses)}")

		# Validate weight_per_unit if provided
		if weight_per_unit:
			try:
				weight_per_unit = float(weight_per_unit)
				if weight_per_unit <= 0:
					frappe.throw("Weight per unit must be a positive number.")
			except (ValueError, TypeError):
				frappe.throw("Invalid weight per unit value. Please enter a valid number.")

		# Prepare kwargs for transition handler
		transition_kwargs = {
			"karigar_received_weight": karigar_received_weight,
			"receive_notes": receive_notes,
			"incoming_to_received": incoming_to_received,
			"received_to_incoming": received_to_incoming,
			"dispatch_weight": dispatch_weight,
			"dispatch_notes": dispatch_notes,
			"weight_per_unit": weight_per_unit,
		}

		results = []
		total = len(item_names)
		success_count = 0

		# Process updates - Frappe handles transactions automatically per save()
		for idx, item_name in enumerate(item_names):
			try:
				# Get the order with for_update to lock row
				order = frappe.get_doc("Order Ledger", item_name, for_update=True)
				order.check_permission("write")

				current_status = order.get("order_status")

				# Apply bulk weight update if weight_per_unit and weight_field provided
				# This multiplies weight_per_unit by each order's qty to calculate total weight
				if weight_per_unit and weight_field:
					try:
						entry_qty = float(order.qty) if order.qty else 1
						entry_weight = entry_qty * weight_per_unit
						setattr(order, weight_field, entry_weight)
					except (ValueError, TypeError) as e:
						logger.warning(f"Invalid qty for weight calculation in {item_name}: {order.qty}")
						# Skip weight update for this entry but continue processing

				# Update status
				order.order_status = new_status

				# Apply transition side effects
				apply_status_transition_effects(order, current_status, new_status, transition_kwargs)

				# Save the order
				order.save()

				logger.debug(f"Successfully updated {item_name}: {current_status} → {new_status}")
				results.append({"name": item_name, "success": True, "new_status": new_status})
				success_count += 1

			except frappe.DoesNotExistError:
				# Order not found - user error
				logger.warning(f"Order not found: {item_name}")
				results.append(
					{"name": item_name, "success": False, "error": f"Order Ledger '{item_name}' not found."}
				)

			except frappe.PermissionError as e:
				# Permission denied - user error
				logger.warning(f"Permission denied for {item_name}: {e!s}")
				results.append({"name": item_name, "success": False, "error": "Permission denied."})

			except Exception as e:
				# System error - log it
				logger.error(
					f"Order Status Update Failed: {item_name}. "
					f"New Status: {new_status}. "
					f"Error: {e}. "
					f"Traceback: {frappe.get_traceback()}"
				)
				results.append({"name": item_name, "success": False, "error": str(e)})

			# Emit namespaced realtime progress event with success count
			frappe.publish_realtime(
				"ampower_kj:karigar_batch_progress",
				{
					"data_import": "karigar-dashboard",
					"current": idx + 1,
					"total": total,
					"success_count": success_count,
				},
				user=frappe.session.user,
			)

		# Log summary
		logger.info(f"update_item_status complete: {success_count}/{total} successful")
		return results

	except frappe.ValidationError:
		# User validation errors (invalid status, invalid weight) - let them through
		logger.warning(f"Validation error in update_item_status: {frappe.local.message_log!s}")
		raise

	except Exception as e:
		# Unexpected system error before loop
		logger.error(
			f"update_item_status API Failed: {e}. "
			f"New Status: {new_status}. "
			f"Traceback: {frappe.get_traceback()}"
		)
		frappe.throw("Failed to update order status. Please contact support.")


@frappe.whitelist()
def split_order_item(item_name: str, split_qty) -> dict:
	"""
	Splits an Order Ledger entry by updating the original and creating a new entry for the remainder.
	Example: Entry with 100 qty, user enters 60 → original becomes 60 qty, new entry created with 40 qty.

	Args:
		item_name: Name of the Order Ledger entry to split
		split_qty: Quantity to keep in the original entry (remaining goes to new entry)

	Returns:
		dict: Success status with original and new entry details
	"""
	try:
		logger.info(f"split_order_item called: item={item_name}, split_qty={split_qty}")

		# Get the original order
		original_order = frappe.get_doc("Order Ledger", item_name)
		original_order.check_permission("write")

		# Validate and convert split_qty
		try:
			split_qty = float(split_qty)
		except (ValueError, TypeError):
			frappe.throw("Invalid split quantity. Please enter a valid number.")

		# Validate original qty exists and is valid
		if not original_order.qty or float(original_order.qty) <= 0:
			frappe.throw("Cannot split order: original quantity is invalid or zero.")

		total_qty = float(original_order.qty)

		# Round to avoid floating point precision issues
		split_qty = round(split_qty, 3)
		total_qty = round(total_qty, 3)

		# Validate split quantity
		if split_qty <= 0:
			frappe.throw("Split quantity must be greater than 0.")

		if split_qty >= total_qty:
			frappe.throw("Split quantity must be less than total quantity.")
		# Calculate remaining quantity
		remaining_qty = total_qty - split_qty

		# Update original order with split quantity
		original_order.qty = split_qty
		split_note = f"\nSplit on {frappe.utils.now_datetime()} - kept {split_qty} qty, created new entry with {remaining_qty} qty"
		original_order.soi_customer_notes = (original_order.soi_customer_notes or "") +";" + split_note
		original_order.save()

		# Create new entry with remaining quantity
		remaining_entry = frappe.copy_doc(original_order)
		remaining_entry.name = None
		remaining_entry.qty = remaining_qty
		split_note_2 = f"\nSplit from {item_name} ({total_qty} qty) on {frappe.utils.now_datetime()} - remainder ({remaining_qty} qty)"
		# Preserve original notes and append split information
		remaining_entry.soi_customer_notes = (original_order.soi_customer_notes or "") +";" + split_note_2
		remaining_entry.insert()
		logger.info(
			f"Split successful: {item_name} -> {original_order.name} ({split_qty}) + {remaining_entry.name} ({remaining_qty})"
		)
		return {
			"success": True,
			"original_entry": item_name,
			"new_entry": remaining_entry.name,
			"original_qty": split_qty,
			"new_qty": remaining_qty,
			"message": f"Successfully split {item_name}: kept {split_qty} qty, created new entry with {remaining_qty} qty",
		}

	except frappe.DoesNotExistError:
		# Order not found
		logger.warning(f"Order not found for split: {item_name}")
		frappe.throw(f"Order Ledger '{item_name}' not found.")

	except frappe.PermissionError:
		# Permission denied
		logger.warning(f"Permission denied for split: {item_name}")
		raise

	except frappe.ValidationError:
		# User validation errors (invalid qty, etc) - let them through
		logger.warning(f"Validation error in split_order_item: {item_name}")
		raise

	except Exception as e:
		# Unexpected system error
		logger.error(
			f"Order Split Failed: {item_name}. "
			f"Split Qty: {split_qty}. "
			f"Error: {e}. "
			f"Traceback: {frappe.get_traceback()}"
		)
		frappe.throw("Failed to split order. Please contact support.")
