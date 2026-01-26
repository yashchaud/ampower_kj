// Component testing support file for Vue components
import { mount } from 'cypress/vue';
import '@testing-library/cypress/add-commands';

// Add custom mount command
Cypress.Commands.add('mount', mount);

// Add custom command for testing Vue component props
Cypress.Commands.add('mountWithProps', (component, options = {}) => {
	return mount(component, {
		...options,
		global: {
			...options.global,
		},
	});
});

// Suppress uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
	// Return false to prevent the error from failing the test
	return false;
});

// Add custom commands for common test patterns
Cypress.Commands.add('getByTestId', (testId) => {
	return cy.get(`[data-testid="${testId}"]`);
});

Cypress.Commands.add('findByTestId', { prevSubject: 'element' }, (subject, testId) => {
	return cy.wrap(subject).find(`[data-testid="${testId}"]`);
});
