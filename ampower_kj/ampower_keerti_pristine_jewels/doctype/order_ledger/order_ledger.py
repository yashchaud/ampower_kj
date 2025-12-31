import frappe
from frappe.model.document import Document
from typing import List, Dict, Optional


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

# Cache keys
CACHE_KEY_WORKFLOW_STATUSES = "order_ledger_workflow_statuses"
CACHE_KEY_WORKFLOW_STAGES = "order_ledger_workflow_stages"
CACHE_EXPIRY = 3600  


# WORKFLOW STATUS HELPERS

def _get_workflow_status_cached() -> List[str]:
	"""
	Returns workflow status options from Order Ledger metadata.
	Cached to avoid repeated DocType queries.
	Internal use only - use get_workflow_status() for public API.
	"""
	cache_key = CACHE_KEY_WORKFLOW_STATUSES
	statuses = frappe.cache().get_value(cache_key)

	if statuses:
		return statuses

	meta = frappe.get_meta("Order Ledger")
	field = meta.get_field("order_status")

	if not field:
		frappe.throw("Field 'order_status' not found in Order Ledger DocType.")

	if field.fieldtype != "Select":
		frappe.throw(f"Field 'order_status' must be of type Select, found {field.fieldtype}")

	statuses = [s.strip() for s in field.options.split("\n") if s.strip()]

	if not statuses:
		frappe.throw("No workflow statuses defined in order_status field")

	# Cache for 1 hour
	frappe.cache().set_value(cache_key, statuses, expires_in_sec=CACHE_EXPIRY)

	return statuses


def status_to_key(status: str) -> str:
	"""
	Convert status label to key (e.g., "Internal QA" -> "internal_qa").
	Centralized to avoid duplication.
	"""
	return status.lower().replace(" ", "_")


def key_to_status(key: str, statuses: Optional[List[str]] = None) -> Optional[str]:
	"""
	Convert key to status label (e.g., "internal_qa" -> "Internal QA").
	Returns None if not found.
	"""
	if statuses is None:
		statuses = _get_workflow_status_cached()

	for status in statuses:
		if status_to_key(status) == key:
			return status
	return None


def get_workflow_stages() -> List[Dict]:
	"""
	Get workflow stages dynamically from Order Ledger DocType metadata.
	Returns list of stage dictionaries with id, label, key, and status.
	Uses caching to avoid repeated queries.
	"""
	cache_key = CACHE_KEY_WORKFLOW_STAGES
	stages = frappe.cache().get_value(cache_key)

	if stages:
		return stages

	# Get statuses (cached)
	statuses = _get_workflow_status_cached()

	# Build stages dynamically
	stages = [
		{
			"id": idx + 1,
			"label": status,
			"key": status_to_key(status),
			"status": status
		}
		for idx, status in enumerate(statuses)
	]

	# Cache for 1 hour
	frappe.cache().set_value(cache_key, stages, expires_in_sec=CACHE_EXPIRY)

	return stages


def get_status_index(status: str, statuses: Optional[List[str]] = None) -> int:
	"""
	Get zero-based index of a status in workflow.
	Returns -1 if not found.
	"""
	if statuses is None:
		statuses = _get_workflow_status_cached()

	try:
		return statuses.index(status)
	except ValueError:
		return -1


def get_workflow_progression_map() -> Dict[str, str]:
	"""
	Build workflow progression map dynamically from workflow statuses.
	Returns a dict mapping current status to next status.
	"""
	statuses = _get_workflow_status_cached()
	return {statuses[i]: statuses[i + 1] for i in range(len(statuses) - 1)}


def get_reverse_workflow_map() -> Dict[str, str]:
	"""
	Build reverse workflow progression map dynamically from workflow statuses.
	Returns a dict mapping current status to previous status.
	"""
	statuses = _get_workflow_status_cached()
	return {statuses[i]: statuses[i - 1] for i in range(1, len(statuses))}


def get_stage_filters(stage_key: str) -> Dict:
	"""Get frappe filters for a specific stage using order_status field."""
	filters = {"disabled": ["!=", 1]}

	# Convert key to status
	status = key_to_status(stage_key)
	if status:
		filters["order_status"] = status

	return filters


