frappe.pages["karigar-workflow"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Karigar Order Workflow",
		single_column: true,
	});

	// Add search field in page header
	page.search_field = page.add_field({
		fieldname: "search",
		fieldtype: "Data",
		label: "",
		placeholder: __("Search Here"),
		change: function () {
			page.refresh_data(true); // Reset to page 1 on search
		},
	});

	// Store workflow data (will be populated from backend)
	page.workflow_data = {
		current_stage: "",
		stages: [],
	};

	// Orders data
	page.orders_data = [];

	// Pagination state
	page.pagination = {
		current_page: 1,
		page_size: 50,
		total: 0,
		total_pages: 0,
	};

	// ========== CONSTANTS ==========
	const CONSTANTS = {
		DROPDOWN_MAX_OPTIONS: 10,
		FILTER_DEBOUNCE_MS: 500,
		SEARCH_RESET_DELAY_MS: 100,
		PAGINATION_MAX_VISIBLE_PAGES: 5,
		MAX_REASONABLE_WEIGHT: 1000000, // grams
	};

	// ========== HELPER FUNCTIONS ==========

	// Check if transition requires weight entry (index-based, not hardcoded names)
	page.requires_weight_entry = function (from_index, to_index) {
		// Incoming (2) → Internal QA (3)
		if (from_index === 2 && to_index === 3) return true;
		// Pending Delivery (4) → Delivered (5)
		if (from_index === 4 && to_index === 5) return true;
		return false;
	};

	// Check if reverse transition needs timestamp parameter
	page.needs_revert_timestamp = function (from_index, to_index) {
		// Internal QA (3) → Incoming (2)
		return from_index === 3 && to_index === 2;
	};

	// Get weight field type for a transition
	page.get_weight_type = function (from_index, to_index) {
		if (from_index === 2 && to_index === 3) return "received";
		if (from_index === 4 && to_index === 5) return "dispatch";
		return null;
	};

	// Helper function to get stage info (reduces code duplication)
	page.get_stage_info = function () {
		const current_stage = page.workflow_data.current_stage;
		const stages = page.workflow_data.stages;
		const current_index = stages.findIndex((s) => s.name === current_stage);
		return {
			current: current_stage,
			current_index: current_index,
			prev: current_index > 0 ? stages[current_index - 1].name : null,
			prev_index: current_index > 0 ? current_index - 1 : -1,
			next: current_index < stages.length - 1 ? stages[current_index + 1].name : null,
			next_index: current_index < stages.length - 1 ? current_index + 1 : -1,
			is_first: current_index === 0,
			is_last: current_index === stages.length - 1,
		};
	};

	page.format_item_display = function (order) {
		const item_code = order.item_code || "";
		const item_name = order.item_name || "";  // Fetched from Item master, not Sales Order Item

		if (!item_code) {
			return "N/A";
		}

		if (!item_name) {
			return item_code;
		}
		return `${item_code}-${item_name}`;
	};

	// Helper function to update order status (reduces API call duplication)
	page.update_order_status = function (item_names, new_status, extra_args, callback) {
		const args = Object.assign(
			{
				item_names: JSON.stringify(item_names),
				new_status: new_status,
			},
			extra_args || {}
		);

		frappe.call({
			method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.update_item_status",
			args: args,
			freeze: true,
			freeze_message: __("Updating..."),
			callback: function (r) {
				if (r.message) {
					const failed = r.message.filter((item) => !item.success);
					const succeeded = r.message.filter((item) => item.success);

					if (failed.length > 0) {
						const error_details = failed.map((f) => `${f.name}: ${f.error}`).join("<br>");
						frappe.msgprint({
							title: __("Update Status"),
							indicator: failed.length === r.message.length ? "red" : "orange",
							message: __("{0} succeeded, {1} failed:<br><br>{2}", [
								succeeded.length,
								failed.length,
								error_details
							])
						});
					} else if (succeeded.length > 0) {
						frappe.show_alert({
							message: __("{0} item(s) updated successfully", [succeeded.length]),
							indicator: "green"
						}, 3);
					}
				}
				if (callback) callback(r);
			},
			error: function (err) {
				console.error("Order status update failed:", err);
				frappe.msgprint({
					title: __("Update Failed"),
					indicator: "red",
					message: __("Error updating status: {0}", [err.message || "Unknown error. Please try again or contact support."])
				});
			},
		});
	};

	
	// Get workflow statuses and initialize UI
	frappe.call({
		method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_workflow_status",
		callback: function (r) {
			if (r.message && r.message.length > 0) {
				// Update stages with actual workflow statuses
				page.workflow_data.stages = r.message.map((status, idx) => ({
					name: status,
					count: 0,
					stage_number: idx + 1,
				}));
				// Set first stage as current stage
				page.workflow_data.current_stage = r.message[0];
			}
			// Initialize the UI after workflow statuses are loaded
			page.build_ui();
			// Load data on page load
			page.refresh_data();
		},
	});

	// Setup real-time progress listener
	frappe.realtime.off("karigar_batch_progress");
	frappe.realtime.on("karigar_batch_progress", function (data) {
		if (data.data_import !== "karigar-dashboard") return;

		// Skip showing progress modal

		if (data.current === data.total) {
			frappe.show_alert("Status updated successfully.");
			page.refresh_data();
		}
	});

	// Build the UI
	page.build_ui = function () {
		// Clear existing content
		page.main.empty();

		// Create filter section
		page.create_filter_section();

		// Create workflow step indicator
		page.create_workflow_steps();

		// Create data table
		page.create_data_table();
	};

	// Create filter section
	page.create_filter_section = function () {
		const filter_html = `
			<div class="workflow-filters">
				<div class="row" style="margin: 0;">
					<div class="col-12 col-sm-6 col-md-4 col-lg-3 filter-col">
						<div class="filter-box" data-filter="customer">
							<input type="text" class="form-control filter-input" id="customer-filter" placeholder="Customer" autocomplete="off">
							<div class="custom-dropdown" id="customer-dropdown"></div>
						</div>
					</div>
					<div class="col-12 col-sm-6 col-md-4 col-lg-3 filter-col">
						<div class="filter-box" data-filter="karigar">
							<input type="text" class="form-control filter-input" id="karigar-filter" placeholder="Karigar" autocomplete="off">
							<div class="custom-dropdown" id="karigar-dropdown"></div>
						</div>
					</div>
					<div class="col-12 col-sm-6 col-md-4 col-lg-3 filter-col">
						<div class="filter-box" data-filter="item-name">
							<input type="text" class="form-control filter-input" id="item-name-filter" placeholder="Item Name" autocomplete="off">
							<div class="custom-dropdown" id="item-name-dropdown"></div>
						</div>
					</div>
					<div class="col-12 col-sm-6 col-md-4 col-lg-3 filter-col">
						<button class="btn btn-sm btn-default" id="clear-filters-btn" style="height: 38px;">Clear Filters</button>
					</div>
				</div>
			</div>
		`;

		$(filter_html).appendTo(page.main);

		// Store filter options data
		page.filter_options = {
			customers: [],
			karigars: [],
			item_names: [],
		};

		// Debounce timer for filter inputs
		let filter_timeout = null;

		// Function to show custom dropdown with filtered options
		const showDropdown = function ($input) {
			// Hide all other dropdowns first
			$(".custom-dropdown").not($input.siblings(".custom-dropdown")).hide();

			const filter_type = $input.closest(".filter-box").data("filter");
			const $dropdown = $input.siblings(".custom-dropdown");
			const input_value = $input.val().toLowerCase().trim();

			let options = [];
			if (filter_type === "customer") {
				options = page.filter_options.customers || [];
			} else if (filter_type === "karigar") {
				options = page.filter_options.karigars || [];
			} else if (filter_type === "item-name") {
				options = page.filter_options.item_names || [];
			}

			// If input is empty, hide dropdown
			if (!input_value) {
				$dropdown.hide();
				return;
			}

			// Filter options based on input value
			const filtered_options = options.filter((opt) =>
				opt.toLowerCase().includes(input_value)
			);

			if (filtered_options.length > 0) {
				let dropdown_html = "";
				filtered_options.slice(0, CONSTANTS.DROPDOWN_MAX_OPTIONS).forEach((option) => {
					// Escape HTML to prevent XSS
					const escaped_option = $('<div>').text(option).html();
					dropdown_html += `<div class="dropdown-option" data-value="${escaped_option}">${escaped_option}</div>`;
				});
				$dropdown.html(dropdown_html).show();
			} else {
				$dropdown.hide();
			}
		};

		// Function to hide all dropdowns
		const hideAllDropdowns = function () {
			$(".custom-dropdown").hide();
		};

		// Track if we're currently searching to prevent multiple calls
		let is_searching = false;

		// Add filter change handlers with debounce
		page.main.find(".filter-input").on("input", function () {
			const $this = $(this);
			showDropdown($this);

			// Don't trigger search while we're already searching
			if (is_searching) {
				return;
			}

			clearTimeout(filter_timeout);
			filter_timeout = setTimeout(function () {
				is_searching = true;
				page.refresh_data(true); // Reset to page 1 on filter change
				// Reset flag after a short delay
				setTimeout(function () {
					is_searching = false;
				}, CONSTANTS.SEARCH_RESET_DELAY_MS);
			}, CONSTANTS.FILTER_DEBOUNCE_MS);
		});

		// Show dropdown on focus if there's a value
		page.main.find(".filter-input").on("focus", function () {
			const $this = $(this);
			if ($this.val().trim()) {
				showDropdown($this);
			}
		});

		// Handle dropdown option click - use event delegation on page.main
		page.main.on("click", ".dropdown-option", function (e) {
			e.preventDefault();
			e.stopPropagation();

			const value = $(this).data("value");
			const $filterBox = $(this).closest(".filter-box");
			const $input = $filterBox.find(".filter-input");

			// Set the value
			$input.val(value);

			// Hide dropdown immediately
			hideAllDropdowns();

			// Clear any pending timeout
			clearTimeout(filter_timeout);

			// Trigger search only once
			if (!is_searching) {
				is_searching = true;
				page.refresh_data(true);
				// Reset flag after search completes
				setTimeout(function () {
					is_searching = false;
				}, 100);
			}
		});

		// Hide dropdown when clicking outside
		$(document).on("click", function (e) {
			if (!$(e.target).closest(".filter-box").length) {
				hideAllDropdowns();
			}
		});

		// Prevent dropdown from closing when clicking inside it
		page.main.on("click", ".custom-dropdown", function (e) {
			e.stopPropagation();
		});

		// Keyboard navigation for dropdown
		page.main.find(".filter-input").on("keydown", function (e) {
			const $input = $(this);
			const $dropdown = $input.siblings(".custom-dropdown");
			const $options = $dropdown.find(".dropdown-option");

			// If dropdown is not visible, only handle Enter
			if (!$dropdown.is(":visible")) {
				if (e.which === 13) {
					// Enter key
					clearTimeout(filter_timeout);
					page.refresh_data(true);
				}
				return;
			}

			// Arrow Down - move to next option
			if (e.which === 40) {
				e.preventDefault();
				const $active = $options.filter(".active");
				if ($active.length === 0) {
					$options.first().addClass("active");
				} else {
					$active.removeClass("active");
					const $next = $active.next(".dropdown-option");
					if ($next.length > 0) {
						$next.addClass("active");
					} else {
						$options.first().addClass("active");
					}
				}
			}
			// Arrow Up - move to previous option
			else if (e.which === 38) {
				e.preventDefault();
				const $active = $options.filter(".active");
				if ($active.length === 0) {
					$options.last().addClass("active");
				} else {
					$active.removeClass("active");
					const $prev = $active.prev(".dropdown-option");
					if ($prev.length > 0) {
						$prev.addClass("active");
					} else {
						$options.last().addClass("active");
					}
				}
			}
			// Enter - select active option
			else if (e.which === 13) {
				e.preventDefault();
				const $active = $options.filter(".active");
				if ($active.length > 0) {
					$active.click();
				} else {
					clearTimeout(filter_timeout);
					hideAllDropdowns();
					page.refresh_data(true);
				}
			}
			// Escape - close dropdown
			else if (e.which === 27) {
				e.preventDefault();
				hideAllDropdowns();
			}
		});

		// Clear all filters button
		page.main.find("#clear-filters-btn").on("click", function () {
			page.main.find("#customer-filter").val("");
			page.main.find("#karigar-filter").val("");
			page.main.find("#item-name-filter").val("");
			page.refresh_data(true);
		});

		// Load autocomplete data
		page.load_filter_options();
	};

	// Load filter options for autocomplete
	page.load_filter_options = function () {
		// Fetch unique customers, karigars, and item names from all stages
		frappe.call({
			method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_filter_options",
			callback: function (r) {
				if (r.message) {
					// Store options in page object for custom dropdown
					page.filter_options.customers = r.message.customers || [];
					page.filter_options.karigars = r.message.karigars || [];
					page.filter_options.item_names = r.message.item_names || [];
				}
			},
		});
	};

	// Create workflow step indicator
	page.create_workflow_steps = function () {
		const stages = page.workflow_data.stages;
		const current_stage = page.workflow_data.current_stage;

		let steps_html = '<div class="workflow-steps">';
		steps_html +=
			'<div class="steps-container" style="display: flex; justify-content: space-between; align-items: center;">';

		// Add connecting line
		steps_html += '<div class="steps-line"></div>';

		stages.forEach((stage) => {
			const is_active = stage.name === current_stage;
			const step_class = is_active ? "active" : "";

			steps_html += `
				<div class="workflow-step ${step_class}" data-stage="${stage.name}">
					<div class="step-circle">
						${stage.stage_number}
					</div>
					<div class="step-label">
						${stage.name} (${stage.count})
					</div>
				</div>
			`;
		});

		steps_html += "</div></div>";

		$(steps_html).appendTo(page.main);

		// Add click handler for workflow steps
		page.main.find(".workflow-step").on("click", function () {
			const stage_name = $(this).data("stage");
			page.workflow_data.current_stage = stage_name;
			page.refresh_data(true, true); // Reset to page 1 and rebuild full UI when changing stage
		});
	};

	// Create data table
	page.create_data_table = function () {
		const current_stage = page.workflow_data.current_stage;
		const current_count =
			page.workflow_data.stages.find((s) => s.name === current_stage)?.count || 0;
		const current_index = page.workflow_data.stages.findIndex((s) => s.name === current_stage);
		const is_first_stage = current_index === 0;
		const is_last_stage = current_index === page.workflow_data.stages.length - 1;

		// Build dropdown menu items based on current stage (hide completely for last stage)
		let action_dropdown_html = "";
		if (!is_last_stage) {
			let dropdown_items = "";
			if (!is_last_stage) {
				dropdown_items +=
					'<a class="dropdown-item move-next-action" href="#" style="cursor: pointer;">Move to Next Stage</a>';
			}
			if (!is_first_stage) {
				dropdown_items +=
					'<a class="dropdown-item move-prev-action" href="#" style="cursor: pointer;">Move to Previous Stage</a>';
			}
			dropdown_items += `<a class="dropdown-item split-action" href="#" style="cursor: pointer;">Split</a>`;

			action_dropdown_html = `
				<div class="dropdown">
					<button class="btn btn-default btn-sm dropdown-toggle table-action-btn" type="button" id="actionDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="background-color: #2d3748; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 500; cursor: pointer;">
						Action
					</button>

					<div class="dropdown-menu dropdown-menu-right" aria-labelledby="actionDropdown">
						${dropdown_items}
					</div>
				</div>
			`;
		}

		const table_html = `
			<div class="workflow-table">
				<div class="table-header" style="display: flex; justify-content: space-between; align-items: center;">
					<h4>${current_stage} : ${current_count}</h4>
					${action_dropdown_html}
				</div>
				<div class="table-responsive">
					<table class="table table-bordered">
						<thead>
							<tr>
								<th style="width: 40px; text-align: center;">
									<input type="checkbox" class="select-all-checkbox">
								</th>
								<th style="width: 80px;">S. No.</th>
								<th>Customer</th>
								<th>PO No.</th>
								<th>Karigar</th>
								<th>Item Code</th>
								<th>Item Details</th>
								<th>Description</th>
								<th>Texture</th>
								<th>Item Weight (g)</th>
								<th style="width: 80px;">Qty</th>
								<th style="width: 120px;">Status</th>
								<th>Sales Order</th>
								<th style="width: 120px;">ID</th>
							</tr>
						</thead>
						<tbody>
							${page.generate_table_rows()}
						</tbody>
					</table>
				</div>
				${page.generate_pagination_html()}
			</div>
		`;

		$(table_html).appendTo(page.main);

		// Add dropdown menu item click handler for next stage
		page.main.find(".move-next-action").on("click", function (e) {
			e.preventDefault();

			const selected_rows = page.main.find(".row-checkbox:checked");
			const selected_count = selected_rows.length;

			if (selected_count === 0) {
				frappe.msgprint(__("Please select at least one entry"));
				return;
			}

			const stage_info = page.get_stage_info();

			if (!stage_info.next) {
				frappe.msgprint(__("Already at last stage"));
				return;
			}

			// Check if dialog is needed for this transition
			const needs_dialog = page.requires_weight_entry(stage_info.current_index, stage_info.next_index);

			if (needs_dialog) {
				if (selected_count === 1) {
					page.open_single_entry_dialog(selected_rows);
				} else {
					page.open_multiple_entries_dialog(selected_rows);
				}
			} else {
				const selected_ids = [];
				selected_rows.each(function () {
					selected_ids.push($(this).data("name"));
				});

				frappe.confirm(
					__("Move {0} item(s) from {1} to {2}?", [
						selected_count,
						stage_info.current,
						stage_info.next,
					]),
					function () {
						page.update_order_status(selected_ids, stage_info.next, {}, function () {
							frappe.show_alert({
								message: __("Successfully updated {0} item(s)", [selected_count]),
								indicator: "green",
							});
							page.refresh_data();
						});
					}
				);
			}
		});

		// Add dropdown menu item click handler for previous stage
		page.main.find(".move-prev-action").on("click", function (e) {
			e.preventDefault();

			const selected_rows = page.main.find(".row-checkbox:checked");
			const selected_count = selected_rows.length;

			if (selected_count === 0) {
				frappe.msgprint(__("Please select at least one entry"));
				return;
			}

			const stage_info = page.get_stage_info();

			if (!stage_info.prev) {
				frappe.msgprint(__("Already at first stage"));
				return;
			}

			const selected_ids = [];
			selected_rows.each(function () {
				selected_ids.push($(this).data("name"));
			});

			frappe.confirm(
				__("Move {0} item(s) from {1} to {2}?", [
					selected_count,
					stage_info.current,
					stage_info.prev,
				]),
				function () {
					const extra_args = {};
					if (page.needs_revert_timestamp(stage_info.current_index, stage_info.prev_index)) {
						extra_args.received_to_incoming = frappe.datetime.now_datetime();
					}
					page.update_order_status(
						selected_ids,
						stage_info.prev,
						extra_args,
						function () {
							frappe.show_alert({
								message: __("Successfully moved {0} item(s) back to {1}", [
									selected_count,
									stage_info.prev,
								]),
								indicator: "green",
							});
							page.refresh_data();
						}
					);
				}
			);
		});

		// Add dropdown menu item click handler for split
		page.main.find(".split-action").on("click", function (e) {
			e.preventDefault();

			const selected_rows = page.main.find(".row-checkbox:checked");
			const selected_count = selected_rows.length;

			if (selected_count === 0) {
				frappe.msgprint(__("Please select at least one entry"));
				return;
			}

			const selected_orders = [];
			selected_rows.each(function () {
				const id = $(this).data("name");
				const order = page.orders_data.find((o) => o.name === id);
				if (order) selected_orders.push(order);
			});

			page.open_split_modal(selected_orders);
		});

		// Add checkbox handlers
		page.attach_checkbox_handlers();

		// Add customer link click handler
		page.main.find(".customer-link").on("click", function (e) {
			e.preventDefault();
			const order_index = parseInt($(this).data("order-index"));
			const stage_info = page.get_stage_info();

			// Check if we should open weight entry dialog for specific transitions
			const should_open_weight_dialog = page.requires_weight_entry(stage_info.current_index, stage_info.next_index);

			if (should_open_weight_dialog) {
				// Open weight entry dialog with navigation
				page.open_single_entry_dialog_with_nav(page.orders_data, order_index);
			} else {
				// Open read-only view dialog with navigation
				page.open_view_dialog_with_nav(page.orders_data, order_index);
			}
		});

		// Add pagination event handlers
		page.setup_pagination_handlers();
	};

	// Generate pagination HTML
	page.generate_pagination_html = function () {
		const { current_page, total_pages, total, page_size } = page.pagination;

		if (total_pages <= 1) {
			return ""; // Don't show pagination if only one page
		}

		const start_item = total === 0 ? 0 : (current_page - 1) * page_size + 1;
		const end_item = Math.min(current_page * page_size, total);

		// Generate page number buttons
		let page_buttons = [];
		const max_visible = CONSTANTS.PAGINATION_MAX_VISIBLE_PAGES;

		if (total_pages <= max_visible) {
			for (let i = 1; i <= total_pages; i++) {
				page_buttons.push(i);
			}
		} else {
			if (current_page <= 3) {
				page_buttons = [1, 2, 3, 4, "...", total_pages];
			} else if (current_page >= total_pages - 2) {
				page_buttons = [
					1,
					"...",
					total_pages - 3,
					total_pages - 2,
					total_pages - 1,
					total_pages,
				];
			} else {
				page_buttons = [
					1,
					"...",
					current_page - 1,
					current_page,
					current_page + 1,
					"...",
					total_pages,
				];
			}
		}

		let buttons_html = "";
		page_buttons.forEach((btn) => {
			if (btn === "...") {
				buttons_html += `<span style="padding: 6px 12px; color: #6c757d;">...</span>`;
			} else {
				const active_class = btn === current_page ? "btn-primary" : "btn-default";
				const active_style =
					btn === current_page
						? "background-color: #2490EF; color: white; border-color: #2490EF;"
						: "";
				buttons_html += `
					<button class="btn btn-sm pagination-page-btn ${active_class}" data-page="${btn}" style="margin: 0 2px; ${active_style}">
						${btn}
					</button>
				`;
			}
		});

		return `
			<div class="pagination-container" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 10px; border-top: 1px solid #dee2e6;">
				<div class="pagination-info" style="color: #6c757d; font-size: 14px;">
					Showing ${start_item} to ${end_item} of ${total} entries
				</div>
				<div class="pagination-controls" style="display: flex; align-items: center; gap: 10px;">
					<button class="btn btn-sm btn-default pagination-prev-btn" ${
						current_page === 1 ? "disabled" : ""
					} style="padding: 6px 12px;">
						Previous
					</button>
					<div class="pagination-pages" style="display: flex; align-items: center;">
						${buttons_html}
					</div>
					<button class="btn btn-sm btn-default pagination-next-btn" ${
						current_page === total_pages ? "disabled" : ""
					} style="padding: 6px 12px;">
						Next
					</button>
				</div>
			</div>
		`;
	};

	// Setup pagination event handlers
	page.setup_pagination_handlers = function () {
		// Previous button
		page.main.find(".pagination-prev-btn").on("click", function () {
			if (page.pagination.current_page > 1) {
				page.pagination.current_page--;
				page.refresh_data();
			}
		});

		// Next button
		page.main.find(".pagination-next-btn").on("click", function () {
			if (page.pagination.current_page < page.pagination.total_pages) {
				page.pagination.current_page++;
				page.refresh_data();
			}
		});

		// Page number buttons
		page.main.find(".pagination-page-btn").on("click", function () {
			const page_num = parseInt($(this).data("page"));
			if (page_num !== page.pagination.current_page) {
				page.pagination.current_page = page_num;
				page.refresh_data();
			}
		});
	};

	// Generate table rows
	page.generate_table_rows = function () {
		let rows_html = "";
		const start_index = (page.pagination.current_page - 1) * page.pagination.page_size;

		page.orders_data.forEach((order, idx) => {
			const customer = order.customer || "N/A";
			const po_no = order.po_no || "N/A";
			const karigar = order.karigar || "N/A";
			const item_code = order.item_code || "N/A";
			const item_details = page.format_item_display(order);
			// Strip HTML tags from description and limit length
			let description = order.description || "N/A";
			if (description && description !== "N/A") {
				// Create a temporary div to strip HTML tags
				const tempDiv = document.createElement("div");
				tempDiv.innerHTML = description;
				description = tempDiv.textContent || tempDiv.innerText || "N/A";
				// Limit to 100 characters for table display
				if (description.length > 100) {
					description = description.substring(0, 100) + "...";
				}
			}
			const texture = order.texture || "N/A";
			const item_weight = order.item_weight !== null && order.item_weight !== undefined ? parseFloat(order.item_weight).toFixed(2) : "N/A";
			const qty = order.qty || 0;
			const status = order.order_status || "N/A";
			const sales_order = order.sales_order || "N/A";
			const id = order.name || "N/A";
			const serial_number = start_index + idx + 1;

			rows_html += `
				<tr>
					<td style="text-align: center;">
						<input type="checkbox" class="row-checkbox" data-name="${id}" data-order-index="${idx}">
					</td>
					<td>${serial_number}</td>
					<td><a href="#" class="customer-link" data-order-index="${idx}" style="color: #2490EF; cursor: pointer;">${customer}</a></td>
					<td>${po_no}</td>
					<td>${karigar}</td>
					<td>${item_code}</td>
					<td>${item_details}</td>
					<td>${description}</td>
					<td>${texture}</td>
					<td>${item_weight}</td>
					<td>${qty}</td>
					<td>
						<span class="status-in-progress">${status}</span>
					</td>
					<td>${sales_order}</td>
					<td>${id}</td>
				</tr>
			`;
		});

		return (
			rows_html ||
			'<tr><td colspan="14" style="text-align: center;">No orders found</td></tr>'
		);
	};

	// Load status counts
	page.load_status_counts = function () {
		// Get current filter values
		const filter_args = {
			customer: $("#customer-filter").val() || "",
			karigar: $("#karigar-filter").val() || "",
			item_name: $("#item-name-filter").val() || "",
			search: page.search_field ? page.search_field.get_value() : "",
			return_counts_only: true,
		};

		frappe.call({
			method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_all_order_items",
			args: filter_args,
			callback: function (r) {
				if (r.message) {
					page.workflow_data.stages.forEach((stage) => {
						stage.count = r.message[stage.name] || 0;
					});
					// Update the counts in the existing workflow steps without re-rendering
					page.update_workflow_step_counts();
				}
			},
		});
	};

	// Update workflow step counts without re-rendering
	page.update_workflow_step_counts = function () {
		page.workflow_data.stages.forEach((stage) => {
			const $step = page.main.find(`.workflow-step[data-stage="${stage.name}"]`);
			if ($step.length) {
				$step.find(".step-label").text(`${stage.name} (${stage.count})`);
			}
		});
	};

	// Update workflow steps without full rebuild
	page.update_workflow_steps = function () {
		const current_stage = page.workflow_data.current_stage;

		// Update active state and counts for all steps
		page.workflow_data.stages.forEach((stage) => {
			const $step = page.main.find(`.workflow-step[data-stage="${stage.name}"]`);
			if ($step.length) {
				// Update count
				$step.find(".step-label").text(`${stage.name} (${stage.count})`);

				// Update active state
				if (stage.name === current_stage) {
					$step.addClass("active");
				} else {
					$step.removeClass("active");
				}
			}
		});
	};

	// Update data table without full rebuild
	page.update_data_table = function () {
		// Find and update the workflow table
		const $workflow_table = page.main.find(".workflow-table");
		if (!$workflow_table.length) {
			// If table doesn't exist, do full rebuild
			page.create_data_table();
			return;
		}

		const current_stage = page.workflow_data.current_stage;
		const current_count =
			page.workflow_data.stages.find((s) => s.name === current_stage)?.count || 0;

		// Update table header count
		$workflow_table.find(".table-header h4").text(`${current_stage} : ${current_count}`);

		// Update table rows
		const $tbody = $workflow_table.find("tbody");
		if ($tbody.length) {
			$tbody.html(page.generate_table_rows());
		}

		// Update pagination
		const $pagination = page.main.find(".pagination-container");
		if ($pagination.length) {
			$pagination.html(page.generate_pagination_html());
			// Re-attach pagination handlers
			page.setup_pagination_handlers();
		}

		// Re-attach table event handlers
		page.attach_table_handlers();
	};

	// Setup checkbox handlers for select-all and row checkboxes
	page.attach_checkbox_handlers = function () {
		page.main.find(".select-all-checkbox").on("change", function () {
			const is_checked = $(this).prop("checked");
			page.main.find(".row-checkbox").prop("checked", is_checked);
		});

		page.main.find(".row-checkbox").on("change", function () {
			const all_checked =
				page.main.find(".row-checkbox:checked").length ===
				page.main.find(".row-checkbox").length;
			page.main.find(".select-all-checkbox").prop("checked", all_checked);
		});
	};

	// Attach table event handlers (separated for reuse)
	page.attach_table_handlers = function () {
		const stage_info = page.get_stage_info();

		// Attach checkbox handlers
		page.attach_checkbox_handlers();

		// Customer link click handler
		page.main.find(".customer-link").on("click", function (e) {
			e.preventDefault();
			const order_index = parseInt($(this).data("order-index"));

			// Check if we should open weight entry dialog for specific transitions
			const should_open_weight_dialog = page.requires_weight_entry(stage_info.current_index, stage_info.next_index);

			if (should_open_weight_dialog) {
				page.open_single_entry_dialog_with_nav(page.orders_data, order_index);
			} else {
				page.open_view_dialog_with_nav(page.orders_data, order_index);
			}
		});
	};

	// Refresh data with server-side pagination
	page.refresh_data = function (reset_page = false, rebuild_full_ui = false) {
		if (reset_page) {
			page.pagination.current_page = 1;
		}

		const filters = {
			page: page.pagination.current_page,
			page_size: page.pagination.page_size,
			order_status: page.workflow_data.current_stage,
			search: page.search_field ? page.search_field.get_value() : "",
			customer: $("#customer-filter").val() || "",
			karigar: $("#karigar-filter").val() || "",
			item_name: $("#item-name-filter").val() || "",
		};

		frappe.call({
			method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_all_order_items",
			args: filters,
			freeze: false, // Don't freeze UI during filter operations
			callback: function (r) {
				if (r.message) {
					page.orders_data = r.message.data || [];
					page.pagination.total = r.message.total || 0;
					page.pagination.total_pages = r.message.total_pages || 0;

					// Only rebuild full UI if needed (e.g., stage change)
					// Otherwise just update the table and workflow steps
					if (rebuild_full_ui) {
						page.build_ui();
					} else {
						// Update only the workflow steps and table, keeping filters intact
						page.update_workflow_steps();
						page.update_data_table();
					}

					// Update status counts
					page.load_status_counts();
				}
			},
			error: function (err) {
				frappe.msgprint(__("Error loading orders: {0}", [err.message || "Unknown error"]));
			},
		});
	};

	// View dialog for customer link clicks (read-only view with navigation)
	page.open_view_dialog_with_nav = function (orders_array, initial_index) {
		let current_order_index = initial_index;
		let dialog = null;

		const update_dialog_content = function () {
			const order = orders_array[current_order_index];
			const stage_info = page.get_stage_info();

			// Update content
			const view_html = page.get_view_dialog_html(
				order,
				current_order_index,
				orders_array.length
			);
			dialog.fields_dict.view_content.$wrapper.html(view_html);

			// Update action button labels to show target stage names
			if (stage_info.next) {
				dialog.$wrapper
					.find(".modal-footer .btn-primary")
					.first()
					.text(__("Move To {0}", [stage_info.next]));
			}
			if (stage_info.prev) {
				dialog.$wrapper
					.find(".modal-footer .btn-secondary")
					.first()
					.text(__("Move to {0}", [stage_info.prev]));
			}

			// Setup navigation button handlers
			setTimeout(() => {
				const $prevBtn = dialog.$wrapper.find(".prev-row-btn");
				const $nextBtn = dialog.$wrapper.find(".next-row-btn");

				$prevBtn.off("click").on("click", function (e) {
					e.preventDefault();
					e.stopPropagation();
					if (current_order_index > 0) {
						current_order_index--;
						update_dialog_content();
					}
				});

				$nextBtn.off("click").on("click", function (e) {
					e.preventDefault();
					e.stopPropagation();
					if (current_order_index < orders_array.length - 1) {
						current_order_index++;
						update_dialog_content();
					}
				});
			}, 100);
		};

		dialog = new frappe.ui.Dialog({
			title: __("Details"),
			size: "large",
			fields: [
				{
					fieldname: "view_content",
					fieldtype: "HTML",
					options: "",
				},
			],
			primary_action_label: __("Move To Next Stage"),
			primary_action() {
				const order = orders_array[current_order_index];
				const stage_info = page.get_stage_info();

				if (!stage_info.next) {
					frappe.msgprint(__("Already at last stage"));
					return;
				}

				// Check if this transition needs the weight dialog
				const needs_weight_dialog = page.requires_weight_entry(stage_info.current_index, stage_info.next_index);

				if (needs_weight_dialog) {
					dialog.hide();
					page.open_single_entry_dialog_with_nav([order], 0);
				} else {
					frappe.confirm(
						__("Move this order from {0} to {1}?", [
							stage_info.current,
							stage_info.next,
						]),
						function () {
							page.update_order_status(
								[order.name],
								stage_info.next,
								{},
								function () {
									dialog.hide();
									page.refresh_data();
								}
							);
						}
					);
				}
			},
			secondary_action_label: __("Move to Previous Stage"),
			secondary_action() {
				const order = orders_array[current_order_index];
				const stage_info = page.get_stage_info();

				if (!stage_info.prev) {
					frappe.msgprint(__("Already at first stage"));
					return;
				}

				frappe.confirm(
					__("Move this order from {0} to {1}?", [stage_info.current, stage_info.prev]),
					function () {
						const extra_args = {};
						if (page.needs_revert_timestamp(stage_info.current_index, stage_info.prev_index)) {
							extra_args.received_to_incoming = frappe.datetime.now_datetime();
						}
						page.update_order_status(
							[order.name],
							stage_info.prev,
							extra_args,
							function () {
								dialog.hide();
								page.refresh_data();
							}
						);
					}
				);
			},
		});

		dialog.show();
		dialog.$wrapper.addClass("karigar-view-modal");

		// Initialize content
		update_dialog_content();
	};

	// Generate HTML for view dialog (read-only)
	page.get_view_dialog_html = function (order, current_index, total) {
		return `
			<div class="view-dialog-container" style="padding: 0;">
				<!-- Header Navigation -->
				<div class="entry-navigation" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 0;">
					<div style="flex: 1; text-align: left;">
						<span style="font-size: 14px; color: #6c757d;">${current_index + 1} / ${total}</span>
					</div>
					<div style="flex: 0 0 auto; display: flex; gap: 8px;">
						<button class="btn btn-default btn-sm prev-row-btn" style="padding: 6px 12px; font-size: 13px; border: 1px solid #d1d5db;" ${
							current_index === 0 ? "disabled" : ""
						}>
							← Prev Row
						</button>
						<button class="btn btn-default btn-sm next-row-btn" style="padding: 6px 12px; font-size: 13px; border: 1px solid #d1d5db;" ${
							current_index === total - 1 ? "disabled" : ""
						}>
							Next Row →
						</button>
					</div>
				</div>

				<!-- Order Details -->
				<div style="background: #f8f9fa; border-radius: 6px; padding: 20px;">
					<div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
						<div style="color: #64748b; font-size: 13px; margin-bottom: 4px;">Customer</div>
						<div style="color: #1a202c; font-size: 15px; font-weight: 500;">${order.customer || "N/A"}</div>
					</div>

					<div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
						<div style="color: #64748b; font-size: 13px; margin-bottom: 4px;">Karigar</div>
						<div style="color: #1a202c; font-size: 15px; font-weight: 500;">${order.karigar || "N/A"}</div>
					</div>

					<div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
						<div style="color: #64748b; font-size: 13px; margin-bottom: 4px;">Item Group</div>
						<div style="color: #1a202c; font-size: 15px; font-weight: 500;">${order.item_group || "N/A"}</div>
					</div>

					<div style="margin-bottom: 0;">
						<div style="color: #64748b; font-size: 13px; margin-bottom: 4px;">Item</div>
						<div style="color: #1a202c; font-size: 15px; font-weight: 500;">
							<a href="/app/item/${
								order.item_code || ""
							}" target="_blank" style="color: #2490EF; text-decoration: none;">${
				page.format_item_display(order)
		}</a>
						</div>
					</div>
				</div>
			</div>
		`;
	};

	// Dialog for single entry with navigation (used by dropdown actions)
	page.open_single_entry_dialog_with_nav = function (orders_array, initial_index) {
		let current_order_index = initial_index;
		let dialog = null;

		const update_dialog_content = function () {
			const order = orders_array[current_order_index];
			const stage_info = page.get_stage_info();
			const placeholder = '/assets/frappe/images/ui-states/list-empty-state.svg';
			// Use images array from backend (includes Sales Order Item image + Item master image)
			const images = order.images && order.images.length > 0 ? order.images : [placeholder];

			let current_image_index = 0;

			// Determine weight type based on transition
			const is_pending_to_delivered =
				stage_info.current === "Pending Delivery" && stage_info.next === "Delivered";
			const weight_type = is_pending_to_delivered ? "dispatch" : "received";

			// Update title to show position
			dialog.set_title(
				__("Update Weight and Notes ({0}/{1})", [
					current_order_index + 1,
					orders_array.length,
				])
			);

			// Update content with appropriate weight type
			const new_html = page.get_single_entry_modal_html(
				order,
				images,
				current_image_index,
				weight_type
			);
			dialog.fields_dict.modal_content.$wrapper.html(new_html);

			//add current count to current-image class which is a span
			dialog.$wrapper.find(".current-image").text(current_order_index + 1);

			// Re-setup handlers
			setTimeout(() => {
				page.setup_single_entry_handlers(dialog, images, current_image_index);

				// Add navigation handlers with updated logic
				dialog.$wrapper
					.find(".prev-row-btn")
					.off("click")
					.on("click", function () {
						if (current_order_index > 0) {
							current_order_index--;
							update_dialog_content();
						}
					});

				dialog.$wrapper
					.find(".next-row-btn")
					.off("click")
					.on("click", function () {
						if (current_order_index < orders_array.length - 1) {
							current_order_index++;
							update_dialog_content();
						}
					});

				// Update button states
				dialog.$wrapper.find(".prev-row-btn").prop("disabled", current_order_index === 0);
				dialog.$wrapper
					.find(".next-row-btn")
					.prop("disabled", current_order_index === orders_array.length - 1);
			}, 100);
		};

		dialog = new frappe.ui.Dialog({
			title: __("Update Weight and Notes"),
			size: "large",
			fields: [
				{
					fieldname: "modal_content",
					fieldtype: "HTML",
					options: "",
				},
			],
			primary_action_label: __("Move To Next Stage"),
			primary_action() {
				const order = orders_array[current_order_index];
				const weight = dialog.$wrapper.find(".weight-input").val();
				const notes = dialog.$wrapper.find(".notes-input").val();
				const stage_info = page.get_stage_info();

				if (!stage_info.next) {
					frappe.msgprint(__("Already at last stage"));
					return;
				}

				const weight_type = page.get_weight_type(stage_info.current_index, stage_info.next_index);

				// Transitions that require weight
				if (weight_type) {
					// Validate weight input
					const weightValue = parseFloat(weight);
					if (!weight || isNaN(weightValue) || weightValue <= 0) {
						const weight_label = weight_type === "dispatch" ? "dispatch weight" : "received weight";
						frappe.msgprint(__("Please enter a valid positive {0}", [weight_label]));
						return;
					}
					if (weightValue > CONSTANTS.MAX_REASONABLE_WEIGHT) {
						frappe.msgprint(__("Weight seems unusually high. Please verify."));
						return;
					}

					const extra_args = {};

					if (weight_type === "received") {
						// Incoming (2) → Internal QA (3): update received weight
						extra_args.karigar_received_weight = weight;
						extra_args.receive_notes = notes;
						extra_args.incoming_to_received = frappe.datetime.now_datetime();
					} else if (weight_type === "dispatch") {
						// Pending Delivery (4) → Delivered (5): update dispatch weight
						extra_args.dispatch_weight = weight;
						extra_args.qa_notes = notes;
					}

					page.update_order_status(
						[order.name],
						stage_info.next,
						extra_args,
						function () {
							dialog.hide();
							page.refresh_data();
						}
					);
				} else {
					// Other transitions don't need weight
					page.update_order_status([order.name], stage_info.next, {}, function () {
						dialog.hide();
						page.refresh_data();
					});
				}
			},
			secondary_action_label: __("Move to Previous Stage"),
			secondary_action() {
				const order = orders_array[current_order_index];
				const stage_info = page.get_stage_info();

				if (!stage_info.prev) {
					frappe.msgprint(__("Already at first stage"));
					return;
				}

				const extra_args = {};
				if (page.needs_revert_timestamp(stage_info.current_index, stage_info.prev_index)) {
					extra_args.received_to_incoming = frappe.datetime.now_datetime();
				}

				page.update_order_status([order.name], stage_info.prev, extra_args, function () {
					dialog.hide();
					page.refresh_data();
				});
			},
		});

		dialog.show();
		dialog.$wrapper.addClass("karigar-single-entry-modal");

		// Initialize content
		update_dialog_content();
	};

	// Dialog for single entry (old function kept for dropdown menu compatibility)
	page.open_single_entry_dialog = function (selected_rows) {
		const selected_id = $(selected_rows[0]).data("name");
		const selected_order = page.orders_data.find((order) => order.name === selected_id);

		if (!selected_order) return;

		// Use the new navigation function with single order
		page.open_single_entry_dialog_with_nav([selected_order], 0);
	};

	// Generate HTML for single entry modal
	page.get_single_entry_modal_html = function (order, images, current_index, weight_type) {
		// weight_type can be 'received' (Incoming → Internal QA) or 'dispatch' (Pending Delivery → Delivered)
		weight_type = weight_type || "";

		const item_weight = order.item_weight;
		const item_weight_display = (item_weight !== null && item_weight !== undefined) ? parseFloat(item_weight).toFixed(2) : "-";
		const karigar_received_weight = order.karigar_received_weight;
		const karigar_received_weight_display = (karigar_received_weight !== null && karigar_received_weight !== undefined) ? parseFloat(karigar_received_weight).toFixed(2) : "-";

		const weight_config = {
			received: {
				label: "Received Weight (g)*",
				field_name: "weight-input",
				value: order.karigar_received_weight || 0.0,
				notes_value: order.karigar_notes || "",
			},
			dispatch: {
				label: "Dispatch Weight (g)*",
				field_name: "weight-input",
				value: order.dispatch_weight || 0.0,
				notes_value: order.qa_notes || "",
			},
		};

		const config = weight_config[weight_type];

		// Build weight info section based on transition type
		let weight_info_html = "";
		if (weight_type === "received") {
			// Incoming → Internal QA: Show item weight only
			weight_info_html = `
				<div class="weight-info-section" style="background: #f0f9ff; border-radius: 6px; padding: 12px; margin-bottom: 16px;">
					<div class="weight-info-item" style="display: flex; justify-content: space-between; align-items: center;">
						<span style="color: #64748b; font-size: 13px;">Item Weight (g)</span>
						<span style="color: #1a202c; font-size: 14px; font-weight: 500;">${item_weight_display} g</span>
					</div>
				</div>
			`;
		} else if (weight_type === "dispatch") {
			// Pending Delivery → Delivered: Show item weight and karigar received weight
			weight_info_html = `
				<div class="weight-info-section" style="background: #f0f9ff; border-radius: 6px; padding: 12px; margin-bottom: 16px;">
					<div class="weight-info-item" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
						<span style="color: #64748b; font-size: 13px;">Item Weight (g)</span>
						<span style="color: #1a202c; font-size: 14px; font-weight: 500;">${item_weight_display} g</span>
					</div>
					<div class="weight-info-item" style="display: flex; justify-content: space-between; align-items: center;">
						<span style="color: #64748b; font-size: 13px;">Karigar Received Weight (g)</span>
						<span style="color: #1a202c; font-size: 14px; font-weight: 500;">${karigar_received_weight_display} g</span>
					</div>
				</div>
			`;
		}

		// Only show image section if images exist
		const image_html =
			images && images.length > 0
				? `
        <div class="image-column">
            <div class="image-frame" style="position: relative;">
                <img src="${images[current_index]}" alt="Product" class="product-img main-product-image" data-current-index="${current_index}">

                ${images.length > 1 ? `
                    <!-- Left Navigation Arrow -->
                    <button class="image-nav-btn prev-image-btn" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); background: rgba(255, 255, 255, 0.9); border: 1px solid #ddd; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.15); transition: all 0.2s; z-index: 10;" ${current_index === 0 ? 'disabled' : ''}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="15 18 9 12 15 6"></polyline>
                        </svg>
                    </button>

                    <!-- Right Navigation Arrow -->
                    <button class="image-nav-btn next-image-btn" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: rgba(255, 255, 255, 0.9); border: 1px solid #ddd; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.15); transition: all 0.2s; z-index: 10;" ${current_index === images.length - 1 ? 'disabled' : ''}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </button>
                ` : ''}

                <div class="image-pagination">
                    ${images
						.map(
							(_, idx) => `
                        <span class="dot ${idx === current_index ? "active" : ""}" data-index="${idx}" style="cursor: pointer;"></span>
                    `
						)
						.join("")}
                </div>
            </div>
            <div class="image-counter-text">Image ${current_index + 1} of ${images.length}</div>
        </div>`
				: "";

		return `
<div class="modal-wrapper">
    <div class="modal-header">

        <div class="header-controls">
            <button class="btn btn-outline btn-sm prev-row-btn">Prev Row</button>

            <div class="row-indicator">
                <span class="row-count current-image">1</span>
             </div>

            <button class="btn btn-solid-blue btn-sm next-row-btn">Next Row</button>


        </div>
    </div>

    <div class="content-card">

        ${image_html}

        <div class="details-column">
            <div class="section-title mb-3">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#007bff" stroke-width="2" style="margin-right: 6px;">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Fill Details
            </div>

            ${weight_info_html}

            <div class="">
                <div class="form-group">

                                <label>${config.label}</label>

                                <input type="number" step="0.01" class="form-control ${
									config.field_name
								}" value="${config.value}" placeholder="0.0">

                            </div>

                 <div class="form-group">

                                <label>Notes</label>

                                <textarea class="form-control notes-input" rows="3" placeholder="Write Here">${
									config.notes_value
								}</textarea>

                            </div>
            </div>

            <div class="info-list">
                <div class="info-item">
                    <span class="label">Customer :</span>
                    <span class="value">${order.customer || "N/A"}</span>
                </div>
                <div class="info-item">
                    <span class="label">Karigar :</span>
                    <span class="value">${order.karigar || "N/A"}</span>
                </div>
                <div class="info-item">
                    <span class="label">Item Group :</span>
                    <span class="value">${order.item_group || "N/A"}</span>
                </div>
                <div class="info-item">
                    <span class="label">Item :</span>
                    <span class="value">${page.format_item_display(order)}</span>
                </div>
            </div>
        </div>
    </div>


</div>
`;
	};

	// Set up event handlers for single entry modal
	page.setup_single_entry_handlers = function (dialog, images, current_index) {
		const $wrapper = dialog.$wrapper;

		// Function to update image display
		const updateImageDisplay = function (newIndex) {
			current_index = newIndex;

			// Update main image
			$wrapper
				.find(".main-product-image")
				.attr("src", images[newIndex])
				.data("current-index", newIndex);

			// Update counter text below image
			$wrapper.find(".image-counter-text").text(`Image ${newIndex + 1} of ${images.length}`);

			// Update pagination dots
			$wrapper.find(".dot").removeClass("active");
			$wrapper.find(`.dot[data-index="${newIndex}"]`).addClass("active");

			// Update button states
			$wrapper.find(".prev-image-btn").prop("disabled", newIndex === 0);
			$wrapper.find(".next-image-btn").prop("disabled", newIndex === images.length - 1);

			// Update button opacity for visual feedback
			if (newIndex === 0) {
				$wrapper.find(".prev-image-btn").css("opacity", "0.5");
			} else {
				$wrapper.find(".prev-image-btn").css("opacity", "1");
			}

			if (newIndex === images.length - 1) {
				$wrapper.find(".next-image-btn").css("opacity", "0.5");
			} else {
				$wrapper.find(".next-image-btn").css("opacity", "1");
			}
		};

		// Previous image button
		$wrapper.find(".prev-image-btn").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			if (current_index > 0) {
				updateImageDisplay(current_index - 1);
			}
		});

		// Next image button
		$wrapper.find(".next-image-btn").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			if (current_index < images.length - 1) {
				updateImageDisplay(current_index + 1);
			}
		});

		// Dot pagination click handler
		$wrapper.find(".dot").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			const clickedIndex = parseInt($(this).data("index"));
			if (clickedIndex !== current_index) {
				updateImageDisplay(clickedIndex);
			}
		});

		// Keyboard navigation (left/right arrows)
		$(document).off("keydown.image-nav").on("keydown.image-nav", function (e) {
			if (!dialog.$wrapper.is(":visible")) return;

			if (e.key === "ArrowLeft" && current_index > 0) {
				e.preventDefault();
				updateImageDisplay(current_index - 1);
			} else if (e.key === "ArrowRight" && current_index < images.length - 1) {
				e.preventDefault();
				updateImageDisplay(current_index + 1);
			}
		});

		// Clean up keyboard listener when dialog closes
		dialog.$wrapper.on("hidden.bs.modal", function () {
			$(document).off("keydown.image-nav");
		});
	};

	// Dialog for multiple entries
	page.open_multiple_entries_dialog = function (selected_rows) {
		const selected_ids = [];
		const selected_orders = [];

		selected_rows.each(function () {
			const id = $(this).data("name");
			selected_ids.push(id);
			const order = page.orders_data.find((o) => o.name === id);
			if (order) selected_orders.push(order);
		});

		const dialog = new frappe.ui.Dialog({
			title: __("Update Weight (Selected Rows : {0})", [selected_ids.length]),
			size: "medium",
			fields: [
				{
					fieldname: "bulk_content",
					fieldtype: "HTML",
					options: page.get_bulk_entry_modal_html(selected_orders),
				},
			],
			primary_action_label: __("Move To Next Stage"),
			primary_action() {
				const stage_info = page.get_stage_info();

				if (!stage_info.next) {
					frappe.msgprint(__("Already at last stage"));
					return;
				}

				// Determine which weight field to update based on stage transition
				const weight_type = page.get_weight_type(stage_info.current_index, stage_info.next_index);
				let weight_field = null;

				if (weight_type === "received") {
					weight_field = "karigar_received_weight";
				} else if (weight_type === "dispatch") {
					weight_field = "dispatch_weight";
				}

				// Get the total weight from input
				const weight_input_value = dialog.$wrapper.find(".bulk-weight-input").val();
				const total_weight = parseFloat(weight_input_value) || 0;

				// Validate weight input if required
				if (weight_field) {
					if (!weight_input_value || weight_input_value.trim() === "" || isNaN(total_weight) || total_weight <= 0) {
						const weight_label = weight_type === "dispatch" ? "dispatch weight" : "received weight";
						frappe.msgprint(__("Please enter a valid positive {0} for bulk update", [weight_label]));
						return;
					}
					if (total_weight > CONSTANTS.MAX_REASONABLE_WEIGHT) {
						frappe.msgprint(__("Weight seems unusually high. Please verify."));
						return;
					}
				}

				// Calculate total quantity from all selected orders
				const total_qty = selected_orders.reduce(
					(sum, order) => sum + (parseFloat(order.qty) || 0),
					0
				);

				// Calculate weight per unit (weight per single quantity)
				const weight_per_unit = total_qty > 0 ? total_weight / total_qty : 0;

				// Prepare extra args with weight information
				const extra_args = {};
				if (weight_field && total_weight > 0) {
					extra_args.weight_per_unit = weight_per_unit;
					extra_args.weight_field = weight_field;
				}

				page.update_order_status(selected_ids, stage_info.next, extra_args, function () {
					dialog.hide();
					page.refresh_data();
				});
			},
			secondary_action_label: __("Move to Previous Stage"),
			secondary_action() {
				const stage_info = page.get_stage_info();

				if (!stage_info.prev) {
					frappe.msgprint(__("Already at first stage"));
					return;
				}

				page.update_order_status(selected_ids, stage_info.prev, {}, function () {
					dialog.hide();
					page.refresh_data();
				});
			},
		});

		dialog.show();
		dialog.$wrapper.addClass("karigar-bulk-entry-modal");

		// Center the modal on screen
		setTimeout(() => {
			const $modal = dialog.$wrapper.find(".modal-dialog");
			$modal.css({
				"margin-top": "0",
				"margin-bottom": "0",
				top: "50%",
				transform: "translateY(-50%)",
			});
		}, 0);
	};

	// Generate HTML for bulk entry modal
	page.get_bulk_entry_modal_html = function (orders) {
		return `
			<div class="bulk-entry-container">
				<div class="bulk-fill-details-header">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M3 5h14M3 10h14M3 15h14" stroke="#2490EF" stroke-width="2" stroke-linecap="round"/>
					</svg>
					<span>Fill Details</span>
				</div>
				<div class="bulk-form-fields">
					<div class="form-group">
						<label class="bulk-weight-label">Weight (g)*</label>
						<input type="number" step="0.01" class="form-control bulk-weight-input" value="0.0" placeholder="0.0 grams">
					</div>
				</div>
			</div>
		`;
	};

	// Open split modal
	page.open_split_modal = function (selected_orders) {
		let selected_item_index = 0;
		let item_split_qty = {};

		// Initialize split quantities to 0
		selected_orders.forEach((order, idx) => {
			item_split_qty[idx] = 0;
		});

		const update_split_modal_content = function () {
			const selected_order = selected_orders[selected_item_index];
			const total_qty = parseFloat(selected_order.qty) || 0;

			// Update the selected item in the list
			dialog.$wrapper.find(".split-item").removeClass("selected");
			dialog.$wrapper
				.find(`.split-item[data-index="${selected_item_index}"]`)
				.addClass("selected");

			// Update the details panel
			dialog.$wrapper.find(".split-customer-value").text(selected_order.customer || "N/A");
			dialog.$wrapper.find(".split-karigar-value").text(selected_order.karigar || "N/A");
			dialog.$wrapper
				.find(".split-item-group-value")
				.text(selected_order.item_group || "N/A");
			dialog.$wrapper.find(".split-item-code-value").text(page.format_item_display(selected_order));
			dialog.$wrapper.find(".split-total-qty-value").text(total_qty);

			// Update split qty input with saved value and set max attribute
			const $input = dialog.$wrapper.find(".split-qty-input");
			$input.val(item_split_qty[selected_item_index]);
			$input.attr("max", total_qty);

			// Update remaining quantity display
			const split_qty = item_split_qty[selected_item_index] || 0;
			const remaining_qty = total_qty - split_qty;
			dialog.$wrapper.find(".split-remaining-qty-value").text(remaining_qty);
		};

		const split_modal_html = `
			<div class="split-modal-container">
				<div class="split-modal-header">
					<div class="split-header-text">Select an item to edit its value</div>
				</div>
				<div class="split-modal-content">
					<div class="split-left-panel">
						<div class="split-items-list">
							${selected_orders
								.map(
									(order, idx) => `
								<div class="split-item ${idx === 0 ? "selected" : ""}" data-index="${idx}">
									<div class="split-item-id">${order.name}</div>
								</div>
							`
								)
								.join("")}
						</div>
					</div>
					<div class="split-right-panel">
						<div class="split-details-section">
							<div class="split-detail-row">
								<span class="split-detail-label">Customer:</span>
								<span class="split-detail-value split-customer-value">${
									selected_orders[0].customer || "N/A"
								}</span>
							</div>
							<div class="split-detail-row">
								<span class="split-detail-label">Karigar:</span>
								<span class="split-detail-value split-karigar-value">${selected_orders[0].karigar || "N/A"}</span>
							</div>
							<div class="split-detail-row">
								<span class="split-detail-label">Item Group:</span>
								<span class="split-detail-value split-item-group-value">${
									selected_orders[0].item_group || "N/A"
								}</span>
							</div>
							<div class="split-detail-row">
								<span class="split-detail-label">Item Code:</span>
								<span class="split-detail-value split-item-code-value">${
									selected_orders[0].item_code || "N/A"
								}</span>
							</div>
							<div class="split-detail-row">
								<span class="split-detail-label">Total Quantity:</span>
								<span class="split-detail-value split-total-qty-value">${selected_orders[0].qty || 0}</span>
							</div>
						</div>
						<div class="split-weight-section">
							<label class="split-weight-label">Split Quantity</label>
							<input type="number" step="1" min="0" max="${
								selected_orders[0].qty || 0
							}" class="form-control split-qty-input" value="0" placeholder="Enter quantity to split...">
							<div class="split-qty-info">
								<span class="split-qty-info-text">Remaining: <strong class="split-remaining-qty-value">${
									selected_orders[0].qty || 0
								}</strong></span>
							</div>
						</div>
					</div>
				</div>
			</div>
		`;

		const dialog = new frappe.ui.Dialog({
			title: __("Edit Item Values ({0} Items Selected)", [selected_orders.length]),
			size: "large",
			fields: [
				{
					fieldname: "split_content",
					fieldtype: "HTML",
					options: split_modal_html,
				},
			],
			primary_action_label: __("Done"),
			primary_action() {
				dialog.hide();
				page.refresh_data();
			},
			secondary_action_label: __("Cancel"),
			secondary_action() {
				dialog.hide();
			},
		});

		dialog.show();
		dialog.$wrapper.addClass("karigar-split-modal");

		// Setup event handlers after dialog is shown
		setTimeout(() => {
			// Handle item click
			dialog.$wrapper.find(".split-item").on("click", function () {
				// Save current qty before switching
				const current_qty =
					parseFloat(dialog.$wrapper.find(".split-qty-input").val()) || 0;
				item_split_qty[selected_item_index] = current_qty;

				// Switch to clicked item
				selected_item_index = parseInt($(this).data("index"));
				update_split_modal_content();
			});

			// Handle qty input change with validation and remaining update
			dialog.$wrapper.find(".split-qty-input").on("input", function () {
				const selected_order = selected_orders[selected_item_index];
				const total_qty = parseFloat(selected_order.qty) || 0;
				let split_qty = parseFloat($(this).val()) || 0;

				// Validate: don't allow more than total quantity
				if (split_qty > total_qty) {
					split_qty = total_qty;
					$(this).val(total_qty);
					frappe.show_alert({
						message: __("Split quantity cannot exceed total quantity"),
						indicator: "orange",
					});
				}

				// Don't allow negative values
				if (split_qty < 0) {
					split_qty = 0;
					$(this).val(0);
				}

				item_split_qty[selected_item_index] = split_qty;

				// Update remaining quantity display
				const remaining_qty = total_qty - split_qty;
				dialog.$wrapper.find(".split-remaining-qty-value").text(remaining_qty);
			});

			// Add Save button handler (individual save)
			const save_btn_html =
				'<button class="btn btn-primary btn-sm split-save-btn" style="margin-top: 15px; width: 100%;">Save</button>';
			dialog.$wrapper.find(".split-weight-section").append(save_btn_html);

			dialog.$wrapper.find(".split-save-btn").on("click", function () {
				const selected_order = selected_orders[selected_item_index];
				const split_qty = parseFloat(dialog.$wrapper.find(".split-qty-input").val());
				const total_qty = parseFloat(selected_order.qty) || 0;

				if (!split_qty || split_qty <= 0) {
					frappe.msgprint(__("Please enter a valid quantity to split"));
					return;
				}

				if (split_qty >= total_qty) {
					frappe.msgprint(__("Split quantity must be less than total quantity"));
					return;
				}

				// Confirm split action
				const remaining_qty = total_qty - split_qty;
				frappe.confirm(
					__("This will split the entry into two: {0} qty and {1} qty. Continue?", [
						split_qty,
						remaining_qty,
					]),
					function () {
						frappe.call({
							method: "ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.split_order_item",
							args: {
								item_name: selected_order.name,
								split_qty: split_qty,
							},
							freeze: true,
							freeze_message: __("Splitting order..."),
							callback: function (r) {
								if (r.message && r.message.success) {
									frappe.show_alert({
										message: __("Successfully created duplicate entries"),
										indicator: "green",
									});
									// Reset the split qty for this item
									item_split_qty[selected_item_index] = 0;
									// Close the modal and refresh
									dialog.hide();
									page.refresh_data();
								} else {
									frappe.msgprint(
										__("Error splitting order: {0}", [
											r.message?.error || "Unknown error",
										])
									);
								}
							},
							error: function (err) {
								frappe.msgprint(
									__("Error splitting order: {0}", [
										err.message || "Unknown error",
									])
								);
							},
						});
					}
				);
			});
		}, 100);
	};
};
