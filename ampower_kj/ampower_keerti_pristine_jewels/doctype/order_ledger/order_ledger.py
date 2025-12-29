import frappe
from frappe.model.document import Document


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


# Pagination limits
DEFAULT_PAGE_LIMIT = 100
KARIGAR_PAGE_LIMIT = 200


def get_workflow_stages():
	"""
	Get workflow stages dynamically from Order Ledger DocType metadata.
	Returns list of stage dictionaries with id, label, key, and status.
	Uses caching to avoid repeated DocType metadata queries.
	"""
	cache_key = "order_ledger_workflow_stages"
	stages = frappe.cache().get_value(cache_key)

	if stages:
		return stages

	# Get statuses from DocType field metadata
	statuses = get_workflow_status()

	# Build stages dynamically
	stages = []
	for idx, status in enumerate(statuses):
		# Convert status to key (e.g., "Internal QA" -> "internal_qa")
		key = status.lower().replace(" ", "_")
		stages.append({"id": idx + 1, "label": status, "key": key, "status": status})

	# Cache for 1 hour
	frappe.cache().set_value(cache_key, stages, expires_in_sec=3600)

	return stages


def enrich_order_data(orders):
	"""
	Enrich order data with customer and item details using bulk fetching.
	Solves N+1 query problem by fetching all related data in bulk.

	Args:
		orders: List of order dictionaries

	Returns:
		List of enriched order dictionaries
	"""
	if not orders:
		return orders

	# Extract unique sales orders and items
	sales_order_ids = {order.get("sales_order") for order in orders if order.get("sales_order")}
	item_ids = {order.get("item") for order in orders if order.get("item")}

	# Bulk fetch customers from sales orders
	customer_map = {}
	if sales_order_ids:
		sales_orders = frappe.get_all(
			"Sales Order", filters={"name": ["in", list(sales_order_ids)]}, fields=["name", "customer"]
		)
		customer_map = {so["name"]: so["customer"] for so in sales_orders}

	# Bulk fetch item details
	item_map = {}
	if item_ids:
		items = frappe.get_all(
			"Item", filters={"name": ["in", list(item_ids)]}, fields=["name", "item_group"]
		)
		item_map = {item["name"]: item for item in items}

	# Enrich each order
	for order in orders:
		# Add customer from sales order
		sales_order = order.get("sales_order")
		order["customer"] = customer_map.get(sales_order, "") if sales_order else ""

		# Add item details
		item_code = order.get("item")
		if item_code and item_code in item_map:
			item_data = item_map[item_code]
			order["item_code"] = item_code
			order["item_group"] = item_data.get("item_group", "")
		else:
			order["item_code"] = item_code or ""
			order["item_group"] = ""

		# Map fields for frontend compatibility
		order["our_details"] = order.get("order_weight", 0)
		order["smith_details"] = order.get("karigar_assigned_weight", 0)
		order["qty"] = order.get("qty", 1)
		order["parent"] = order.get("sales_order")
		order["doctype"] = "Order Ledger"

	return orders


def get_workflow_progression_map():
	"""
	Build workflow progression map dynamically from workflow statuses.
	Returns a dict mapping current status to next status.
	Assumes sequential workflow progression based on order of statuses.
	"""
	statuses = get_workflow_status()
	workflow_map = {}

	# Build sequential progression map (status[i] -> status[i+1])
	for i in range(len(statuses) - 1):
		workflow_map[statuses[i]] = statuses[i + 1]

	return workflow_map


def get_reverse_workflow_map():
	"""
	Build reverse workflow progression map dynamically from workflow statuses.
	Returns a dict mapping current status to previous status.
	"""
	statuses = get_workflow_status()
	reverse_map = {}

	# Build reverse progression map (status[i] -> status[i-1])
	for i in range(1, len(statuses)):
		reverse_map[statuses[i]] = statuses[i - 1]

	return reverse_map


def get_stage_filters(stage_key):
	"""Get frappe filters for a specific stage using order_status field."""
	filters = {"disabled": ["!=", 1]}  # Check field: 0 = not disabled

	# Build stage_to_status mapping dynamically from workflow statuses
	statuses = get_workflow_status()
	stage_to_status = {}
	for status in statuses:
		# Convert status to key (e.g., "Internal QA" -> "internal_qa")
		key = status.lower().replace(" ", "_")
		stage_to_status[key] = status

	# Use order_status field directly instead of deriving from date fields
	if stage_key in stage_to_status:
		filters["order_status"] = stage_to_status[stage_key]

	return filters


