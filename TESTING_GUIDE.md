# Comprehensive Testing Guide for Frappe Vue Apps

## Table of Contents
1. [Component Testing vs E2E Testing](#component-testing-vs-e2e-testing)
2. [Your Test Failures - Root Cause Analysis](#your-test-failures---root-cause-analysis)
3. [Component Testing Setup](#component-testing-setup)
4. [E2E Testing Best Practices](#e2e-testing-best-practices)
5. [Debugging Failed Tests](#debugging-failed-tests)

---

## Component Testing vs E2E Testing

### Component Testing
- **What**: Tests individual Vue components in isolation
- **When**: Testing component logic, props, events, UI rendering
- **Fast**: Runs in milliseconds
- **Reliable**: No backend dependencies
- **Tools**: Cypress Component Testing, Vue Test Utils

### E2E (End-to-End) Testing
- **What**: Tests the entire application flow including Frappe backend
- **When**: Testing user workflows, API integration, full page interactions
- **Slow**: Runs in seconds/minutes
- **Fragile**: Depends on backend, database, network
- **Tools**: Cypress E2E

**Your failing tests are E2E tests** - they're testing the full Custom Workflow page with Frappe integration.

---

## Your Test Failures - Root Cause Analysis

### What's Happening

Your E2E tests are failing with:
```
Expected to find element: `.cw-tabs-list button`, but never found it.
```

### Why It's Failing

#### 1. **Vue App Not Mounting**
The most common cause. Possible reasons:

```javascript
// The page tries to load Vue bundle:
await frappe.require([
    'custom_workflow.bundle.js',  // ← This might be failing
    'tailwind.bundle.css'
]);
```

**Diagnostic Steps:**
- Check if `custom_workflow.bundle.js` exists in build folder
- Check browser console for JavaScript errors
- Verify `ampower_kj.ui.setup_custom_workflow` is defined

#### 2. **Bundle Not Built**
```bash
# Check if bundle exists
ls -la apps/ampower_kj/ampower_kj/public/dist/js/custom_workflow.bundle.*.js

# If missing, build it
cd apps/ampower_kj
bench build --app ampower_kj
```

#### 3. **Async Loading Race Condition**
Vue app takes time to mount, but tests don't wait long enough.

**Bad Test:**
```javascript
cy.visit('/app/custom-workflow');
cy.get('.cw-tabs-list button').click(); // ❌ Fails - Vue not mounted yet
```

**Good Test:**
```javascript
cy.visit('/app/custom-workflow');

// Wait for loading spinner to disappear
cy.get('.tw-animate-spin', { timeout: 15000 }).should('not.exist');

// Wait for Vue component
cy.get('.cw-tabs-list', { timeout: 30000 }).should('be.visible');
cy.get('.cw-tabs-list button').click(); // ✅ Works
```

#### 4. **Frappe Page Lifecycle Issues**
```javascript
// custom_workflow.js
frappe.pages["custom-workflow"].on_page_load = function(wrapper) {
    loadVueApp(page);  // ← Async function
};
```

If `loadVueApp()` fails silently, tests will timeout.

### How to Diagnose

#### Step 1: Check if bundle is built
```bash
cd apps/ampower_kj
ls -la ampower_kj/public/dist/js/
# Should see: custom_workflow.bundle.HASH.js
```

#### Step 2: Run diagnostic test
```bash
cd apps/ampower_kj
npx cypress open

# Run: custom_workflow_improved.cy.js
# Look at the [DIAGNOSTIC] test
```

#### Step 3: Check browser console
When test runs, open browser DevTools:
- Network tab: Check if bundle loads (200 status)
- Console tab: Look for JavaScript errors
- Vue DevTools: Check if Vue app is mounted

#### Step 4: Add debug logging
```javascript
// In custom_workflow.js, add:
async function loadVueApp(page) {
    console.log('1. loadVueApp called');

    try {
        await frappe.require([...]);
        console.log('2. Bundles loaded');

        const app = ampower_kj.ui.setup_custom_workflow($parent);
        console.log('3. Vue app mounted:', app);
    } catch (error) {
        console.error('4. FAILED:', error);
    }
}
```

---

## Component Testing Setup

Component tests are **much more reliable** than E2E tests. Use them for Vue components.

### Example: Testing CwBadge Component

**File**: `CwBadge.cy.js`

```javascript
import CwBadge from './CwBadge.vue';

describe('CwBadge', () => {
    it('renders with props', () => {
        cy.mount(CwBadge, {
            props: {
                label: 'Test',
                variant: 'success',
                size: 'lg'
            }
        });

        cy.contains('Test').should('be.visible');
        cy.get('span').should('have.class', 'tw-bg-green-100');
    });

    it('shows dot when enabled', () => {
        cy.mount(CwBadge, {
            props: {
                label: 'Status',
                showDot: true,
                variant: 'warning'
            }
        });

        cy.get('span > span').should('exist');
        cy.get('span > span').should('have.class', 'tw-bg-amber-500');
    });
});
```

### Running Component Tests

```bash
cd apps/ampower_kj

# Open Cypress UI
npm run test:component:open

# Run headless
npm run test:component
```

**Benefits:**
- ✅ Fast (runs in ms)
- ✅ Reliable (no backend needed)
- ✅ Easy to debug
- ✅ Tests component logic directly

---

## E2E Testing Best Practices

### 1. Robust Waiting Strategy

```javascript
function waitForVueApp() {
    // 1. Check for errors first
    cy.get('body').then($body => {
        if ($body.find('.tw-text-red-500').length > 0) {
            cy.get('.tw-text-red-500').parent().invoke('text').then(text => {
                throw new Error(`Vue failed to load: ${text}`);
            });
        }
    });

    // 2. Wait for loading to complete
    cy.get('.tw-animate-spin', { timeout: 20000 }).should('not.exist');

    // 3. Wait for Vue components
    cy.get('.cw-tabs-list', { timeout: 30000 }).should('be.visible');
    cy.get('.cw-tabs-list button').should('have.length.at.least', 1);
}
```

### 2. Handle Teleported Elements

Vue Teleport moves elements outside component tree:

```vue
<!-- In component -->
<Teleport to="body">
    <div class="dropdown-menu">...</div>
</Teleport>
```

**Test it:**
```javascript
// ❌ Won't work - teleported outside
cy.get('.dropdown-container').find('.dropdown-menu');

// ✅ Correct - search from body
cy.get('body').find('.dropdown-menu');
```

### 3. Handle Async State Changes

```javascript
it('should transition order status', () => {
    // Click button that triggers async update
    cy.get('button').contains('Next Stage').click();

    // ❌ Bad - checks immediately
    cy.get('.cw-badge').should('contain', 'Internal QA');

    // ✅ Good - waits for backend update
    cy.get('.cw-badge', { timeout: 10000 })
        .should('not.contain', 'Incoming')
        .should('contain', 'Internal QA');
});
```

### 4. Verify Before Asserting

```javascript
it('should display orders', () => {
    waitForVueApp();

    // ❌ Bad - assumes data exists
    cy.get('tbody tr').first().click();

    // ✅ Good - checks first
    cy.get('tbody').then($tbody => {
        if ($tbody.find('tr').length === 0) {
            cy.log('No data in table');
            cy.task('log', 'WARNING: No test data found');
        }
    });

    cy.get('tbody tr').should('have.length.at.least', 1);
    cy.get('tbody tr').first().click();
});
```

### 5. Descriptive Test Names

```javascript
// ❌ Bad
it('test 1', () => { ... });

// ✅ Good
it('should transition order from Incoming to Internal QA when Next Stage clicked', () => { ... });
```

### 6. Independent Tests

```javascript
// ❌ Bad - tests depend on each other
it('create order', () => { /* creates order */ });
it('update order', () => { /* assumes order exists */ });

// ✅ Good - each test is independent
it('should update order status', () => {
    // Create test data in this test
    cy.insert_doc('Order Ledger', { ... }).then(doc => {
        // Test update on this specific doc
        cy.visit(`/app/custom-workflow`);
        // ... test logic
    });
});
```

---

## Debugging Failed Tests

### Technique 1: Screenshots and Videos

Cypress automatically captures screenshots on failure:
```bash
# Check screenshots
ls -la cypress/screenshots/

# Enable video recording
# cypress.config.js:
video: true,
videosFolder: 'cypress/videos/'
```

### Technique 2: Pause and Debug

```javascript
it('debug test', () => {
    cy.visit('/app/custom-workflow');
    cy.pause(); // ← Pauses test, you can inspect in browser
    cy.get('.cw-tabs-list button').click();
});
```

### Technique 3: Add Logging

```javascript
it('should load tabs', () => {
    cy.visit('/app/custom-workflow');

    // Log page state
    cy.get('body').then($body => {
        cy.log('Page HTML length:', $body.html().length);
        cy.log('Has tabs:', $body.find('.cw-tabs-list').length > 0);
        cy.log('Has table:', $body.find('table').length > 0);
    });

    // Log window objects
    cy.window().then(win => {
        cy.log('ampower_kj:', Object.keys(win.ampower_kj || {}));
        cy.log('frappe.boot:', !!win.frappe.boot);
    });

    cy.get('.cw-tabs-list').should('exist');
});
```

### Technique 4: Test in Isolation

If all tests fail:
```javascript
// Run only one test
it.only('should load page', () => {
    // This test runs alone
});

// Skip other tests
it.skip('other test', () => {
    // This test is skipped
});
```

### Technique 5: Check Test Environment

```bash
# Is Frappe site running?
bench start

# In another terminal, check if site is accessible
curl http://localhost:8000

# Check Cypress config
cat cypress.config.js
# baseUrl should match your site
```

---

## Common Frappe + Vue Testing Patterns

### Pattern 1: Test After Creating Data

```javascript
it('should display newly created order', () => {
    const orderName = `ORD-${Date.now()}`;

    // Create via Frappe API
    cy.insert_doc('Order Ledger', {
        name: orderName,
        qty: 5,
        order_status: 'Incoming'
    }, true).then(doc => {
        // Visit page
        cy.visit('/app/custom-workflow');
        waitForVueApp();

        // Verify it appears
        cy.get('tbody').contains(doc.name).should('be.visible');
    });
});
```

### Pattern 2: Test Modal Interactions

```javascript
it('should open and close order modal', () => {
    waitForVueApp();

    // Click row to open modal
    cy.get('tbody tr').first().click();

    // Verify modal opened
    cy.get('[role="dialog"]').should('be.visible');

    // Interact with modal
    cy.get('[role="dialog"]').within(() => {
        cy.get('input[type="number"]').type('123');
        cy.contains('button', 'Save').click();
    });

    // Verify modal closed
    cy.get('[role="dialog"]').should('not.exist');
});
```

### Pattern 3: Test Filters

```javascript
it('should filter by customer', () => {
    waitForVueApp();

    // Type in filter
    cy.get('input[placeholder="Customer"]').type('Test Customer');
    cy.wait(500); // Debounce

    // Select from dropdown (if any)
    cy.get('[role="listbox"]').contains('Test Customer').click();

    // Verify filtered results
    cy.get('tbody tr').each($row => {
        cy.wrap($row).should('contain', 'Test Customer');
    });
});
```

---

## Fixing Your Specific Tests

### Problem: Tests timeout waiting for `.cw-tabs-list`

**Root Cause**: Vue app not mounting

**Solution:**

1. **Check if bundle is built:**
```bash
cd apps/ampower_kj
bench build --app ampower_kj
```

2. **Add better wait logic:**
```javascript
function waitForVueApp() {
    // Wait for loading to finish
    cy.get('.page-content').should('exist');

    cy.get('body').then($body => {
        // Check for loading spinner
        if ($body.find('.tw-animate-spin').length > 0) {
            cy.get('.tw-animate-spin', { timeout: 20000 })
                .should('not.exist');
        }

        // Check for error
        if ($body.find('.tw-text-red-500').length > 0) {
            cy.get('.tw-text-red-500').parent().invoke('text')
                .then(text => {
                    throw new Error(`Vue app failed: ${text}`);
                });
        }
    });

    // Wait for Vue components
    cy.get('.cw-tabs-list', { timeout: 30000 })
        .should('be.visible');
}
```

3. **Run improved test:**
```bash
cd apps/ampower_kj
npx cypress open
# Run: custom_workflow_improved.cy.js
```

---

## Test File Structure Recommendation

```
apps/ampower_kj/
├── cypress/
│   ├── integration/           # E2E tests
│   │   ├── custom_workflow.cy.js
│   │   └── order_flow.cy.js
│   ├── support/
│   │   ├── commands.js       # Custom Cypress commands
│   │   └── e2e.js
│   └── fixtures/
│       └── test_data.json
├── ampower_kj/public/js/vue_components/
│   ├── CwBadge.vue
│   ├── CwBadge.cy.js         # ← Component test
│   ├── CwDropdown.vue
│   └── CwDropdown.cy.js      # ← Component test
└── cypress.config.js          # E2E config
└── cypress.component.config.js # Component config
```

---

## Quick Reference

### Run Component Tests (Fast, Reliable)
```bash
npm run test:component         # Headless
npm run test:component:open    # UI mode
```

### Run E2E Tests (Slow, Full Integration)
```bash
npx cypress run                           # All tests
npx cypress run --spec "cypress/integration/custom_workflow.cy.js"  # One file
npx cypress open                          # UI mode
```

### Debug
```bash
# Open Cypress UI and watch test execution
npx cypress open

# Enable debug mode
DEBUG=cypress:* npx cypress run
```

---

## Summary

**Your Issue:** E2E tests failing because Vue app not mounting in time

**Root Causes:**
1. Bundle not built/loaded
2. Inadequate wait logic
3. No error handling in tests

**Solutions:**
1. Build bundles: `bench build --app ampower_kj`
2. Use improved wait function with error checking
3. Add diagnostic logging
4. Use component tests for Vue components (more reliable)

**Best Practice:**
- **Component tests**: 80% of your tests (fast, reliable)
- **E2E tests**: 20% of your tests (critical user flows only)

---

## Next Steps

1. ✅ Build your app bundles
2. ✅ Run the improved diagnostic test
3. ✅ Fix any build/bundle errors
4. ✅ Update wait functions in tests
5. ✅ Write component tests for Vue components
6. ✅ Keep E2E tests for critical workflows only
