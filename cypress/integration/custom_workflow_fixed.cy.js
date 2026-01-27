/**
 * Fixed Custom Workflow Tests
 *
 * These tests account for the 1.6MB bundle size and wait appropriately
 * for the Vue app to load completely before running assertions.
 */

// Set longer timeouts for this test suite
Cypress.config('defaultCommandTimeout', 30000);
Cypress.config('pageLoadTimeout', 60000);
Cypress.config('requestTimeout', 30000);

context('Custom Workflow - Fixed with Proper Timeouts', () => {
    const testSuffix = Math.random().toString(36).slice(2, 7);
    const customerName = `Test Customer ${testSuffix}`;
    const karigarName = `Test Karigar ${testSuffix}`;
    const itemName = `Test Item ${testSuffix}`;
    let salesOrderName;
    let orderLedgerName;

    function getToday() {
        return new Date().toISOString().split('T')[0];
    }

    function addDays(days) {
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString().split('T')[0];
    }

    before(() => {
        cy.login();
        cy.visit('/app');
        cy.window().its('frappe').should('exist');

        // Create test data
        cy.create_records({
            doctype: 'Customer',
            customer_name: customerName,
            customer_type: 'Individual',
            customer_group: 'All Customer Groups',
            territory: 'All Territories'
        });

        cy.create_records({
            doctype: 'Item',
            item_code: itemName,
            item_group: 'All Item Groups',
            stock_uom: 'Nos',
            is_sales_item: 1
        });

        cy.create_records({
            doctype: 'Supplier',
            supplier_name: karigarName,
            supplier_group: 'All Supplier Groups',
            supplier_type: 'Individual'
        });

        cy.insert_doc('Sales Order', {
            customer: customerName,
            delivery_date: addDays(7),
            items: [{
                item_code: itemName,
                qty: 10,
                rate: 1000,
                delivery_date: addDays(7)
            }]
        }, true).then(doc => {
            salesOrderName = doc.name;

            cy.insert_doc('Order Ledger', {
                sales_order: salesOrderName,
                item: itemName,
                order_date: getToday(),
                qty: 5,
                order_status: 'Incoming',
                soi_karigar: karigarName
            }, true).then(olDoc => {
                orderLedgerName = olDoc.name;
            });
        });
    });

    /**
     * Navigate to custom workflow page and wait for initial page load
     */
    function navigateToPage() {
        cy.log('=== NAVIGATING TO CUSTOM WORKFLOW ===');

        cy.login();

        // Intercept the bundle request to track loading
        cy.intercept('GET', '**/custom_workflow.bundle.*.js').as('vueBundle');
        cy.intercept('GET', '**/tailwind.bundle.*.css').as('tailwindCss');

        cy.visit('/app/custom-workflow');
        cy.url().should('match', /\/(app|desk)\/custom-workflow/, { timeout: 10000 });

        // Wait for Frappe to be ready
        cy.window().its('frappe').should('exist');
        cy.get('.page-content', { timeout: 15000 }).should('exist');

        cy.log('✓ Page loaded, waiting for bundles...');
    }

    /**
     * Robust wait function for Vue app to fully load
     * Accounts for 1.6MB bundle size - may take 30-60 seconds
     */
    function waitForVueApp() {
        cy.log('=== WAITING FOR VUE APP TO LOAD ===');

        // Step 1: Check if loading spinner appears
        cy.get('body').then($body => {
            if ($body.find('.tw-animate-spin').length > 0) {
                cy.log('⏳ Loading spinner detected - bundle is loading...');
            } else {
                cy.log('⚠️  No loading spinner - checking if already loaded...');
            }
        });

        // Step 2: Wait for loading spinner to disappear (if it exists)
        // Use .then() to check, not .should() to avoid retrying cy.log()
        cy.get('body').then($body => {
            if ($body.find('.tw-animate-spin').length > 0) {
                cy.log('Waiting for bundle to load (up to 60s)...');
                cy.get('.tw-animate-spin', { timeout: 60000 }).should('not.exist');
                cy.log('✓ Loading spinner gone - bundle loaded');
            } else {
                cy.log('✓ No spinner - app may already be loaded');
            }
        });

        // Step 3: Check for error state
        cy.get('body').then($body => {
            if ($body.find('.tw-text-red-500').length > 0) {
                cy.log('❌ ERROR DETECTED');
                cy.get('.tw-text-red-500').parent().invoke('text').then(errorText => {
                    cy.log('Error message:', errorText);
                    throw new Error(`Vue app failed to load: ${errorText}`);
                });
            }
        });

        // Step 4: Wait for Vue components to be rendered
        cy.get('.cw-tabs-list', { timeout: 30000 })
            .should('exist')
            .should('be.visible')
            .then(() => {
                cy.log('✓ Tabs component found');
            });

        // Step 5: Verify tab labels are actually rendered (tabs use <label> not <button>)
        cy.get('.cw-tabs-list label', { timeout: 15000 })
            .should('have.length.at.least', 1)
            .first()
            .should('be.visible')
            .then($labels => {
                cy.log(`✓ Found ${$labels.length} tab labels`);
            });

        // Step 6: Wait a bit more for any final rendering
        cy.wait(1000);

        cy.log('=== ✅ VUE APP FULLY LOADED ===');
    }

    beforeEach(() => {
        navigateToPage();
    });

    it('[DIAGNOSTIC] Check bundle loading and app state', () => {
        // Log initial state
        cy.get('.page-content').then($content => {
            const html = $content.html();
            cy.log('Page content length:', html.length);
            cy.log('Has loading spinner:', html.includes('tw-animate-spin'));
            cy.log('Has Vue content:', html.includes('cw-tabs'));
        });

        // Check window objects
        cy.window().then(win => {
            cy.log('=== Window Objects ===');
            cy.log('frappe available:', !!win.frappe);
            cy.log('ampower_kj available:', !!win.ampower_kj);
            cy.log('ampower_kj.ui available:', !!(win.ampower_kj && win.ampower_kj.ui));
            cy.log('setup_custom_workflow available:',
                !!(win.ampower_kj && win.ampower_kj.ui && win.ampower_kj.ui.setup_custom_workflow));

            if (win.ampower_kj && win.ampower_kj.ui) {
                cy.log('Available functions:', Object.keys(win.ampower_kj.ui));
            }
        });

        // Now wait for Vue app
        waitForVueApp();

        // Final verification
        cy.get('.cw-tabs-list label').should('have.length.at.least', 6);
    });

    it('should load page and render all tabs', () => {
        waitForVueApp();

        const expectedTabs = ['Unassigned', 'Assigned', 'Incoming', 'Internal QA', 'Pending Delivery', 'Delivered'];

        // Verify each tab exists
        expectedTabs.forEach((tabName, index) => {
            cy.get('.cw-tabs-list')
                .contains('label', tabName)
                .should('be.visible')
                .then(() => {
                    cy.log(`✓ Tab ${index + 1}/${expectedTabs.length}: ${tabName}`);
                });
        });

        cy.log('✅ All tabs rendered successfully');
    });

    it('should have functional tables in each tab', () => {
        waitForVueApp();

        const tabs = ['Unassigned', 'Assigned', 'Incoming'];

        tabs.forEach((tabName, index) => {
            cy.log(`Testing tab ${index + 1}/${tabs.length}: ${tabName}`);

            cy.get('.cw-tabs-list label').contains(tabName).click();
            cy.wait(1500); // Wait for tab content to render

            // Verify table exists
            cy.get('table').should('exist');
            cy.get('thead').should('exist');
            cy.get('tbody').should('exist');

            cy.log(`✓ ${tabName} tab has valid table structure`);
        });
    });

    it('should display test order in Incoming tab', () => {
        waitForVueApp();

        cy.log('Navigating to Incoming tab...');
        cy.get('.cw-tabs-list label').contains('Incoming').click();
        cy.wait(2000); // Wait for data to load

        // Verify table has data
        cy.get('tbody').should('exist');

        cy.get('tbody tr').should('have.length.at.least', 1).then($rows => {
            cy.log(`Found ${$rows.length} rows in Incoming tab`);
        });

        // Find our test order - scroll into view if clipped
        cy.get('tbody').contains(orderLedgerName).scrollIntoView().should('be.visible').then(() => {
            cy.log(`✓ Test order ${orderLedgerName} found in table`);
        });
    });

    it('should open order modal when row clicked', () => {
        waitForVueApp();

        cy.get('.cw-tabs-list label').contains('Incoming').click();
        cy.wait(2000);

        // Click on our test order - scroll into view first
        cy.get('tbody').contains(orderLedgerName)
            .scrollIntoView()
            .should('be.visible')
            .parents('tr')
            .first()
            .click();

        // Wait for modal to appear
        cy.get('[role="dialog"]', { timeout: 10000 })
            .should('be.visible')
            .then(() => {
                cy.log('✓ Modal opened successfully');
            });

        // Verify modal contains order details
        cy.get('[role="dialog"]').within(() => {
            cy.contains(orderLedgerName).should('exist');
        });

        // Close modal
        cy.get('body').type('{esc}');
        cy.get('[role="dialog"]').should('not.exist');
    });

    it('[PERFORMANCE] Measure app load time', () => {
        const startTime = Date.now();

        navigateToPage();
        waitForVueApp();

        cy.then(() => {
            const loadTime = Date.now() - startTime;
            const loadTimeSec = (loadTime / 1000).toFixed(2);

            cy.log('=== PERFORMANCE METRICS ===');
            cy.log(`Total load time: ${loadTimeSec}s (${loadTime}ms)`);

            if (loadTime < 5000) {
                cy.log('✅ Excellent: Under 5 seconds');
            } else if (loadTime < 10000) {
                cy.log('⚠️  Fair: 5-10 seconds (consider optimizing bundle)');
            } else if (loadTime < 30000) {
                cy.log('⚠️  Slow: 10-30 seconds (bundle optimization needed)');
            } else {
                cy.log('❌ Very slow: Over 30 seconds (critical - optimize immediately)');
            }

            // Don't fail test, just log performance
            cy.log(`Custom Workflow load time: ${loadTimeSec}s`);
        });
    });
});