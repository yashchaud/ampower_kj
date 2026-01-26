const path = require("path");

module.exports = {
  projectId: "ampower_kj",
  env: {
    adminPassword: "admin"
  },
  defaultCommandTimeout: 10000,
  pageLoadTimeout: 20000,
  video: false,
  viewportHeight: 960,
  viewportWidth: 1400,
  // Memory optimization settings
  numTestsKeptInMemory: 0,
  experimentalMemoryManagement: true,
  e2e: {
    setupNodeEvents(on, config) {
      // Clear memory between specs
      on('after:spec', () => {
        if (global.gc) {
          global.gc();
        }
      });

      // Use Frappe's plugins (code coverage)
      return require(path.resolve(__dirname, "../frappe/cypress/plugins/index.js"))(on, config);
    },
    testIsolation: false,
    baseUrl: "http://localhost:8000",
    specPattern: ["./cypress/integration/*.cy.js"],
    supportFile: "./cypress/support/e2e.js",
  },
};
