"""
Installation hooks for AmPower KJ app
Handles automatic build and setup after app installation
"""

import subprocess
import os
import frappe


def after_install():
	"""
	Called after the app is installed to a site via `bench --site <site> install-app ampower_kj`
	This ensures the Vue components and Tailwind CSS are built automatically
	"""
	try:
		print("\n" + "="*60)
		print("🚀 AmPower KJ: Running post-install build...")
		print("="*60 + "\n")

		# Get the app path
		app_path = frappe.get_app_path("ampower_kj")

		# Step 1: Install npm dependencies (if needed)
		package_json = os.path.join(app_path, "..", "package.json")
		if os.path.exists(package_json):
			print("📦 Installing npm dependencies...")
			try:
				subprocess.run(
					["npm", "install"],
					cwd=os.path.dirname(package_json),
					check=True,
					capture_output=True,
					text=True
				)
				print("✅ npm install completed")
			except subprocess.CalledProcessError as e:
				print(f"⚠️  npm install failed: {e.stderr}")
				print("   You may need to run 'npm install' manually in apps/ampower_kj/")

		# Step 2: Build Tailwind CSS
		print("\n🎨 Building Tailwind CSS...")
		try:
			subprocess.run(
				["npm", "run", "build:tailwind"],
				cwd=os.path.dirname(package_json),
				check=True,
				capture_output=True,
				text=True
			)
			print("✅ Tailwind CSS built successfully")
		except subprocess.CalledProcessError as e:
			print(f"⚠️  Tailwind build failed: {e.stderr}")
			print("   You may need to run 'npm run build:tailwind' manually")

		# Step 3: Build Frappe assets (Vue components)
		print("\n⚡ Building Vue components...")
		print("   (This will be handled by bench build automatically)")

		print("\n" + "="*60)
		print("✨ AmPower KJ installation complete!")
		print("   Next: Run 'bench build --app ampower_kj' to compile Vue assets")
		print("="*60 + "\n")

	except Exception as e:
		frappe.log_error(f"AmPower KJ after_install error: {str(e)}")
		print(f"\n⚠️  Post-install build encountered an error: {str(e)}")
		print("   The app is installed but you may need to run builds manually:")
		print("   1. cd apps/ampower_kj && npm install")
		print("   2. npm run build:tailwind")
		print("   3. bench build --app ampower_kj")
