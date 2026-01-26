# Vue Component Testing with Cypress in Frappe

This guide explains how to write and run component tests for Vue components in your Frappe app using Cypress.

## Prerequisites

The following packages should already be installed in your Frappe bench:
- `cypress` (v13+)
- `@testing-library/cypress`
- `cypress/vue` (for component testing)

If not installed, add them to your app's `package.json`:

```bash
cd apps/ampower_kj
npm install --save-dev cypress @cypress/vue @testing-library/cypress
```

## Project Structure

```
apps/ampower_kj/
├── cypress/
│   └── support/
│       ├── component.js          # Component test support file
│       └── component-index.html  # HTML template for component tests
├── cypress.component.config.js   # Cypress component config
└── ampower_kj/public/js/vue_components/
    ├── CwBadge.vue              # Your Vue component
    └── CwBadge.cy.js            # Component test file
```

## Running Component Tests

### From your app directory:

```bash
# Open Cypress UI for component testing
npx cypress open --component --config-file cypress.component.config.js

# Run component tests in headless mode
npx cypress run --component --config-file cypress.component.config.js

# Run specific test file
npx cypress run --component --spec "ampower_kj/public/js/vue_components/CwBadge.cy.js"
```

### From bench directory:

```bash
# Run tests from bench root
cd apps/ampower_kj
npx cypress open --component --config-file cypress.component.config.js
```

## Writing Component Tests

### Basic Test Structure

Create a `.cy.js` file next to your Vue component:

```javascript
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
	it('should render correctly', () => {
		cy.mount(MyComponent, {
			props: {
				title: 'Test Title'
			}
		});
		cy.contains('Test Title').should('be.visible');
	});
});
```

### Testing Props

```javascript
it('should accept and display props', () => {
	cy.mount(CwBadge, {
		props: {
			label: 'Test Badge',
			variant: 'success',
			size: 'lg'
		}
	});
	cy.contains('Test Badge').should('be.visible');
	cy.get('span').should('have.class', 'tw-bg-green-100');
});
```

### Testing Slots

```javascript
it('should render slot content', () => {
	cy.mount(MyComponent, {
		slots: {
			default: '<span data-testid="custom-content">Custom Content</span>'
		}
	});
	cy.getByTestId('custom-content').should('exist');
});
```

### Testing Events

```javascript
it('should emit events on click', () => {
	const onClickSpy = cy.spy().as('clickSpy');

	cy.mount(MyButton, {
		props: {
			onClick: onClickSpy
		}
	});

	cy.get('button').click();
	cy.get('@clickSpy').should('have.been.calledOnce');
});
```

### Testing with Vuex/Pinia Store

```javascript
import { createStore } from 'vuex';

it('should work with Vuex store', () => {
	const store = createStore({
		state: {
			user: { name: 'John' }
		}
	});

	cy.mount(MyComponent, {
		global: {
			plugins: [store]
		}
	});

	cy.contains('John').should('be.visible');
});
```

### Testing with Vue Router

```javascript
import { createRouter, createMemoryHistory } from 'vue-router';

it('should navigate correctly', () => {
	const router = createRouter({
		history: createMemoryHistory(),
		routes: [
			{ path: '/', component: Home },
			{ path: '/about', component: About }
		]
	});

	cy.mount(Navigation, {
		global: {
			plugins: [router]
		}
	});

	cy.contains('About').click();
	cy.url().should('include', '/about');
});
```

## Available Custom Commands

The setup includes custom Cypress commands:

```javascript
// Mount component with props
cy.mountWithProps(Component, { props: { ... } });

// Find elements by test ID
cy.getByTestId('button-submit');

// Find within a subject
cy.get('.container').findByTestId('item-1');
```

## Best Practices

### 1. Use Data Test IDs
Add `data-testid` attributes to your components for reliable selectors:

```vue
<template>
	<button data-testid="submit-button">Submit</button>
</template>
```

```javascript
cy.getByTestId('submit-button').click();
```

### 2. Test User Behavior, Not Implementation
Focus on what users see and do:

```javascript
// Good
cy.contains('Submit').click();
cy.contains('Success!').should('be.visible');

// Avoid
cy.get('.component__internal-class').invoke('someMethod');
```

### 3. Organize Tests with Describe Blocks

```javascript
describe('CwBadge Component', () => {
	describe('Size Variants', () => {
		it('should render small size', () => { ... });
		it('should render medium size', () => { ... });
	});

	describe('Color Variants', () => {
		it('should render success variant', () => { ... });
	});
});
```

### 4. Use BeforeEach for Common Setup

```javascript
describe('MyComponent', () => {
	beforeEach(() => {
		cy.mount(MyComponent, {
			props: { commonProp: 'value' }
		});
	});

	it('test 1', () => { ... });
	it('test 2', () => { ... });
});
```

### 5. Test Accessibility

```javascript
it('should be accessible', () => {
	cy.mount(MyComponent);
	cy.get('button').should('have.attr', 'aria-label');
	cy.get('button').should('not.have.attr', 'disabled');
});
```

## Integration with Frappe Bench

### Running Tests in CI/CD

Add to your `.github/workflows` or CI configuration:

```yaml
- name: Run Component Tests
  run: |
    cd apps/ampower_kj
    npx cypress run --component --config-file cypress.component.config.js
```

### Running with Bench Commands

You can create a custom bench command:

```python
# In hooks.py or a custom command file
import click
import subprocess

@click.command()
def test_components():
	"""Run Vue component tests"""
	subprocess.run([
		"npx", "cypress", "run",
		"--component",
		"--config-file", "cypress.component.config.js"
	], cwd="apps/ampower_kj")
```

## Troubleshooting

### Issue: Tailwind classes not applying

Make sure your `component-index.html` includes Tailwind:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

Or link to your compiled CSS file.

### Issue: Module not found errors

Check your `viteConfig` aliases in `cypress.component.config.js`:
```javascript
resolve: {
	alias: {
		"@": path.resolve(__dirname, "./ampower_kj/public/js"),
	},
}
```

### Issue: Components not mounting

Ensure you have `cypress/vue` installed:
```bash
npm install --save-dev @cypress/vue
```

## Example Test Coverage

For a component like `CwBadge.vue`, test:

1. ✅ Rendering with default props
2. ✅ All prop variants (size, variant, etc.)
3. ✅ Slot content
4. ✅ Conditional rendering (showDot)
5. ✅ CSS classes application
6. ✅ Accessibility features
7. ✅ Edge cases (empty props, invalid values)

## Resources

- [Cypress Component Testing Docs](https://docs.cypress.io/guides/component-testing/overview)
- [Cypress Vue Guide](https://docs.cypress.io/guides/component-testing/vue/overview)
- [Testing Library Cypress](https://testing-library.com/docs/cypress-testing-library/intro/)
- [Frappe Framework Docs](https://frappeframework.com)

## Next Steps

1. Add component tests for other Vue components in your app
2. Set up code coverage reporting with `@cypress/code-coverage`
3. Add visual regression testing with `cypress-plugin-snapshots`
4. Integrate tests into your CI/CD pipeline
5. Add component tests to your development workflow

Happy Testing! 🧪
