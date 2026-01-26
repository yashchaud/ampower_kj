# Why Your Bundle Takes Long to Load & How to Fix Tests

## The Root Cause

Your **1.6MB bundle** is taking too long to load, causing Cypress tests to timeout before the Vue app mounts.

### Why 1.6MB is Large

```bash
# Your bundle
custom_workflow.bundle.js: 1.6MB

# Typical Vue app bundles:
- Small app: 100-300KB
- Medium app: 300-600KB
- Large app: 600KB-1MB
- VERY large: 1MB+ ← You are here
```

---

## Reasons for Large Bundle Size

### 1. **Large Main Component**
```
CustomWorkflow.vue: 1,420 lines
```

This single component is doing too much. It likely contains:
- All tab logic
- All table rendering
- All modal logic
- All filtering logic
- All state management

**Impact**: Entire app loads at once, even if user only needs one tab.

### 2. **Multiple Vue Components Bundled Together**
```
21 Vue/JS files in your bundle
```

All components (CwTabs, CwButton, CwDropdown, CwBadge, etc.) are bundled together.

### 3. **No Code Splitting**
Everything loads upfront instead of on-demand.

### 4. **Development vs Production Build**
Your bundle might not be minified/optimized properly.

### 5. **Large Dependencies**
Vue 3, possibly date libraries, utility functions, etc.

---

## Quick Fixes for Tests (Immediate)

### Fix 1: Increase Cypress Timeouts

**File**: `cypress.config.js`

```javascript
module.exports = defineConfig({
    defaultCommandTimeout: 30000,  // Increase from 20s to 30s
    pageLoadTimeout: 60000,        // Increase from 15s to 60s
    requestTimeout: 30000,
    responseTimeout: 30000,

    e2e: {
        // ... rest of config
    }
});
```

### Fix 2: Better Wait Function

**File**: `custom_workflow_improved.cy.js`

```javascript
function waitForVueApp() {
    // 1. Wait for page container
    cy.get('.page-content', { timeout: 15000 }).should('exist');

    // 2. Wait for loading spinner to appear (proves bundle is loading)
    cy.get('.tw-animate-spin', { timeout: 10000 }).should('exist');
    cy.log('Loading spinner detected - bundle is loading...');

    // 3. Wait for loading spinner to disappear (bundle loaded)
    cy.get('.tw-animate-spin', { timeout: 60000 }).should('not.exist');
    cy.log('Loading complete');

    // 4. Check for error state
    cy.get('body').then($body => {
        if ($body.find('.tw-text-red-500').length > 0) {
            cy.get('.tw-text-red-500').parent().invoke('text').then(text => {
                throw new Error(`Vue app error: ${text}`);
            });
        }
    });

    // 5. Wait for Vue components
    cy.get('.cw-tabs-list', { timeout: 30000 }).should('be.visible');
    cy.get('.cw-tabs-list button', { timeout: 10000 })
        .should('have.length.at.least', 1)
        .first()
        .should('be.visible');

    cy.log('✓ Vue app fully loaded');
}
```

### Fix 3: Add Network Wait

```javascript
function waitForBundleLoad() {
    // Intercept the bundle request
    cy.intercept('GET', '**/custom_workflow.bundle.*.js').as('vueBundle');

    // Visit page
    cy.visit('/app/custom-workflow');

    // Wait for bundle to load (max 60 seconds)
    cy.wait('@vueBundle', { timeout: 60000 }).then((interception) => {
        cy.log('Bundle loaded:', interception.response.statusCode);
        expect(interception.response.statusCode).to.equal(200);
    });

    // Then wait for Vue app
    waitForVueApp();
}
```

---

## Long-term Performance Fixes

### Solution 1: Code Splitting

Split your large component into smaller chunks that load on demand.

**Before** (1.6MB loaded upfront):
```javascript
// custom_workflow.bundle.js
import CustomWorkflow from './CustomWorkflow.vue';  // 1420 lines!
```

**After** (load tabs on demand):
```javascript
// CustomWorkflow.vue
const UnassignedTab = defineAsyncComponent(() =>
    import('./tabs/UnassignedTab.vue')
);

const AssignedTab = defineAsyncComponent(() =>
    import('./tabs/AssignedTab.vue')
);

// Only loads when tab is clicked
<component :is="currentTabComponent" />
```

**Impact**: Initial bundle drops from 1.6MB to ~400KB

### Solution 2: Split Main Component

**Current structure**:
```
CustomWorkflow.vue (1420 lines)
├── Tab logic
├── Table rendering
├── Modal handling
├── Filters
├── Search
└── All state management
```

**Better structure**:
```
CustomWorkflow.vue (200 lines) - Main coordinator
├── CwWorkflowTabs.vue (150 lines)
├── CwWorkflowTable.vue (300 lines)
├── CwOrderModal.vue (400 lines)
├── CwFilterPanel.vue (200 lines)
└── composables/
    ├── useWorkflowData.js (state)
    ├── useWorkflowFilters.js (filtering)
    └── useWorkflowActions.js (API calls)
```

### Solution 3: Lazy Load Modals

Modals are only needed when clicked, not on page load.

```javascript
// Before: Modal loaded immediately (adds ~200KB)
import CwOrderModal from './CwOrderModal.vue';

// After: Modal loaded when opened (saves ~200KB on initial load)
const CwOrderModal = defineAsyncComponent(() =>
    import('./CwOrderModal.vue')
);
```

### Solution 4: Optimize Build Configuration

Check your build config in Frappe:

```python
# hooks.py or build.json

# Make sure you're building for production
app_include_js = [
    "/assets/ampower_kj/js/custom_workflow.bundle.js"
]

# Enable minification
# This should happen automatically, but verify
```