@frappe.whitelist()
def get_workflow_data(stage_key=None, search=None, karigar=None, customer=None, item_group=None):
	"""Get workflow stages with counts and orders for the selected stage."""

	# Get workflow stages dynamically
	workflow_stages = get_workflow_stages()

	# Get counts for each stage
	stages = []
	for stage in workflow_stages:
		filters = get_stage_filters(stage["key"])
		count = frappe.db.count("Order Ledger", filters=filters)
		stages.append(
			{
				"id": stage["id"],
				"label": stage["label"],
				"key": stage["key"],
				"count": count,
				"active": stage["key"] == stage_key,
			}
		)

	# Default to first stage with orders if no stage selected
	if not stage_key:
		for stage in stages:
			if stage["count"] > 0:
				stage_key = stage["key"]
				stage["active"] = True
				break
		if not stage_key:
			# Default to first stage key if no stages have orders
			stage_key = stages[0]["key"] if stages else "unassigned"
			if stages:
				stages[0]["active"] = True

	# Get orders for selected stage
	filters = get_stage_filters(stage_key)

	# Apply additional filters
	if karigar:
		filters["karigar"] = karigar
	if search:
		filters["name"] = ["like", f"%{search}%"]

	orders = frappe.get_all(
		"Order Ledger",
		filters=filters,
		fields=[
			"name",
			"sales_order",
			"item",
			"karigar",
			"order_weight",
			"karigar_assigned_weight",
			"order_date",
			"karigar_assignment_date",
			"karigar_incoming_date",
			"karigar_actual_receive_date",
			"is_qa_cleared",
			"actual_dispatch_date",
			"customer_notes",
		],
		order_by="modified desc",
		limit_page_length=DEFAULT_PAGE_LIMIT,
	)

	# Enrich orders
	# Get default status (first status in workflow)
	default_status = get_workflow_status()[0] if get_workflow_status() else ""

	for order in orders:
		# Use order_status directly instead of deriving from fields
		order["stage"] = order.get("order_status", default_status).lower().replace(" ", "_")
		order["customer_name"] = order.get("customer_notes", "")[:50] if order.get("customer_notes") else ""
		order["item_name"] = order.get("item") or ""

	# Get unique karigars from Order Ledger for filter dropdown (ORM only)
	karigars = frappe.get_all(
		"Order Ledger",
		filters={"karigar": ["is", "set"]},  # not null + not empty
		pluck="karigar",
		group_by="karigar",
		order_by="karigar asc",
	)

	return {
		"stages": stages,
		"orders": orders,
		"active_stage": stage_key,
		"filters": {"karigars": karigars, "customers": [], "item_groups": []},
	}


@frappe.whitelist()
def move_to_next_stage(order_name):
	"""Move an order to the next workflow stage."""
	order = frappe.get_doc("Order Ledger", order_name)
	order.check_permission("write")
	current_status = order.order_status

	# Get workflow progression map dynamically
	workflow_map = get_workflow_progression_map()

	# Get first status for validation
	statuses = get_workflow_status()
	first_status = statuses[0] if statuses else None

	if current_status not in workflow_map:
		frappe.throw(f"Cannot move from status: {current_status}")

	if current_status == first_status and not order.karigar:
		frappe.throw("Please assign a Karigar first before moving to next stage")

	# Get next status
	next_status = workflow_map[current_status]
	order.order_status = next_status

	# Set appropriate date fields (will be handled by before_save or update_item_status)
	today = frappe.utils.today()

	# Status index for progression logic
	current_idx = statuses.index(current_status)
	next_idx = statuses.index(next_status)

	# Handle status-specific field updates based on progression
	if current_idx == 0 and next_idx == 1:  # Unassigned -> Assigned
		if not order.karigar_assignment_date:
			order.karigar_assignment_date = today
	elif next_idx == 2:  # Moving to Incoming (index 2)
		if not order.karigar_incoming_date:
			order.karigar_incoming_date = today
	elif current_idx == 2 and next_idx == 3:  # Incoming -> Internal QA
		if not order.karigar_actual_receive_date:
			order.karigar_actual_receive_date = today
	elif current_idx == 3 and next_idx == 4:  # Internal QA -> Pending Delivery
		order.is_qa_cleared = 1
	elif current_idx == 4 and next_idx == 5:  # Pending Delivery -> Delivered
		if not order.actual_dispatch_date:
			order.actual_dispatch_date = today

	order.save()

	return {"success": True, "new_stage": next_status}


