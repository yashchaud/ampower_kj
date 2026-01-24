/**
 * Logger Utility for Custom Workflow
 *
 * Provides consistent logging with:
 * - Dev-only debug/info logs
 * - Always-on warn/error logs
 * - Prefixed messages for easy filtering
 */

const PREFIX = '[CustomWorkflow]';

/**
 * Check if we're in development mode
 * @returns {boolean}
 */
function isDev() {
  // Check Frappe's developer_mode
  if (typeof window !== 'undefined' && window.frappe && window.frappe.boot && window.frappe.boot.developer_mode) {
    return true;
  }
  return false;
}

/**
 * Logger object with debug, info, warn, and error methods
 */
export const logger = {
  /**
   * Debug level - only logs in development mode
   * Use for detailed debugging information
   * @param {...any} args - Arguments to log
   */
  debug(...args) {
    if (isDev()) {
      console.debug(PREFIX, ...args);
    }
  },

  /**
   * Info level - only logs in development mode
   * Use for general informational messages
   * @param {...any} args - Arguments to log
   */
  info(...args) {
    if (isDev()) {
      console.info(PREFIX, ...args);
    }
  },

  /**
   * Warn level - always logs
   * Use for warnings that don't stop execution
   * @param {...any} args - Arguments to log
   */
  warn(...args) {
    console.warn(PREFIX, ...args);
  },

  /**
   * Error level - always logs
   * Use for errors and exceptions
   * @param {...any} args - Arguments to log
   */
  error(...args) {
    console.error(PREFIX, ...args);
  }
};

export default logger;
