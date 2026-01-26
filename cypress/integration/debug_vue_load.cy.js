/**
 * Debug Test - Find Why Vue App Won't Mount
 */

Cypress.config('defaultCommandTimeout', 30000);
Cypress.config('pageLoadTimeout', 60000);

context('Debug Vue App Loading', () => {
    it('should capture console errors and page state', () => {
        const consoleErrors = [];
        const consoleWarnings = [];

        cy.visit('/app/custom-workflow', {
            onBeforeLoad(win) {
                // Capture console errors
                cy.stub(win.console, 'error').callsFake((...args) => {
                    consoleErrors.push(args.join(' '));
                });
                cy.stub(win.console, 'warn').callsFake((...args) => {
                    consoleWarnings.push(args.join(' '));
                });
            }
        });

        cy.window().its('frappe').should('exist');
        cy.get('.page-content', { timeout: 15000 }).should('exist');

        // Wait for bundle to try loading
        cy.wait(10000);

        // Check page HTML
        cy.get('.page-content').then($content => {
            const html = $content.html();
            cy.log('=== PAGE HTML ===');
            cy.log('Content length:', html.length);
            cy.log('Has spinner:', html.includes('tw-animate-spin'));
            cy.log('Has error:', html.includes('tw-text-red-500'));
            cy.log('Has tabs:', html.includes('cw-tabs'));
            cy.log('Has table:', html.includes('table'));

            cy.log('\n=== HTML PREVIEW ===');
            cy.log(html.substring(0, 1000));
        });

        // Check window objects
        cy.window().then(win => {
            cy.log('\n=== WINDOW OBJECTS ===');
            cy.log('frappe exists:', !!win.frappe);
            cy.log('ampower_kj exists:', !!win.ampower_kj);

            if (win.ampower_kj) {
                cy.log('ampower_kj.ui exists:', !!win.ampower_kj.ui);
                if (win.ampower_kj.ui) {
                    cy.log('Available functions:', Object.keys(win.ampower_kj.ui));
                    cy.log('setup_custom_workflow exists:', !!win.ampower_kj.ui.setup_custom_workflow);
                }
            }
        });

        // Log console errors
        cy.then(() => {
            cy.log('\n=== CONSOLE ERRORS ===');
            if (consoleErrors.length > 0) {
                consoleErrors.forEach(err => cy.log('ERROR:', err));
            } else {
                cy.log('No console errors');
            }

            cy.log('\n=== CONSOLE WARNINGS ===');
            if (consoleWarnings.length > 0) {
                consoleWarnings.forEach(warn => cy.log('WARN:', warn));
            } else {
                cy.log('No console warnings');
            }
        });

        // Check network requests
        cy.window().then(win => {
            cy.log('\n=== CHECKING BUNDLE LOAD ===');

            // Try to manually check if bundle loaded
            const scripts = win.document.querySelectorAll('script');
            const bundleScripts = Array.from(scripts).filter(s =>
                s.src && s.src.includes('custom_workflow.bundle')
            );

            cy.log('Custom workflow bundle scripts:', bundleScripts.length);
            bundleScripts.forEach(script => {
                cy.log('Bundle script:', script.src);
            });
        });

        // Check if there's an error message on the page
        cy.get('body').then($body => {
            if ($body.find('.tw-text-red-500').length > 0) {
                cy.log('\n=== ERROR MESSAGE ON PAGE ===');
                cy.get('.tw-text-red-500').parent().invoke('text').then(text => {
                    cy.log('Error:', text);
                });
            }
        });

        // Final check - try to find ANY Vue component markers
        cy.get('body').then($body => {
            cy.log('\n=== SEARCHING FOR VUE COMPONENTS ===');
            const vueMarkers = [
                '.cw-tabs-list',
                '.cw-tabs',
                '[class*="cw-"]',
                '[class*="tw-"]',
                '#custom-workflow-app'
            ];

            vueMarkers.forEach(selector => {
                const found = $body.find(selector).length;
                cy.log(`${selector}: ${found} found`);
            });
        });
    });

    it('should manually try to mount Vue app', () => {
        cy.visit('/app/custom-workflow');
        cy.window().its('frappe').should('exist');
        cy.wait(10000); // Wait for bundles

        cy.window().then(win => {
            cy.log('=== MANUAL MOUNT ATTEMPT ===');

            if (!win.ampower_kj || !win.ampower_kj.ui || !win.ampower_kj.ui.setup_custom_workflow) {
                cy.log('❌ setup_custom_workflow function NOT available');
                cy.log('This means the Vue bundle failed to load or execute');
                return;
            }

            cy.log('✓ setup_custom_workflow function is available');

            // Try to find the mount point
            const pageContent = win.document.querySelector('.page-content');
            if (!pageContent) {
                cy.log('❌ .page-content not found');
                return;
            }

            cy.log('✓ .page-content found');
            cy.log('Content HTML:', pageContent.innerHTML.substring(0, 500));

            // Check if already mounted
            const existingApp = pageContent.querySelector('#custom-workflow-app');
            if (existingApp) {
                cy.log('✓ #custom-workflow-app already exists');
                cy.log('HTML:', existingApp.innerHTML.substring(0, 500));
            } else {
                cy.log('⚠️  #custom-workflow-app does not exist');
                cy.log('The setup function should create this, but it didn\'t');
            }
        });
    });
});