# TRANSITION LOGIC (Centralized & Maintainable)

def apply_status_transition_effects(
	order: Document,
	current_status: str,
	new_status: str,
	kwargs: Optional[Dict] = None
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

	statuses = _get_workflow_status_cached()
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

		# Handle weight and notes for receiving
		if kwargs.get("karigar_received_weight") and not kwargs.get("weight_per_unit"):
			order.karigar_received_weight = float(kwargs["karigar_received_weight"])

		if kwargs.get("receive_notes"):
			order.karigar_notes = kwargs["receive_notes"]

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
		if kwargs.get("dispatch_weight") and not kwargs.get("weight_per_unit"):
			order.dispatch_weight = float(kwargs["dispatch_weight"])

		if kwargs.get("dispatch_notes"):
			order.qa_notes = kwargs["dispatch_notes"]

	# ========== REVERSE TRANSITIONS (Revert/Undo) ==========

	# Transition 3→2: Internal QA → Incoming (Revert receiving)
	if current_idx == 3 and new_idx == 2:
		order.karigar_received_weight = None
		order.karigar_actual_receive_date = None

		if kwargs.get("received_to_incoming"):
			revert_note = f"\nReverted from {statuses[3]} at {kwargs['received_to_incoming']}"
			order.karigar_notes = (order.karigar_notes or "") + revert_note


# API ENDPOINTS
 
@frappe.whitelist()
def get_workflow_status():
	"""
	Public API to get workflow statuses.
	Returns workflow status options from Order Ledger metadata.
	"""
	return _get_workflow_status_cached()


@frappe.whitelist()
def get_all_order_items(
	page=1,
	page_size=10,
	order_status=None,
	search=None,
	customer=None,
	karigar=None,
	item_group=None
) -> Dict:
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
	SalesOrderItem = DocType("Sales Order Item")

	# Build base query with joins
	query = (
		frappe.qb.from_(OrderLedger)
		.left_join(SalesOrder).on(OrderLedger.sales_order == SalesOrder.name)
		.left_join(Item).on(OrderLedger.item == Item.name)
		.left_join(SalesOrderItem).on(OrderLedger.sales_order_item == SalesOrderItem.name)
		.select(
			OrderLedger.name,
			OrderLedger.sales_order,
			OrderLedger.item,
 			OrderLedger.order_status,
			OrderLedger.karigar,
 			OrderLedger.karigar_assigned_weight,
			OrderLedger.karigar_received_weight,
			OrderLedger.dispatch_weight,
 			OrderLedger.qa_notes,
			OrderLedger.order_date,
			OrderLedger.qty,
 			OrderLedger.planned_dispatch_date,
			SalesOrder.customer,
			Item.item_group,
			Item.image,
			SalesOrderItem.custom_sales_order_image,
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
		.left_join(SalesOrder).on(OrderLedger.sales_order == SalesOrder.name)
		.left_join(Item).on(OrderLedger.item == Item.name)
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
		order["qty"] = order.get("qty", 1)
		order["parent"] = order.get("sales_order")
		order["doctype"] = "Order Ledger"

		# Build images array (Sales Order Item image + Item master image)
		images = []
		if order.get("custom_sales_order_image"):
			images.append(order["custom_sales_order_image"])
		if order.get("image"):
			images.append(order["image"])
		order["images"] = images
		order["item_image"] = images[0] if images else None

		# Prioritize SOI fields over Order Ledger fields when they have values
		# Use soi_order_weight if available, otherwise fall back to order_weight
		if order.get("soi_order_weight") is not None:
			order["item_weight"] = order.get("soi_order_weight")
		else:
			order["item_weight"] = order.get("order_weight")

		# Use soi_karigar if available, otherwise fall back to karigar
		if order.get("soi_karigar") is not None:
			order["karigar"] = order.get("soi_karigar")

		# Use soi_die if available, otherwise fall back to die/item_group
		if order.get("soi_die") is not None:
			order["item_group"] = order.get("soi_die")

		# Use soi_karigar_notes if available, otherwise fall back to karigar_notes
		if order.get("soi_karigar_notes") is not None:
			order["karigar_notes"] = order.get("soi_karigar_notes")

		# Use soi_customer_notes if available, otherwise fall back to customer_notes
		if order.get("soi_customer_notes") is not None:
			order["customer_notes"] = order.get("soi_customer_notes")

		# Use soi_planned_dispatch_date if available, otherwise fall back to planned_dispatch_date
		if order.get("soi_planned_dispatch_date") is not None:
			order["planned_dispatch_date"] = order.get("soi_planned_dispatch_date")

	return {
		"data": orders,
		"total": total_count,
		"page": page,
		"page_size": page_size,
		"total_pages": (total_count + page_size - 1) // page_size,
	}


@frappe.whitelist()
def get_status_counts(
	customer=None,
	karigar=None,
	item_group=None,
	search=None
) -> Dict[str, int]:
	"""Get count of orders for each status with optional filters."""
	from frappe.query_builder import DocType
	from frappe.query_builder.functions import Count

	statuses = _get_workflow_status_cached()
	counts = {}

	# Define DocTypes
	OrderLedger = DocType("Order Ledger")
	SalesOrder = DocType("Sales Order")
	Item = DocType("Item")

	for status in statuses:
		# Build count query with joins
		query = (
			frappe.qb.from_(OrderLedger)
			.left_join(SalesOrder).on(OrderLedger.sales_order == SalesOrder.name)
			.left_join(Item).on(OrderLedger.item == Item.name)
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
def get_filter_options() -> Dict[str, List[str]]:
	"""
	Get unique filter options for autocomplete (customers, karigars, item groups).
	Returns all options across all stages so filtering works regardless of current stage.
	"""
	from frappe.query_builder import DocType
	from pypika import Order

	# Define DocTypes
	OrderLedger = DocType("Order Ledger")
	SalesOrder = DocType("Sales Order")
	Item = DocType("Item")

	base_condition = OrderLedger.disabled != 1

	# Get unique customers
	customer_query = (
		frappe.qb.from_(OrderLedger)
		.left_join(SalesOrder).on(OrderLedger.sales_order == SalesOrder.name)
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
		.select(OrderLedger.karigar)
		.distinct()
		.where(base_condition)
		.where(OrderLedger.karigar.isnotnull())
		.where(OrderLedger.karigar != "")
		.orderby(OrderLedger.karigar, order=Order.asc)
	)
	karigars = [row[0] for row in karigar_query.run() if row[0]]

	# Get unique item groups
	item_group_query = (
		frappe.qb.from_(OrderLedger)
		.left_join(Item).on(OrderLedger.item == Item.name)
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
) -> List[Dict]:
	"""
	Updates order_status for one or more Order Ledger entries.
	Applies transition side effects based on workflow logic.
	"""
	# Parse item_names if it's a JSON string
	if isinstance(item_names, str):
		item_names = frappe.parse_json(item_names)

	if not isinstance(item_names, list):
		item_names = [item_names]

	# Validate new_status against allowed workflow statuses
	allowed_statuses = _get_workflow_status_cached()
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

	for idx, item_name in enumerate(item_names):
		try:
			# Get the order
			order = frappe.get_doc("Order Ledger", item_name)
			order.check_permission("write")

			current_status = order.get("order_status")

			# Apply bulk weight update if weight_per_unit and weight_field provided
			if weight_per_unit and weight_field:
				entry_qty = float(order.qty) if order.qty else 1
				entry_weight = entry_qty * weight_per_unit
				setattr(order, weight_field, entry_weight)

			# Update status
			order.order_status = new_status

			# Apply transition side effects
			apply_status_transition_effects(order, current_status, new_status, transition_kwargs)

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
def split_order_item(item_name: str, split_qty) -> Dict:
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

	return {
		"success": True,
		"original_entry": item_name,
		"new_entries": [first_entry.name, second_entry.name],
		"first_entry": {"name": first_entry.name, "qty": split_qty},
		"second_entry": {"name": second_entry.name, "qty": remaining_qty},
		"message": f"Successfully split {item_name} ({total_qty} qty) into {split_qty} and {remaining_qty}",
	}
