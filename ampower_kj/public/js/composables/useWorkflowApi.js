/**
 * Vue 3 Composable for Workflow API
 * Provides methods to interact with Order Ledger backend APIs
 */

import { ref } from 'vue';
import { logger } from '../utils/logger.js';

export function useWorkflowApi() {
  const isLoading = ref(false);
  const error = ref(null);

  /**
   * Centralized error handler for API calls
   * @param {Error|Object} err - The error object
   * @param {string} context - Description of what operation failed
   * @param {boolean} showToUser - Whether to show error message to user
   */
  function handleApiError(err, context, showToUser = true) {
    // Extract error message from various error formats
    let serverMessage;
    if (err?._server_messages) {
      try {
        const parsed = JSON.parse(err._server_messages);
        serverMessage = Array.isArray(parsed) ? parsed[0] : parsed;
      } catch {
        serverMessage = err._server_messages;
      }
    }

    const errorMessage = err?.exc_type
      ? err.message
      : serverMessage
        ? serverMessage
        : err?.message || `Failed to ${context}`;

    error.value = errorMessage;

    // Log error with context for debugging
    logger.error(`${context}:`, err);

    // Show user-friendly message if requested
    if (showToUser && typeof frappe !== 'undefined' && frappe?.msgprint) {
      frappe.msgprint({
        title: 'Error',
        message: errorMessage,
        indicator: 'red'
      });
    }
  }

  /**
   * Fetch workflow stages from backend
   * @returns {Promise<Array<string>>} Array of workflow stage names
   */
  async function fetchWorkflowStages() {
    try {
      isLoading.value = true;
      error.value = null;

      logger.debug('Fetching workflow stages...');

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_workflow_status'
      });

      logger.debug('Workflow stages fetched:', response.message);
      return response.message || [];
    } catch (err) {
      handleApiError(err, 'fetch workflow stages');
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch paginated orders with filters
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (1-based)
   * @param {number} params.pageSize - Items per page
   * @param {string} params.orderStatus - Filter by workflow stage
   * @param {string} params.search - Search term
   * @param {string} params.customer - Filter by customer
   * @param {string} params.karigar - Filter by karigar
   * @param {string} params.itemName - Filter by item name/die
   * @param {string} params.sortBy - Column to sort by
   * @param {string} params.sortOrder - Sort direction ('asc' or 'desc')
   * @returns {Promise<Object>} Paginated response with data, total, total_pages
   */
  async function fetchOrders({
    page = 1,
    pageSize = 50,
    orderStatus = '',
    search = '',
    customer = '',
    karigar = '',
    itemName = '',
    sortBy = '',
    sortOrder = 'asc'
  } = {}) {
    try {
      isLoading.value = true;
      error.value = null;

      logger.debug('Fetching orders with params:', {
        page,
        pageSize,
        orderStatus,
        search,
        customer,
        karigar,
        itemName,
        sortBy,
        sortOrder
      });

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_all_order_items',
        args: {
          page: page,
          page_size: pageSize,
          order_status: orderStatus,
          search: search,
          customer: customer,
          karigar: karigar,
          item_name: itemName,
          sort_by: sortBy,
          sort_order: sortOrder
        }
      });

      logger.debug('Orders fetched:', {
        total: response.message?.total,
        count: response.message?.data?.length
      });

      return response.message || { data: [], total: 0, total_pages: 0 };
    } catch (err) {
      handleApiError(err, 'fetch orders');
      return { data: [], total: 0, total_pages: 0 };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch status counts for all workflow stages
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Object>} Object with stage names as keys and counts as values
   */
  async function fetchStatusCounts({
    search = '',
    customer = '',
    karigar = '',
    itemName = ''
  } = {}) {
    try {
      logger.debug('Fetching status counts...');

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_all_order_items',
        args: {
          return_counts_only: true,
          search: search,
          customer: customer,
          karigar: karigar,
          item_name: itemName
        }
      });

      logger.debug('Status counts fetched:', response.message);
      return response.message || {};
    } catch (err) {
      // Don't show user message for count errors - not critical
      handleApiError(err, 'fetch status counts', false);
      return {};
    }
  }

  /**
   * Fetch filter options for autocomplete
   * @returns {Promise<Object>} Object with customers, karigars, item_names arrays
   */
  async function fetchFilterOptions() {
    try {
      logger.debug('Fetching filter options...');

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.get_filter_options'
      });

      logger.debug('Filter options fetched:', {
        customers: response.message?.customers?.length,
        karigars: response.message?.karigars?.length,
        itemNames: response.message?.item_names?.length
      });

      return response.message || { customers: [], karigars: [], item_names: [] };
    } catch (err) {
      // Don't show user message for filter options - not critical
      handleApiError(err, 'fetch filter options', false);
      return { customers: [], karigars: [], item_names: [] };
    }
  }

  /**
   * Update order item status with optional weight and notes
   * @param {Array<string>} itemNames - Array of Order Ledger names
   * @param {string} newStatus - Target workflow status
   * @param {Object} extraArgs - Additional fields (weights, notes, timestamps)
   * @returns {Promise<Array>} Array of results for each item
   */
  async function updateOrderStatus(itemNames, newStatus, extraArgs = {}) {
    try {
      isLoading.value = true;
      error.value = null;

      logger.debug('Updating order status:', {
        items: itemNames.length,
        newStatus,
        extraArgs: Object.keys(extraArgs)
      });

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.update_item_status',
        args: {
          item_names: JSON.stringify(itemNames),
          new_status: newStatus,
          ...extraArgs
        },
        freeze: true,
        freeze_message: 'Updating status...'
      });

      logger.debug('Order status updated:', response.message);
      return response.message || [];
    } catch (err) {
      handleApiError(err, 'update order status');
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Split an order item into two entries
   * @param {string} itemName - Order Ledger name to split
   * @param {number} splitQty - Quantity to keep in original (remainder goes to new entry)
   * @returns {Promise<Object>} Result with success flag and new entry details
   */
  async function splitOrder(itemName, splitQty) {
    try {
      isLoading.value = true;
      error.value = null;

      logger.debug('Splitting order:', { itemName, splitQty });

      const response = await frappe.call({
        method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.split_order_item',
        args: {
          item_name: itemName,
          split_qty: splitQty
        },
        freeze: true,
        freeze_message: 'Splitting order...'
      });

      logger.debug('Order split result:', response.message);
      return response.message || { success: false };
    } catch (err) {
      handleApiError(err, 'split order');
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Setup real-time WebSocket listener for batch progress
   * @param {Function} callback - Function to call when batch completes
   * @returns {Function} Cleanup function to remove listener
   */
  function setupRealtimeListener(callback) {
    const eventName = 'karigar_batch_progress';

    logger.debug('Setting up realtime listener for:', eventName);

    const handler = (data) => {
      // Only process if it's for karigar-dashboard and batch is complete
      if (data.data_import === 'karigar-dashboard' && data.current === data.total) {
        logger.debug('Realtime batch complete:', data);
        callback(data);
      }
    };

    frappe.realtime.on(eventName, handler);

    // Return cleanup function
    return () => {
      logger.debug('Cleaning up realtime listener');
      frappe.realtime.off(eventName, handler);
    };
  }

  return {
    // State
    isLoading,
    error,

    // Methods
    fetchWorkflowStages,
    fetchOrders,
    fetchStatusCounts,
    fetchFilterOptions,
    updateOrderStatus,
    splitOrder,
    setupRealtimeListener
  };
}
