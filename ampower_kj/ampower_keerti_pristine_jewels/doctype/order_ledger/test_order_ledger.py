import frappe
import unittest
from frappe.utils import today, add_days
from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
	get_workflow_stages,
	get_workflow_progression_map,
	get_reverse_workflow_map,
	status_to_key,
	key_to_status,
	get_status_index,
	get_stage_filters,
	apply_status_transition_effects,
	_get_workflow_status_cached,
	CACHE_KEY_WORKFLOW_STATUSES,
	CACHE_KEY_WORKFLOW_STAGES,
)


class TestOrderLedger(unittest.TestCase):
	"""Test suite for Order Ledger DocType and related functionality.

	Uses standard unittest.TestCase for compatibility across all Frappe versions.
	Tests are isolated using database rollback in tearDown.
	"""

	@classmethod
	def setUpClass(cls):
		"""Set up test fixtures that are reused across tests."""
		super().setUpClass()
		frappe.set_user("Administrator")

		# Use existing data from database
		cls._setup_existing_data()

	@classmethod
	def _setup_existing_data(cls):
		"""Find existing data to use for tests."""
		# Find existing customer
		cls.test_customer = frappe.db.get_value("Customer", {}, "name")

		# Find existing supplier
		cls.test_supplier = frappe.db.get_value("Supplier", {}, "name")

		# Find existing item
		cls.test_item = frappe.db.get_value("Item", {}, "name")

		# Find existing sales order
		cls.test_sales_order = frappe.db.get_value(
			"Sales Order", {"docstatus": ["<", 2]}, "name"
		)
		cls.test_sales_order_item = None
		if cls.test_sales_order:
			cls.test_sales_order_item = frappe.db.get_value(
				"Sales Order Item", {"parent": cls.test_sales_order}, "name"
			)

	def setUp(self):
		"""Set up test data before each test."""
		# Clear cache before each test
		frappe.cache().delete_value(CACHE_KEY_WORKFLOW_STATUSES)
		frappe.cache().delete_value(CACHE_KEY_WORKFLOW_STAGES)
		frappe.set_user("Administrator")

	def tearDown(self):
		"""Clean up after each test."""
		# Clear cache after each test
		frappe.cache().delete_value(CACHE_KEY_WORKFLOW_STATUSES)
		frappe.cache().delete_value(CACHE_KEY_WORKFLOW_STAGES)

		# Rollback any database changes made during test
		frappe.db.rollback()

	def create_test_order_ledger(self, **kwargs):
		"""Helper to create test Order Ledger entry."""
		defaults = {
			"doctype": "Order Ledger",
			"sales_order": self.test_sales_order,
			"sales_order_item": self.test_sales_order_item,
			"item": self.test_item,
			"order_date": today(),
			"qty": 1,
			"order_status": "Unassigned"
		}
		defaults.update(kwargs)

		order = frappe.get_doc(defaults)
		order.insert(ignore_permissions=True)
		return order

	# ========== DOCUMENT LIFECYCLE TESTS ==========

	def test_before_save_auto_fill_qty_from_sales_order_item(self):
		"""Test qty auto-fill from Sales Order Item when qty is not set."""
		if not self.test_sales_order_item:
			self.skipTest("No Sales Order Item available for testing")

		# Get the actual qty from the Sales Order Item
		expected_qty = frappe.db.get_value(
			"Sales Order Item", self.test_sales_order_item, "qty"
		)
		if not expected_qty:
			self.skipTest("Sales Order Item has no qty")

		# Create order with qty explicitly set to 0/None to trigger auto-fill
		# Note: The DocType has default qty=1, so we must explicitly clear it
		order = frappe.get_doc({
			"doctype": "Order Ledger",
			"sales_order": self.test_sales_order,
			"sales_order_item": self.test_sales_order_item,
			"item": self.test_item,
			"order_date": today(),
			"qty": 0  # Explicitly set to 0 to trigger auto-fill
		})
		order.insert(ignore_permissions=True)

		# Should auto-fill qty from Sales Order Item
		self.assertEqual(order.qty, expected_qty)

	def test_before_save_default_qty_to_one(self):
		"""Test qty defaults to 1 when not set and no Sales Order Item."""
		order = frappe.get_doc({
			"doctype": "Order Ledger",
			"sales_order": self.test_sales_order,
			"item": self.test_item,
			"order_date": today()
		})
		order.insert(ignore_permissions=True)

		# Should default to 1
		self.assertEqual(order.qty, 1)

	# ========== WORKFLOW STATUS TESTS ==========

	def test_get_workflow_status_cached(self):
		"""Test workflow status retrieval and caching."""
		statuses = _get_workflow_status_cached()

		self.assertIsInstance(statuses, list)
		self.assertGreater(len(statuses), 0)
		self.assertIn("Unassigned", statuses)
		self.assertIn("Assigned", statuses)
		self.assertIn("Incoming", statuses)
		self.assertIn("Internal QA", statuses)
		self.assertIn("Pending Delivery", statuses)
		self.assertIn("Delivered", statuses)

		# Verify caching works by calling again and ensuring same result
		statuses_again = _get_workflow_status_cached()
		self.assertEqual(statuses, statuses_again)

	def test_status_to_key_conversion(self):
		"""Test status label to key conversion."""
		self.assertEqual(status_to_key("Internal QA"), "internal_qa")
		self.assertEqual(status_to_key("Pending Delivery"), "pending_delivery")
		self.assertEqual(status_to_key("Unassigned"), "unassigned")

	def test_key_to_status_conversion(self):
		"""Test key to status label conversion."""
		statuses = _get_workflow_status_cached()
		self.assertEqual(key_to_status("internal_qa", statuses), "Internal QA")
		self.assertEqual(key_to_status("pending_delivery", statuses), "Pending Delivery")
		self.assertIsNone(key_to_status("invalid_key", statuses))

	def test_get_status_index(self):
		"""Test status index retrieval."""
		statuses = _get_workflow_status_cached()
		self.assertEqual(get_status_index("Unassigned", statuses), 0)
		self.assertEqual(get_status_index("Assigned", statuses), 1)
		self.assertEqual(get_status_index("Invalid Status", statuses), -1)

	def test_get_workflow_stages(self):
		"""Test workflow stages generation and caching."""
		stages = get_workflow_stages()

		self.assertIsInstance(stages, list)
		self.assertGreater(len(stages), 0)

		# Check first stage structure
		first_stage = stages[0]
		self.assertIn("id", first_stage)
		self.assertIn("label", first_stage)
		self.assertIn("key", first_stage)
		self.assertIn("status", first_stage)
		self.assertEqual(first_stage["id"], 1)
		self.assertEqual(first_stage["label"], "Unassigned")

		# Verify caching works by calling again and ensuring same result
		stages_again = get_workflow_stages()
		self.assertEqual(stages, stages_again)

	def test_get_workflow_progression_map(self):
		"""Test workflow progression mapping."""
		progression_map = get_workflow_progression_map()

		self.assertIsInstance(progression_map, dict)
		self.assertEqual(progression_map.get("Unassigned"), "Assigned")
		self.assertEqual(progression_map.get("Assigned"), "Incoming")
		self.assertEqual(progression_map.get("Incoming"), "Internal QA")
		# Last status should not have next status
		self.assertNotIn("Delivered", progression_map)

	def test_get_reverse_workflow_map(self):
		"""Test reverse workflow mapping."""
		reverse_map = get_reverse_workflow_map()

		self.assertIsInstance(reverse_map, dict)
		self.assertEqual(reverse_map.get("Assigned"), "Unassigned")
		self.assertEqual(reverse_map.get("Incoming"), "Assigned")
		self.assertEqual(reverse_map.get("Internal QA"), "Incoming")
		# First status should not have previous status
		self.assertNotIn("Unassigned", reverse_map)

	def test_get_stage_filters(self):
		"""Test stage filter generation."""
		filters = get_stage_filters("internal_qa")

		self.assertIsInstance(filters, dict)
		self.assertEqual(filters.get("order_status"), "Internal QA")
		self.assertEqual(filters.get("disabled"), ["!=", 1])

		# Test invalid stage key
		invalid_filters = get_stage_filters("invalid_key")
		self.assertNotIn("order_status", invalid_filters)

	# ========== STATUS TRANSITION TESTS ==========

	def test_transition_unassigned_to_assigned(self):
		"""Test Unassigned → Assigned transition sets karigar_assignment_date."""
		order = self.create_test_order_ledger(order_status="Unassigned")

		apply_status_transition_effects(order, "Unassigned", "Assigned")

		self.assertEqual(order.karigar_assignment_date, today())

	def test_transition_to_incoming(self):
		"""Test transition to Incoming sets karigar_incoming_date."""
		order = self.create_test_order_ledger(order_status="Assigned")

		apply_status_transition_effects(order, "Assigned", "Incoming")

		self.assertEqual(order.karigar_incoming_date, today())

	def test_transition_incoming_to_internal_qa(self):
		"""Test Incoming → Internal QA transition with weight and notes."""
		order = self.create_test_order_ledger(order_status="Incoming")

		kwargs = {
			"karigar_received_weight": "25.5",
			"receive_notes": "Received in good condition"
		}

		apply_status_transition_effects(order, "Incoming", "Internal QA", kwargs)

		self.assertEqual(order.karigar_actual_receive_date, today())
		self.assertEqual(order.karigar_received_weight, 25.5)
		self.assertEqual(order.soi_karigar_notes, "Received in good condition")

	def test_transition_incoming_to_internal_qa_with_custom_date(self):
		"""Test Incoming → Internal QA with custom receive date."""
		order = self.create_test_order_ledger(order_status="Incoming")

		custom_date = add_days(today(), -2)
		kwargs = {"incoming_to_received": custom_date}

		apply_status_transition_effects(order, "Incoming", "Internal QA", kwargs)

		self.assertEqual(order.karigar_actual_receive_date, custom_date)

	def test_transition_internal_qa_to_pending_delivery(self):
		"""Test Internal QA → Pending Delivery sets is_qa_cleared."""
		order = self.create_test_order_ledger(order_status="Internal QA")

		apply_status_transition_effects(order, "Internal QA", "Pending Delivery")

		self.assertEqual(order.is_qa_cleared, 1)

	def test_transition_pending_delivery_to_delivered(self):
		"""Test Pending Delivery → Delivered with dispatch details."""
		order = self.create_test_order_ledger(order_status="Pending Delivery")

		kwargs = {
			"dispatch_weight": "24.8",
			"dispatch_notes": "QA passed, dispatched"
		}

		apply_status_transition_effects(order, "Pending Delivery", "Delivered", kwargs)

		self.assertEqual(order.actual_dispatch_date, today())
		self.assertEqual(order.dispatch_weight, 24.8)
		self.assertEqual(order.qa_notes, "QA passed, dispatched")

	def test_transition_internal_qa_to_incoming_revert(self):
		"""Test Internal QA → Incoming revert clears receive data."""
		order = self.create_test_order_ledger(
			order_status="Internal QA",
			karigar_received_weight=25.5,
			karigar_actual_receive_date=today()
		)

		kwargs = {"received_to_incoming": today()}

		apply_status_transition_effects(order, "Internal QA", "Incoming", kwargs)

		self.assertIsNone(order.karigar_received_weight)
		self.assertIsNone(order.karigar_actual_receive_date)
		self.assertIn("Reverted from Internal QA", order.soi_karigar_notes or "")

	def test_transition_with_weight_per_unit_not_applied(self):
		"""Test weight is not set when weight_per_unit is provided."""
		order = self.create_test_order_ledger(order_status="Incoming")

		# When weight_per_unit is provided, individual weight should not be set
		kwargs = {
			"karigar_received_weight": "25.5",
			"weight_per_unit": "5.0"
		}

		apply_status_transition_effects(order, "Incoming", "Internal QA", kwargs)

		# Weight should not be set because weight_per_unit is present
		self.assertIsNone(order.karigar_received_weight)

	# ========== API ENDPOINT TESTS ==========

	def test_get_workflow_status_api(self):
		"""Test get_workflow_status API endpoint."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_workflow_status
		)

		statuses = get_workflow_status()

		self.assertIsInstance(statuses, list)
		self.assertIn("Unassigned", statuses)
		self.assertIn("Delivered", statuses)

	def test_get_all_order_items_basic(self):
		"""Test get_all_order_items API with basic pagination."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		# Create multiple test orders
		for i in range(5):
			self.create_test_order_ledger(order_status="Unassigned")

		result = get_all_order_items(page=1, page_size=3)

		self.assertIn("data", result)
		self.assertIn("total", result)
		self.assertIn("page", result)
		self.assertIn("page_size", result)
		self.assertEqual(result["page"], 1)
		self.assertEqual(result["page_size"], 3)
		self.assertGreater(result["total"], 0)
		self.assertLessEqual(len(result["data"]), 3)

	def test_get_all_order_items_with_filters(self):
		"""Test get_all_order_items API with filters."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		# Create orders with different statuses
		self.create_test_order_ledger(order_status="Unassigned")
		self.create_test_order_ledger(order_status="Assigned")

		result = get_all_order_items(
			page=1,
			page_size=10,
			order_status="Unassigned"
		)

		# All returned orders should have Unassigned status
		for order in result["data"]:
			self.assertEqual(order["order_status"], "Unassigned")

	def test_get_all_order_items_with_search(self):
		"""Test get_all_order_items API with search."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		order = self.create_test_order_ledger()

		result = get_all_order_items(
			page=1,
			page_size=10,
			search=self.test_sales_order
		)

		self.assertGreater(len(result["data"]), 0)
		# At least one result should match the search
		found = False
		for item in result["data"]:
			if self.test_sales_order in item.get("sales_order", ""):
				found = True
				break
		self.assertTrue(found)

	def test_get_status_counts(self):
		"""Test get_status_counts API endpoint."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_status_counts
		)

		# Create orders with different statuses
		self.create_test_order_ledger(order_status="Unassigned")
		self.create_test_order_ledger(order_status="Unassigned")
		self.create_test_order_ledger(order_status="Assigned")

		counts = get_status_counts()

		self.assertIsInstance(counts, dict)
		self.assertGreaterEqual(counts.get("Unassigned", 0), 2)
		self.assertGreaterEqual(counts.get("Assigned", 0), 1)

	def test_get_filter_options(self):
		"""Test get_filter_options API endpoint."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_filter_options
		)

		# Create order to ensure data exists (using soi_karigar as that's the actual field)
		self.create_test_order_ledger(soi_karigar=self.test_supplier)

		options = get_filter_options()

		self.assertIn("customers", options)
		self.assertIn("karigars", options)
		self.assertIn("item_groups", options)
		self.assertIsInstance(options["customers"], list)
		self.assertIsInstance(options["karigars"], list)
		self.assertIsInstance(options["item_groups"], list)

	def test_update_item_status_single(self):
		"""Test update_item_status API for single item."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)

		order = self.create_test_order_ledger(order_status="Unassigned")

		results = update_item_status(
			item_names=[order.name],
			new_status="Assigned"
		)

		self.assertEqual(len(results), 1)
		self.assertTrue(results[0]["success"])
		self.assertEqual(results[0]["new_status"], "Assigned")

		# Verify order was updated
		order.reload()
		self.assertEqual(order.order_status, "Assigned")

	def test_update_item_status_bulk(self):
		"""Test update_item_status API for multiple items."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)

		orders = [
			self.create_test_order_ledger(order_status="Unassigned"),
			self.create_test_order_ledger(order_status="Unassigned"),
			self.create_test_order_ledger(order_status="Unassigned")
		]

		item_names = [o.name for o in orders]

		results = update_item_status(
			item_names=item_names,
			new_status="Assigned"
		)

		self.assertEqual(len(results), 3)
		for result in results:
			self.assertTrue(result["success"])

	def test_update_item_status_with_weight_per_unit(self):
		"""Test update_item_status with weight_per_unit calculation."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)

		order = self.create_test_order_ledger(order_status="Incoming", qty=5)

		results = update_item_status(
			item_names=[order.name],
			new_status="Internal QA",
			weight_per_unit="2.5",
			weight_field="karigar_received_weight"
		)

		self.assertTrue(results[0]["success"])

		# Verify weight calculation: 5 qty × 2.5 weight_per_unit = 12.5
		order.reload()
		self.assertEqual(order.karigar_received_weight, 12.5)

	def test_update_item_status_invalid_status(self):
		"""Test update_item_status with invalid status."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)

		order = self.create_test_order_ledger()

		with self.assertRaises(frappe.ValidationError):
			update_item_status(
				item_names=[order.name],
				new_status="Invalid Status"
			)

	def test_update_item_status_invalid_weight(self):
		"""Test update_item_status with invalid weight_per_unit."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)

		order = self.create_test_order_ledger(order_status="Incoming")

		with self.assertRaises(frappe.ValidationError):
			update_item_status(
				item_names=[order.name],
				new_status="Internal QA",
				weight_per_unit="-5"  # Negative weight
			)

	def test_split_order_item_basic(self):
		"""Test split_order_item API basic functionality."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			split_order_item
		)

		order = self.create_test_order_ledger(qty=100)

		result = split_order_item(
			item_name=order.name,
			split_qty=60
		)

		self.assertTrue(result["success"])
		self.assertEqual(result["original_entry"], order.name)
		self.assertEqual(len(result["new_entries"]), 2)
		self.assertEqual(result["first_entry"]["qty"], 60)
		self.assertEqual(result["second_entry"]["qty"], 40)

		# Verify original order is deleted
		self.assertFalse(frappe.db.exists("Order Ledger", order.name))

		# Verify new orders exist
		first_order = frappe.get_doc("Order Ledger", result["first_entry"]["name"])
		second_order = frappe.get_doc("Order Ledger", result["second_entry"]["name"])

		self.assertEqual(first_order.qty, 60)
		self.assertEqual(second_order.qty, 40)
		self.assertIn("Split from", first_order.soi_customer_notes or "")
		self.assertIn("Split from", second_order.soi_customer_notes or "")

	def test_split_order_item_invalid_qty(self):
		"""Test split_order_item with invalid quantities."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			split_order_item
		)

		order = self.create_test_order_ledger(qty=100)

		# Test split_qty <= 0
		with self.assertRaises(frappe.ValidationError):
			split_order_item(item_name=order.name, split_qty=0)

		# Test split_qty >= total_qty
		with self.assertRaises(frappe.ValidationError):
			split_order_item(item_name=order.name, split_qty=100)

		# Test split_qty > total_qty
		with self.assertRaises(frappe.ValidationError):
			split_order_item(item_name=order.name, split_qty=150)

	def test_split_order_item_preserves_fields(self):
		"""Test split_order_item preserves all fields from original."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			split_order_item
		)

		order = self.create_test_order_ledger(
			qty=50,
			order_status="Assigned",
			soi_karigar=self.test_supplier,
			soi_order_weight=100.5,
			soi_karigar_notes="Original notes"
		)

		result = split_order_item(item_name=order.name, split_qty=30)

		first_order = frappe.get_doc("Order Ledger", result["first_entry"]["name"])
		second_order = frappe.get_doc("Order Ledger", result["second_entry"]["name"])

		# Verify fields are preserved
		self.assertEqual(first_order.order_status, "Assigned")
		self.assertEqual(first_order.soi_karigar, self.test_supplier)
		self.assertEqual(first_order.soi_order_weight, 100.5)
		self.assertEqual(second_order.order_status, "Assigned")
		self.assertEqual(second_order.soi_karigar, self.test_supplier)

	# ========== EDGE CASES AND ERROR HANDLING ==========

	def test_disabled_orders_excluded_from_queries(self):
		"""Test that disabled orders are excluded from API queries."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items,
			get_status_counts
		)

		# Create enabled and disabled orders
		enabled_order = self.create_test_order_ledger(order_status="Unassigned")
		disabled_order = self.create_test_order_ledger(
			order_status="Unassigned",
			disabled=1
		)

		result = get_all_order_items(page=1, page_size=100)
		order_names = [o["name"] for o in result["data"]]

		self.assertIn(enabled_order.name, order_names)
		self.assertNotIn(disabled_order.name, order_names)

		# Test status counts
		counts = get_status_counts()
		# Count should not include disabled orders
		# (exact count depends on other tests, just verify it doesn't crash)
		self.assertIsInstance(counts, dict)

	def test_transition_with_invalid_status_indices(self):
		"""Test transition effects with invalid status indices."""
		order = self.create_test_order_ledger()

		# Should not crash with invalid statuses
		apply_status_transition_effects(order, "Invalid Status", "Another Invalid", {})

		# Order should remain unchanged
		self.assertEqual(order.order_status, "Unassigned")

	def test_data_enrichment_in_get_all_order_items(self):
		"""Test data enrichment adds required frontend fields."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		order = self.create_test_order_ledger()

		result = get_all_order_items(page=1, page_size=10)

		# Find our test order
		test_order_data = None
		for item in result["data"]:
			if item["name"] == order.name:
				test_order_data = item
				break

		self.assertIsNotNone(test_order_data)
		self.assertIn("item_code", test_order_data)
		self.assertIn("parent", test_order_data)
		self.assertIn("doctype", test_order_data)
		self.assertIn("images", test_order_data)
		self.assertIsInstance(test_order_data["images"], list)

	def test_soi_field_prioritization(self):
		"""Test SOI fields are prioritized over Order Ledger fields."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		order = self.create_test_order_ledger(
			soi_order_weight=50.5,
			soi_karigar=self.test_supplier,
			soi_karigar_notes="SOI notes"
		)

		result = get_all_order_items(page=1, page_size=10)

		test_order_data = None
		for item in result["data"]:
			if item["name"] == order.name:
				test_order_data = item
				break

		self.assertIsNotNone(test_order_data)
		self.assertEqual(test_order_data["item_weight"], 50.5)
		self.assertEqual(test_order_data["karigar"], self.test_supplier)
		self.assertEqual(test_order_data["karigar_notes"], "SOI notes")

	def test_cache_persistence_across_calls(self):
		"""Test cache persists across multiple function calls."""
		# First call populates cache
		statuses_1 = _get_workflow_status_cached()

		# Second call should use cache and return same result
		statuses_2 = _get_workflow_status_cached()

		self.assertEqual(statuses_1, statuses_2)

		# Third call should also return the same result
		statuses_3 = _get_workflow_status_cached()
		self.assertEqual(statuses_2, statuses_3)

	def test_pagination_total_pages_calculation(self):
		"""Test total_pages calculation in pagination."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			get_all_order_items
		)

		# Create exactly 7 orders
		for i in range(7):
			self.create_test_order_ledger()

		result = get_all_order_items(page=1, page_size=3)

		# With 7 total items and page_size=3, should have 3 pages
		# (3 + 3 + 1 = 7 items)
		expected_pages = (result["total"] + 3 - 1) // 3
		self.assertEqual(result["total_pages"], expected_pages)

	def test_json_parsing_in_update_item_status(self):
		"""Test JSON string parsing for item_names parameter."""
		from ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger import (
			update_item_status
		)
		import json

		orders = [
			self.create_test_order_ledger(),
			self.create_test_order_ledger()
		]

		item_names_json = json.dumps([o.name for o in orders])

		results = update_item_status(
			item_names=item_names_json,
			new_status="Assigned"
		)

		self.assertEqual(len(results), 2)
		for result in results:
			self.assertTrue(result["success"])