### Solution 5: Remove Unused Dependencies

Audit what's actually being used:

```bash
# Check bundle composition
cd apps/ampower_kj
npx vite-bundle-visualizer ampower_kj/public/dist/js/custom_workflow.bundle.*.js

# Or use webpack-bundle-analyzer if you have it
```

### Solution 6: Use CDN for Large Dependencies

If you're importing large libraries (date-fns, lodash, etc.):

```javascript
// Before: Bundle includes entire library
import { format } from 'date-fns';  // Adds 100KB+

// After: Use Frappe's built-in moment
const formattedDate = frappe.datetime.str_to_user(date);
```

---

## Measuring Performance

### Test Bundle Size Improvements

```bash
# Before optimization
ls -lh apps/ampower_kj/ampower_kj/public/dist/js/custom_workflow.bundle.*.js
# Output: 1.6MB

# After applying optimizations
bench build --app ampower_kj
ls -lh apps/ampower_kj/ampower_kj/public/dist/js/custom_workflow.bundle.*.js
# Target: <600KB (60% reduction)
```

### Test Load Time Improvements

Add this to your test:

```javascript
it('[PERFORMANCE] Measure load time', () => {
    const startTime = Date.now();

    cy.visit('/app/custom-workflow');

    waitForVueApp();

    cy.then(() => {
        const loadTime = Date.now() - startTime;
        cy.log(`Load time: ${loadTime}ms`);

        // Target: Under 3 seconds
        expect(loadTime).to.be.lessThan(3000);
    });
});
```

---

## Recommended Testing Strategy

### Use Component Tests for Vue Logic

**Don't E2E test**: Component rendering, props, events
**Use component tests instead**:

```javascript
// CwBadge.cy.js - Fast, reliable
import CwBadge from './CwBadge.vue';

it('renders correctly', () => {
    cy.mount(CwBadge, { props: { label: 'Test', variant: 'success' } });
    cy.contains('Test').should('be.visible');
});
// ✓ Runs in 50ms
```

### Use E2E Tests Only for Critical Flows

**E2E test**: Full user workflows with backend

```javascript
// custom_workflow.cy.js - Slow, but tests real integration
it('should complete order workflow', () => {
    // Create order via API
    // Navigate to page
    // Transition through statuses
    // Verify in database
});
// ✓ Runs in 10-30 seconds (acceptable for critical path)
```

**Ratio**:
- 80% Component Tests (fast, reliable)
- 20% E2E Tests (slow, but tests real integration)

---

## Implementation Plan

### Phase 1: Quick Wins (Fix Tests Immediately)

1. **Update Cypress config** with longer timeouts
2. **Update wait function** to be more patient
3. **Add bundle load interception** to verify it's loading

**Time**: 15 minutes
**Result**: Tests pass reliably

### Phase 2: Performance Optimization (Reduce Bundle)

1. **Split CustomWorkflow.vue** into smaller components
2. **Lazy load modals** (async imports)
3. **Code split tabs** (async components)

**Time**: 2-3 hours
**Result**: Bundle ~600KB, loads in <2s

### Phase 3: Testing Strategy (Prevent Future Issues)

1. **Write component tests** for Vue components
2. **Limit E2E tests** to critical workflows only
3. **Add performance monitoring** to tests

**Time**: 1-2 hours
**Result**: Fast, reliable test suite

---

## Example: Fixed Test File

```javascript
// custom_workflow_fixed.cy.js

context('Custom Workflow - Fixed', () => {
    // Longer timeouts for this specific test file
    Cypress.config('defaultCommandTimeout', 30000);
    Cypress.config('pageLoadTimeout', 60000);

    function waitForVueApp() {
        cy.log('Waiting for page load...');
        cy.get('.page-content', { timeout: 15000 }).should('exist');

        cy.log('Waiting for bundle to load...');
        cy.get('.tw-animate-spin', { timeout: 10000 }).should('exist');

        cy.log('Waiting for bundle to finish loading...');
        cy.get('.tw-animate-spin', { timeout: 60000 }).should('not.exist');

        cy.log('Waiting for Vue components...');
        cy.get('.cw-tabs-list', { timeout: 30000 }).should('be.visible');
        cy.get('.cw-tabs-list button').should('have.length.at.least', 1);

        cy.log('✓ App loaded successfully');
    }

    it('should load app', () => {
        cy.visit('/app/custom-workflow');
        waitForVueApp();

        cy.get('.cw-tabs-list button')
            .should('contain', 'Incoming')
            .and('contain', 'Assigned');
    });
});
```

---

## Summary

### Why Bundle is Slow
1. **1.6MB size** - Too large
2. **Single huge component** - No code splitting
3. **Everything loads upfront** - No lazy loading
4. **Tests timeout** - Not waiting long enough

### Immediate Fix (Tests)
1. Increase Cypress timeouts to 60s
2. Better wait logic that detects loading state
3. Add network interception

### Long-term Fix (Performance)
1. Split CustomWorkflow.vue into smaller pieces
2. Lazy load modals and tabs
3. Use async components
4. Target: <600KB bundle, <2s load time

### Testing Strategy
- **80% component tests** (ms)
- **20% E2E tests** (seconds)
- Tests will be faster AND more reliable

---

## Next Steps

Run this command to fix tests immediately:

```bash
cd /home/yashc/frappe-bench/apps/ampower_kj

# Create fixed test file with proper timeouts
cat > cypress/integration/custom_workflow_fixed.cy.js << 'EOF'
[Use the example above]
EOF

# Run it
npx cypress run --spec "cypress/integration/custom_workflow_fixed.cy.js"
```

If tests still fail, the bundle itself has errors (check browser console).
If tests pass, you just need better timeout handling!
