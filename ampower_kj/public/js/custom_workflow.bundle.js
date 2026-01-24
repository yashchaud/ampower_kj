/**
 * Custom Workflow Vue Bundle
 *
 * This bundle provides Vue 3 components for the Custom Workflow page.
 * It mounts a Vue application into the Frappe page container.
 */

import { createApp } from 'vue';
import CustomWorkflow from './vue_components/CustomWorkflow.vue';
import { logger } from './utils/logger.js';

// Export the setup function to the frappe namespace
frappe.provide('ampower_kj.ui');

/**
 * Sets up and mounts the Custom Workflow Vue application
 * @param {jQuery|HTMLElement} $wrapper - The container element to mount into
 * @param {Object} options - Optional configuration options
 * @returns {Object} The Vue app instance
 */
ampower_kj.ui.setup_custom_workflow = function($wrapper, options = {}) {
  // Get the DOM element
  const container = $wrapper instanceof jQuery ? $wrapper.get(0) : $wrapper;

  // Create a mount point inside the container
  const mountPoint = document.createElement('div');
  mountPoint.id = 'custom-workflow-app';
  mountPoint.className = 'custom-workflow-vue-app';
  container.appendChild(mountPoint);

  // Create the Vue app
  const app = createApp(CustomWorkflow, {
    frappe: window.frappe,
    ...options
  });

  // Mount the app
  app.mount(mountPoint);

  // Return the app instance for potential cleanup
  return app;
};

/**
 * Destroys the Custom Workflow Vue application
 * @param {Object} app - The Vue app instance to destroy
 */
ampower_kj.ui.destroy_custom_workflow = function(app) {
  if (app && typeof app.unmount === 'function') {
    app.unmount();
  }
};

// Log that the bundle is loaded (only in dev mode)
logger.debug('Vue bundle loaded');
