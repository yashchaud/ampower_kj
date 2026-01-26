import CwBadge from './CwBadge.vue';

describe('CwBadge Component', () => {
	// Basic rendering tests
	it('should render with default props', () => {
		cy.mount(CwBadge);
		cy.get('span').should('exist');
		cy.get('span').should('have.class', 'tw-inline-flex');
	});

	it('should render with label text', () => {
		cy.mount(CwBadge, {
			props: {
				label: 'Test Badge'
			}
		});
		cy.contains('Test Badge').should('be.visible');
	});

	it('should render slot content', () => {
		cy.mount(CwBadge, {
			slots: {
				default: 'Custom Slot Content'
			}
		});
		cy.contains('Custom Slot Content').should('be.visible');
	});

	// Size variant tests
	describe('Size Variants', () => {
		it('should apply small size classes', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Small',
					size: 'sm'
				}
			});
			cy.get('span').should('have.class', 'tw-px-1.5');
			cy.get('span').should('have.class', 'tw-text-[10px]');
		});

		it('should apply medium size classes (default)', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Medium',
					size: 'md'
				}
			});
			cy.get('span').should('have.class', 'tw-px-2');
			cy.get('span').should('have.class', 'tw-text-xs');
		});

		it('should apply large size classes', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Large',
					size: 'lg'
				}
			});
			cy.get('span').should('have.class', 'tw-px-2.5');
			cy.get('span').should('have.class', 'tw-text-sm');
		});
	});

	// Color variant tests
	describe('Color Variants', () => {
		const variants = [
			{ name: 'default', bgClass: 'tw-bg-slate-100', textClass: 'tw-text-slate-700' },
			{ name: 'unassigned', bgClass: 'tw-bg-amber-100', textClass: 'tw-text-amber-800' },
			{ name: 'assigned', bgClass: 'tw-bg-blue-100', textClass: 'tw-text-blue-800' },
			{ name: 'incoming', bgClass: 'tw-bg-violet-100', textClass: 'tw-text-violet-800' },
			{ name: 'qa', bgClass: 'tw-bg-cyan-100', textClass: 'tw-text-cyan-800' },
			{ name: 'ready', bgClass: 'tw-bg-emerald-100', textClass: 'tw-text-emerald-800' },
			{ name: 'delivered', bgClass: 'tw-bg-green-100', textClass: 'tw-text-green-800' },
			{ name: 'cancelled', bgClass: 'tw-bg-red-100', textClass: 'tw-text-red-800' },
			{ name: 'primary', bgClass: 'tw-bg-primary-100', textClass: 'tw-text-primary-800' },
			{ name: 'success', bgClass: 'tw-bg-green-100', textClass: 'tw-text-green-800' },
			{ name: 'warning', bgClass: 'tw-bg-amber-100', textClass: 'tw-text-amber-800' },
			{ name: 'danger', bgClass: 'tw-bg-red-100', textClass: 'tw-text-red-800' },
		];

		variants.forEach(({ name, bgClass, textClass }) => {
			it(`should apply ${name} variant classes`, () => {
				cy.mount(CwBadge, {
					props: {
						label: name,
						variant: name
					}
				});
				cy.get('span').first().should('have.class', bgClass);
				cy.get('span').first().should('have.class', textClass);
			});
		});
	});

	// Dot indicator tests
	describe('Dot Indicator', () => {
		it('should not show dot by default', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'No Dot'
				}
			});
			cy.get('span > span').should('not.exist');
		});

		it('should show dot when showDot is true', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'With Dot',
					showDot: true
				}
			});
			cy.get('span > span').should('exist');
			cy.get('span > span').should('have.class', 'tw-w-1.5');
			cy.get('span > span').should('have.class', 'tw-h-1.5');
			cy.get('span > span').should('have.class', 'tw-rounded-full');
		});

		it('should apply correct dot color for variant', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Success',
					variant: 'success',
					showDot: true
				}
			});
			cy.get('span > span').should('have.class', 'tw-bg-green-500');
		});
	});

	// Combination tests
	describe('Prop Combinations', () => {
		it('should handle all props together', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Complete Test',
					variant: 'primary',
					size: 'lg',
					showDot: true
				}
			});
			cy.contains('Complete Test').should('be.visible');
			cy.get('span').first().should('have.class', 'tw-bg-primary-100');
			cy.get('span').first().should('have.class', 'tw-px-2.5');
			cy.get('span > span').should('have.class', 'tw-bg-primary-500');
		});
	});

	// Accessibility tests
	describe('Accessibility', () => {
		it('should be keyboard accessible', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Accessible Badge'
				}
			});
			cy.get('span').should('be.visible');
		});

		it('should have proper contrast for text', () => {
			// Visual regression or contrast checking could be added here
			cy.mount(CwBadge, {
				props: {
					label: 'High Contrast',
					variant: 'danger'
				}
			});
			cy.get('span').should('have.class', 'tw-text-red-800');
		});
	});

	// Visual snapshot tests (requires cypress-plugin-snapshots or similar)
	describe('Visual Tests', () => {
		it('should match snapshot for default state', () => {
			cy.mount(CwBadge, {
				props: {
					label: 'Snapshot Test'
				}
			});
			// Uncomment if you have snapshot plugin installed
			// cy.get('span').matchImageSnapshot('badge-default');
		});
	});
});