@frappe.whitelist()
def move_to_previous_stage(order_name):
	"""Move an order to the previous workflow stage."""
	order = frappe.get_doc("Order Ledger", order_name)
	order.check_permission("write")
	current_status = order.order_status

	# Get reverse workflow progression map dynamically
	reverse_workflow_map = get_reverse_workflow_map()

	# Get statuses for index-based logic
	statuses = get_workflow_status()

	if current_status not in reverse_workflow_map:
		frappe.throw(f"Cannot move back from status: {current_status}")

	# Get previous status
	prev_status = reverse_workflow_map[current_status]
	order.order_status = prev_status

	# Status index for regression logic
	current_idx = statuses.index(current_status)
	prev_idx = statuses.index(prev_status)

	# Clear appropriate fields when moving back
	if current_idx == 1 and prev_idx == 0:  # Assigned -> Unassigned
		order.karigar = None
		order.karigar_assignment_date = None
	elif current_idx == 2 and prev_idx == 1:  # Incoming -> Assigned
		order.karigar_incoming_date = None
	elif current_idx == 3 and prev_idx == 2:  # Internal QA -> Incoming
		order.karigar_actual_receive_date = None
		order.karigar_received_weight = None
	elif current_idx == 4 and prev_idx == 3:  # Pending Delivery -> Internal QA
		order.is_qa_cleared = 0
	elif current_idx == 5 and prev_idx == 4:  # Delivered -> Pending Delivery
		order.actual_dispatch_date = None
		order.dispatch_weight = None

	order.save()

	return {"success": True, "new_stage": prev_status}


@frappe.whitelist()
def bulk_move_to_next_stage(order_names):
	"""Move multiple orders to the next stage."""
	if isinstance(order_names, str):
		order_names = frappe.parse_json(order_names)

	results = []
	for name in order_names:
		try:
			result = move_to_next_stage(name)
			results.append({"name": name, "success": True, "new_stage": result["new_stage"]})
		except Exception as e:
			results.append({"name": name, "success": False, "error": str(e)})

	return results


@frappe.whitelist()
def update_order_details(order_name, weight=None, load=None):
	"""Update order weight and load without moving stages."""
	order = frappe.get_doc("Order Ledger", order_name)
	order.check_permission("write")

	if weight is not None:
		order.order_weight = weight
	if load is not None:
		order.karigar_assigned_weight = load

	order.save()

	return {"success": True, "message": "Order details updated successfully"}


@frappe.whitelist()
def update_and_move_to_next(order_name, weight=None, load=None):
	"""Update order weight/load and move to next stage."""
	# First update the details
	order = frappe.get_doc("Order Ledger", order_name)
	order.check_permission("write")

	if weight is not None:
		order.order_weight = weight
	if load is not None:
		order.karigar_assigned_weight = load

	order.save()

	# Then move to next stage
	result = move_to_next_stage(order_name)

	return {
		"success": True,
		"new_stage": result["new_stage"],
		"message": "Order updated and moved to next stage",
	}


@frappe.whitelist()
def get_workflow_status():
	"""
	Returns workflow status options from Order Ledger metadata.
	"""
	meta = frappe.get_meta("Order Ledger")
	field = meta.get_field("order_status")

	if not field:
		frappe.throw("Field 'order_status' not found in Order Ledger.")

	if field and field.fieldtype == "Select":
		return field.options.split("\n")
	return []


