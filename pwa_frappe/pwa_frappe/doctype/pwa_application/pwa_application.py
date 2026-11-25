import io
import re
from pathlib import Path
from urllib.parse import unquote

import frappe
from frappe import _
from frappe.model.document import Document
from PIL import Image

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
TARGET = re.compile(r"/[a-z0-9][a-z0-9/%_-]*", re.IGNORECASE)
PUBLIC_ICON = re.compile(r"/(?:files|assets/[a-z0-9_]+)/(?:[a-z0-9_-]+/)*[a-z0-9_.-]+\.png", re.I)


class PWAApplication(Document):
	def validate(self):
		if len(self.app_code) > 60 or not SLUG.fullmatch(self.app_code):
			frappe.throw(_("Application code must contain lowercase letters, numbers and single hyphens."))
		if previous := self.get_doc_before_save():
			if previous.app_code != self.app_code:
				frappe.throw(_("Application code is permanent because it identifies installed copies."))
		if self.target_app not in frappe.get_installed_apps():
			frappe.throw(_("Select an application installed on this site."))
		if self.enabled and not any(
			entry.get("name") == self.target_app
			and (entry.get("has_permission") or entry.get("route") == self.entry_route)
			for entry in frappe.get_hooks("add_to_apps_screen", app_name=self.target_app)
		):
			frappe.throw(_("The target application must supply its native Apps access check."))
		route = unquote(self.entry_route)
		if (not TARGET.fullmatch(self.entry_route) or not TARGET.fullmatch(route) or "//" in route
			or route.startswith(("/api", "/assets", "/files", "/private", "/mis-apps", "/login", "/logout"))):
			frappe.throw(_("Enter a same-site application page path without a query or fragment."))
		for color in (self.theme_color, self.background_color):
			if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
				frappe.throw(_("Use a six-digit hexadecimal color."))
		for url, size in ((self.icon_192, 192), (self.icon_512, 512), (self.maskable_512, 512)):
			if url:
				validate_icon(url, size)


def validate_icon(url, size):
	if not PUBLIC_ICON.fullmatch(url):
		frappe.throw(_("Use a public PNG in /files/ or /assets/."))
	if url.startswith("/files/"):
		file_name = frappe.db.get_value("File", {"file_url": url, "is_private": 0})
		if not file_name:
			frappe.throw(_("The selected icon must be a public Frappe file."))
		content = frappe.get_doc("File", file_name).get_content()
		source = io.BytesIO(content)
	else:
		_, _, app, *parts = url.split("/")
		root = Path(frappe.get_app_path(app, "public")).resolve()
		source = root.joinpath(*parts).resolve()
		if not source.is_relative_to(root) or not source.is_file():
			frappe.throw(_("The selected public icon does not exist."))
	try:
		with Image.open(source) as image:
			valid = image.format == "PNG" and image.size == (size, size)
			image.verify()
	except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
		valid = False
	if not valid:
		frappe.throw(_("Select a valid PNG measuring {0} × {0} pixels.").format(size))
