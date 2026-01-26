import "./commands";
// import "@cypress/code-coverage/support";

Cypress.on("uncaught:exception", (err, runnable) => {
	// returning false here prevents Cypress from failing the test
    // We want to ignore benign application errors that don't break functionality
	return false;
});