@frappe.whitelist()
def get_all_order_items(
	page=1, page_size=10, order_status=None, search=None, customer=None, karigar=None, item_group=None
):
	"""Fetches Order Ledger entries with server-side pagination and filtering."""
	from frappe.query_builder import DocType
	from frappe.query_builder.functions import Count
	from pypika import Order

	# Convert parameters
	page = int(page) if page else 1
	page_size = int(page_size) if page_size else 10

	# Define DocTypes
	OrderLedger = DocType("Order Ledger")
	SalesOrder = DocType("Sales Order")
	Item = DocType("Item")

	# Build base query with joins
	query = (
		frappe.qb.from_(OrderLedger)
		.left_join(SalesOrder)
		.on(OrderLedger.sales_order == SalesOrder.name)
		.left_join(Item)
		.on(OrderLedger.item == Item.name)
		.select(
			OrderLedger.name,
			OrderLedger.sales_order,
			OrderLedger.item,
			OrderLedger.customer_notes,
			OrderLedger.order_status,
			OrderLedger.karigar,
			OrderLedger.order_weight,
			OrderLedger.karigar_assigned_weight,
			OrderLedger.karigar_received_weight,
			OrderLedger.dispatch_weight,
			OrderLedger.karigar_notes,
			OrderLedger.qa_notes,
			OrderLedger.order_date,
			OrderLedger.qty,
			SalesOrder.customer,
			Item.item_group,
			Item.image

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
		query = query.where(OrderLedger.karigar == karigar)
		count_query = count_query.where(OrderLedger.karigar == karigar)

	if customer:
		query = query.where(SalesOrder.customer == customer)
		count_query = count_query.where(SalesOrder.customer == customer)

	if item_group:
		query = query.where(Item.item_group == item_group)
		count_query = count_query.where(Item.item_group == item_group)

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
		order["item_code"] = order.get("item") or ""
		order["our_details"] = order.get("order_weight", 0)
		order["smith_details"] = order.get("karigar_assigned_weight", 0)
		order["qty"] = order.get("qty", 1)
		order["parent"] = order.get("sales_order")
		order["doctype"] = "Order Ledger"
		if order.get("image"):
			order["item_image"] = order["image"]
		else:
			order["item_image"] = None

	return {
		"data": orders,
		"total": total_count,
		"page": page,
		"page_size": page_size,
		"total_pages": (total_count + page_size - 1) // page_size,  # Ceiling division
	}


@frappe.whitelist()
def get_status_counts(customer=None, karigar=None, item_group=None, search=None):
	"""Get count of orders for each status with optional filters."""
	from frappe.query_builder import DocType
	from frappe.query_builder.functions import Count

	statuses = get_workflow_status()
	counts = {}

	# Define DocTypes
	OrderLedger = DocType("Order Ledger")
	SalesOrder = DocType("Sales Order")
	Item = DocType("Item")

	for status in statuses:
		# Build count query with joins
		query = (
			frappe.qb.from_(OrderLedger)
			.left_join(SalesOrder)
			.on(OrderLedger.sales_order == SalesOrder.name)
			.left_join(Item)
			.on(OrderLedger.item == Item.name)
			.select(Count("*").as_("total"))
			.where(OrderLedger.disabled != 1)
			.where(OrderLedger.order_status == status)
		)

		# Apply filters
		if customer:
			query = query.where(SalesOrder.customer == customer)

		if karigar:
			query = query.where(OrderLedger.karigar == karigar)

		if item_group:
			query = query.where(Item.item_group == item_group)

		if search:
			search_condition = (
				(OrderLedger.name.like(f"%{search}%"))
				| (OrderLedger.sales_order.like(f"%{search}%"))
				| (OrderLedger.item.like(f"%{search}%"))
			)
			query = query.where(search_condition)

		# Execute query
		result = query.run(as_dict=True)
		counts[status] = result[0].total if result else 0

	return counts


@frappe.whitelist()
def get_filter_options():
	"""Get unique filter options for autocomplete (customers, karigars, item groups).

	Returns all options across all stages so filtering works regardless of current stage.
	"""
	from frappe.query_builder import DocType
	from pypika import Order

	# Define DocTypes
	OrderLedger = DocType("Order Ledger")
	SalesOrder = DocType("Sales Order")
	Item = DocType("Item")

	# Base condition
	base_condition = OrderLedger.disabled != 1

	# Get unique customers (from all stages)
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

	# Get unique karigars (from all stages)
	karigar_query = (
		frappe.qb.from_(OrderLedger)
		.select(OrderLedger.karigar)
		.distinct()
		.where(base_condition)
		.where(OrderLedger.karigar.isnotnull())
		.where(OrderLedger.karigar != "")
		.orderby(OrderLedger.karigar, order=Order.asc)
	)
	karigars = [row[0] for row in karigar_query.run() if row[0]]

	# Get unique item groups (from all stages)
	item_group_query = (
		frappe.qb.from_(OrderLedger)
		.left_join(Item)
		.on(OrderLedger.item == Item.name)
		.select(Item.item_group)
		.distinct()
		.where(base_condition)
		.where(Item.item_group.isnotnull())
		.where(Item.item_group != "")
		.orderby(Item.item_group, order=Order.asc)
	)
	item_groups = [row[0] for row in item_group_query.run() if row[0]]

	return {"customers": customers, "karigars": karigars, "item_groups": item_groups}


@frappe.whitelist()
def get_order_items_by_karigar(karigar, customer=None, item_group=None):
	"""Fetches all Order Ledger entries for a specific karigar with enriched data."""
	if not karigar:
		frappe.throw("Karigar is required")

	# Build filters
	filters = {"karigar": karigar, "disabled": ["!=", 1]}

	# Fetch Order Ledger records
	orders = frappe.get_all(
		"Order Ledger",
		filters=filters,
		fields=[
			"name",
			"sales_order",
			"item",
			"customer_notes",
			"order_status",
			"karigar",
			"order_weight",
			"karigar_assigned_weight",
			"karigar_received_weight",
			"karigar_notes",
			"order_date",
			"qty",
		],
		order_by="modified desc",
		limit_page_length=KARIGAR_PAGE_LIMIT,
	)

	# Enrich data with linked records using bulk fetching (solves N+1 problem)
	return enrich_order_data(orders)


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
):
	"""Updates order_status for one or more Order Ledger entries."""
	# Parse item_names if it's a JSON string
	if isinstance(item_names, str):
		item_names = frappe.parse_json(item_names)

	if not isinstance(item_names, list):
		item_names = [item_names]

	# Validate new_status against allowed workflow statuses
	allowed_statuses = get_workflow_status()
	if new_status not in allowed_statuses:
		frappe.throw(f"Invalid status '{new_status}'. Must be one of: {', '.join(allowed_statuses)}")

	# Validate weight_per_unit if provided
	if weight_per_unit:
		try:
			weight_per_unit = float(weight_per_unit)
			if weight_per_unit < 0:
				frappe.throw("Weight per unit must be a positive number")
		except (ValueError, TypeError):
			frappe.throw("Invalid weight per unit. Please enter a valid number.")

	results = []
	total = len(item_names)

	for idx, item_name in enumerate(item_names):
		try:
			# Get the order
			order = frappe.get_doc("Order Ledger", item_name)
			order.check_permission("write")

			current_status = order.get("order_status")

			# Update status
			order.order_status = new_status

			# Apply bulk weight update if weight_per_unit and weight_field are provided
			# Calculate weight for this entry based on its quantity
			if weight_per_unit and weight_field:
				entry_qty = float(order.qty) if order.qty else 1
				entry_weight = entry_qty * weight_per_unit
				setattr(order, weight_field, entry_weight)

			# Get statuses for index-based transition logic
			statuses = allowed_statuses

			# Get indices for current and new status
			try:
				current_idx = statuses.index(current_status) if current_status in statuses else -1
				new_idx = statuses.index(new_status)
			except ValueError:
				# If status not found, skip transition logic
				current_idx = -1
				new_idx = -1

			# Auto-assign dates based on status transitions
			# Use index-based logic to avoid hardcoded status names
			if current_idx == 0 and new_idx == 1:  # Unassigned -> Assigned
				if not order.karigar_assignment_date:
					order.karigar_assignment_date = frappe.utils.today()

			if new_idx == 2:  # Moving to Incoming
				if not order.karigar_incoming_date:
					order.karigar_incoming_date = frappe.utils.today()

			if current_idx == 2 and new_idx == 3:  # Incoming -> Internal QA
				if not order.karigar_actual_receive_date:
					order.karigar_actual_receive_date = frappe.utils.today()

			if current_idx == 3 and new_idx == 4:  # Internal QA -> Pending Delivery
				order.is_qa_cleared = 1

			if current_idx == 4 and new_idx == 5:  # Pending Delivery -> Delivered
				if not order.actual_dispatch_date:
					order.actual_dispatch_date = frappe.utils.today()

			# Special handling for Incoming → Internal QA (weight and notes)
			if current_idx == 2 and new_idx == 3:  # Incoming -> Internal QA
				if karigar_received_weight and not weight_per_unit:
					order.karigar_received_weight = float(karigar_received_weight)
				if receive_notes:
					order.karigar_notes = receive_notes
				# Allow manual override of receive date if provided
				if incoming_to_received:
					order.karigar_actual_receive_date = incoming_to_received

			# Special handling for Internal QA → Incoming (revert)
			elif current_idx == 3 and new_idx == 2:  # Internal QA -> Incoming
				order.karigar_received_weight = None
				order.karigar_actual_receive_date = None
				if received_to_incoming:
					revert_note = f"\nReverted from {statuses[3]} at {received_to_incoming}"
					order.karigar_notes = (order.karigar_notes or "") + revert_note

			# Special handling for Pending Delivery → Delivered (weight and QA notes)
			elif current_idx == 4 and new_idx == 5:  # Pending Delivery -> Delivered
				if dispatch_weight and not weight_per_unit:
					order.dispatch_weight = float(dispatch_weight)
				# QA notes are captured when moving to Delivered
				if dispatch_notes:
					order.qa_notes = dispatch_notes

			# Save the order
			order.save()

			results.append({"name": item_name, "success": True, "new_status": new_status})

		except Exception as e:
			results.append({"name": item_name, "success": False, "error": str(e)})

		# Emit namespaced realtime progress event
		frappe.publish_realtime(
			"ampower_kj:karigar_batch_progress",
			{"data_import": "karigar-dashboard", "current": idx + 1, "total": total},
			user=frappe.session.user,
		)

	return results


@frappe.whitelist()
def split_order_item(item_name, split_qty):
	"""
	Splits an Order Ledger entry into two entries.
	Example: Entry with 100 qty, user enters 60 → creates 60 qty and 40 qty entries.

	Args:
		item_name: Name of the Order Ledger entry to split
		split_qty: Quantity for the first split entry (remaining goes to second entry)

	Returns:
		dict: Success status and list of new entry names or error message
	"""
	# Get the original order
	original_order = frappe.get_doc("Order Ledger", item_name)
	original_order.check_permission("write")

	# Validate and convert split_qty
	try:
		split_qty = float(split_qty)
	except (ValueError, TypeError):
		frappe.throw("Invalid split quantity. Please enter a valid number.")

	total_qty = float(original_order.qty or 1)

	# Validate split quantity
	if split_qty <= 0:
		frappe.throw("Split quantity must be greater than 0")

	if split_qty >= total_qty:
		frappe.throw("Split quantity must be less than total quantity")

	# Calculate remaining quantity
	remaining_qty = total_qty - split_qty

	# Create first entry with split_qty
	first_entry = frappe.copy_doc(original_order)
	first_entry.name = None
	first_entry.qty = split_qty
	split_note_1 = f"\nSplit from {item_name} ({total_qty} qty) on {frappe.utils.now_datetime()} - Part 1 of 2 ({split_qty} qty)"
	first_entry.customer_notes = (first_entry.customer_notes or "") + split_note_1
	first_entry.insert()

	# Create second entry with remaining_qty
	second_entry = frappe.copy_doc(original_order)
	second_entry.name = None
	second_entry.qty = remaining_qty
	split_note_2 = f"\nSplit from {item_name} ({total_qty} qty) on {frappe.utils.now_datetime()} - Part 2 of 2 ({remaining_qty} qty)"
	second_entry.customer_notes = (second_entry.customer_notes or "") + split_note_2
	second_entry.insert()

	# Delete the original order
	original_order.delete()

	# Frappe will auto-commit at the end of the request
	# No manual commit needed - this allows proper rollback on errors

	return {
		"success": True,
		"original_entry": item_name,
		"new_entries": [first_entry.name, second_entry.name],
		"first_entry": {"name": first_entry.name, "qty": split_qty},
		"second_entry": {"name": second_entry.name, "qty": remaining_qty},
		"message": f"Successfully split {item_name} ({total_qty} qty) into {split_qty} and {remaining_qty}",
	}
