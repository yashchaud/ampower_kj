// Example: More advanced component test with events and interactions
import CwDropdown from './CwDropdown.vue';

describe('CwDropdown Component', () => {
	// Note: This is a template - adjust based on your actual CwDropdown implementation

	it('should render dropdown trigger', () => {
		cy.mount(CwDropdown, {
			props: {
				label: 'Select Option'
			}
		});
		cy.contains('Select Option').should('be.visible');
	});

	it('should toggle dropdown on click', () => {
		cy.mount(CwDropdown, {
			props: {
				label: 'Menu',
				items: [
					{ label: 'Option 1', value: '1' },
					{ label: 'Option 2', value: '2' }
				]
			}
		});

		// Dropdown should be closed initially
		cy.get('[data-testid="dropdown-menu"]').should('not.exist');

		// Click to open
		cy.contains('Menu').click();
		cy.get('[data-testid="dropdown-menu"]').should('be.visible');

		// Click again to close
		cy.contains('Menu').click();
		cy.get('[data-testid="dropdown-menu"]').should('not.exist');
	});

	it('should emit select event when item clicked', () => {
		const onSelectSpy = cy.spy().as('selectSpy');

		cy.mount(CwDropdown, {
			props: {
				label: 'Menu',
				items: [
					{ label: 'Option 1', value: '1' },
					{ label: 'Option 2', value: '2' }
				],
				onSelect: onSelectSpy
			}
		});

		cy.contains('Menu').click();
		cy.contains('Option 1').click();

		cy.get('@selectSpy').should('have.been.calledWith', '1');
	});

	it('should close dropdown when clicking outside', () => {
		cy.mount(CwDropdown, {
			props: {
				label: 'Menu',
				items: [{ label: 'Option 1', value: '1' }]
			}
		});

		cy.contains('Menu').click();
		cy.get('[data-testid="dropdown-menu"]').should('be.visible');

		// Click outside
		cy.get('body').click(0, 0);
		cy.get('[data-testid="dropdown-menu"]').should('not.exist');
	});

	it('should handle keyboard navigation', () => {
		cy.mount(CwDropdown, {
			props: {
				label: 'Menu',
				items: [
					{ label: 'Option 1', value: '1' },
					{ label: 'Option 2', value: '2' },
					{ label: 'Option 3', value: '3' }
				]
			}
		});

		// Open with Enter
		cy.contains('Menu').focus().type('{enter}');
		cy.get('[data-testid="dropdown-menu"]').should('be.visible');

		// Navigate with arrow keys
		cy.focused().type('{downarrow}');
		cy.focused().should('contain', 'Option 1');

		// Close with Escape
		cy.focused().type('{esc}');
		cy.get('[data-testid="dropdown-menu"]').should('not.exist');
	});

	it('should disabled state', () => {
		cy.mount(CwDropdown, {
			props: {
				label: 'Menu',
				disabled: true,
				items: [{ label: 'Option 1', value: '1' }]
			}
		});

		cy.contains('Menu').should('have.attr', 'disabled');
		cy.contains('Menu').click({ force: true });
		cy.get('[data-testid="dropdown-menu"]').should('not.exist');
	});

	it('should render with custom slot content', () => {
		cy.mount(CwDropdown, {
			slots: {
				trigger: '<button data-testid="custom-trigger">Custom Trigger</button>',
				default: '<div data-testid="custom-item">Custom Item</div>'
			}
		});

		cy.getByTestId('custom-trigger').should('be.visible');
		cy.getByTestId('custom-trigger').click();
		cy.getByTestId('custom-item').should('be.visible');
	});
});
