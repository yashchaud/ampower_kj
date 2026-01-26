const { defineConfig } = require("cypress");
const path = require("path");

module.exports = defineConfig({
	projectId: "ampower-component-tests",
	defaultCommandTimeout: 10000,
	video: false,
	viewportHeight: 768,
	viewportWidth: 1024,

	component: {
		devServer: {
			framework: "vue",
			bundler: "vite",
			viteConfig: {
				resolve: {
					alias: {
						"@": path.resolve(__dirname, "./ampower_kj/public/js"),
					},
				},
				server: {
					fs: {
						// Allow serving files from Frappe framework
						allow: [
							path.resolve(__dirname, "../../"),
						],
					},
				},
			},
		},
		specPattern: "**/*.cy.{js,jsx,ts,tsx,vue}",
		supportFile: "cypress/support/component.js",
		indexHtmlFile: "cypress/support/component-index.html",
	},
});
