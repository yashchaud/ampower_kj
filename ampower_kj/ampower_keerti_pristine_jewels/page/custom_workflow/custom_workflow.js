/**
 * Custom Workflow Page
 *
 * This page uses Vue 3 with Tailwind CSS for the UI.
 * The Vue components are loaded from the custom_workflow.bundle.js
 */

frappe.pages["custom-workflow"].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Custom Workflow",
		single_column: true,
	});

	// Store reference to page on wrapper for cleanup
	wrapper.page = page;

	// Load Google Fonts
	loadGoogleFonts();

	// Load the Vue bundle and mount the app
	loadVueApp(page);
};

frappe.pages["custom-workflow"].on_page_show = function(wrapper) {
	// If app already exists, no need to remount
	if (wrapper.vue_app) {
		return;
	}

	// If page is ready but app isn't mounted yet, try mounting
	if (wrapper.page) {
		loadVueApp(wrapper.page);
	}
};

frappe.pages["custom-workflow"].on_page_hide = function(/* wrapper */) {
	// Optionally cleanup Vue app when page is hidden
	// Uncomment and use wrapper if you want to destroy the app on hide:
	// if (wrapper.vue_app && ampower_kj?.ui?.destroy_custom_workflow) {
	//     ampower_kj.ui.destroy_custom_workflow(wrapper.vue_app);
	//     wrapper.vue_app = null;
	// }
};

/**
 * Load Google Fonts (Outfit and Material Symbols)
 */
function loadGoogleFonts() {
	// Load Outfit font
	if (!document.getElementById('cw-google-fonts')) {
		const fontLink = document.createElement('link');
		fontLink.id = 'cw-google-fonts';
		fontLink.rel = 'stylesheet';
		fontLink.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap';
		document.head.appendChild(fontLink);
	}

	// Load Material Symbols
	if (!document.getElementById('cw-material-icons')) {
		const iconLink = document.createElement('link');
		iconLink.id = 'cw-material-icons';
		iconLink.rel = 'stylesheet';
		iconLink.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap';
		document.head.appendChild(iconLink);
	}
}

/**
 * Load the Vue bundle and mount the application
 * @param {Object} page - The Frappe page object
 */
async function loadVueApp(page) {
	const $parent = $(page.main);
	$parent.empty();

	// Show loading indicator
	$parent.html(`
		<div class="tw-flex tw-items-center tw-justify-center tw-py-12">
			<div class="tw-flex tw-flex-col tw-items-center tw-gap-3">
				<span class="material-symbols-outlined tw-text-4xl tw-text-primary-600 tw-animate-spin">
					progress_activity
				</span>
				<p class="tw-text-sm tw-text-slate-500">Loading workflow...</p>
			</div>
		</div>
	`);

	try {
		// Load the Vue bundle and Tailwind CSS
		// frappe.require returns a Promise and loads the bundles
		await frappe.require([
			'custom_workflow.bundle.js',
			'tailwind.bundle.css'
		]);

		// Clear loading and mount Vue app
		$parent.empty();

		// Mount the Vue application
		if (ampower_kj?.ui?.setup_custom_workflow) {
			const app = ampower_kj.ui.setup_custom_workflow($parent);
			// Store reference for cleanup
			page.wrapper.vue_app = app;
		} else {
			throw new Error('Vue bundle not loaded correctly');
		}
	} catch (error) {
		console.error('Failed to load Custom Workflow:', error);

		// Show error message
		$parent.html(`
			<div class="tw-flex tw-items-center tw-justify-center tw-py-12">
				<div class="tw-flex tw-flex-col tw-items-center tw-gap-3 tw-text-center">
					<span class="material-symbols-outlined tw-text-4xl tw-text-red-500">
						error
					</span>
					<p class="tw-text-sm tw-text-slate-700 tw-font-medium">Failed to load workflow</p>
					<p class="tw-text-xs tw-text-slate-500">${error.message}</p>
					<button
						class="tw-mt-2 tw-px-4 tw-py-2 tw-text-sm tw-font-medium tw-text-white tw-bg-primary-600 tw-rounded-lg hover:tw-bg-primary-700"
						onclick="location.reload()"
					>
						Retry
					</button>
				</div>
			</div>
		`);
	}
}
