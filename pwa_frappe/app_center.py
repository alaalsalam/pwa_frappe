"""MIS installation metadata and launch through the existing Frappe session."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode

import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response
from werkzeug.utils import redirect

from pwa_frappe import __version__

CENTER = "/mis-apps"
DOCTYPE = "PWA Application"
APP_PATH = re.compile(r"/?mis-apps/([a-z0-9]+(?:-[a-z0-9]+)*)(?:/(manifest\.webmanifest|open))?")
FIELDS = (
	"name", "name_ar", "name_en", "short_name", "description", "description_en", "target_app",
	"entry_route", "theme_color", "background_color", "icon_192", "icon_512", "maskable_512",
	"version",
)


def can_manage():
	return "System Manager" in frappe.get_roles()


def extend_bootinfo(bootinfo):
	bootinfo.pwa_configure_desk = bool(frappe.db.get_single_value("Web App Manifest", "configure_desk"))


def public_apps():
	installed = set(frappe.get_installed_apps())
	return [
		app for app in frappe.get_all(DOCTYPE, filters={"enabled": 1}, fields=FIELDS, order_by="name")
		if app.target_app in installed
	]


def install_path(app):
	return f"{CENTER}/{app.name}"


def manifest(app):
	path = install_path(app)
	icons = [
		{"src": app.icon_192, "sizes": "192x192", "type": "image/png", "purpose": "any"},
		{"src": app.icon_512, "sizes": "512x512", "type": "image/png", "purpose": "any"},
	]
	if app.maskable_512:
		icons.append({"src": app.maskable_512, "sizes": "512x512", "type": "image/png", "purpose": "maskable"})
	return {
		"id": path,
		"start_url": path + "?launch=1",
		"scope": "/",
		"name": app.name_ar,
		"short_name": app.short_name,
		"description": app.description,
		"lang": "ar",
		"dir": "rtl",
		"display": "standalone",
		"theme_color": app.theme_color,
		"background_color": app.background_color,
		"icons": icons,
		"version": app.version,
	}


def may_open(app):
	# Discoverability alone is insufficient. Require the app's native access hook
	# where it supplies one. Desk and target pages still check their own permissions.
	entries = frappe.get_hooks("add_to_apps_screen", app_name=app.target_app)
	entry = next((item for item in entries if item.get("name") == app.target_app), None)
	if not entry:
		return False
	if check := entry.get("has_permission"):
		return bool(frappe.get_attr(check)())
	from frappe.desk.doctype.dock.dock import get_app_entry_set

	return entry.get("route") == app.entry_route and bool(get_app_entry_set(app.target_app))


class AppCenter(BaseRenderer):
	def can_render(self):
		return self.path in {"mis-apps", "mis-apps/sw.js"} or bool(APP_PATH.fullmatch(self.path))

	def render(self):
		if self.path == "mis-apps/sw.js":
			source = Path(frappe.get_app_path("pwa_frappe", "www", "sw.js")).read_text(encoding="utf-8")
			response = Response(source, mimetype="text/javascript")
		else:
			response = self.render_app()
		response.headers["Cache-Control"] = "no-store"
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["X-Robots-Tag"] = "noindex"
		return response

	def render_app(self):
		apps = public_apps()
		if self.path == "mis-apps":
			return self.page(apps=apps)
		code, action = APP_PATH.fullmatch(self.path).groups()
		app = next((item for item in apps if item.name == code), None)
		if not app:
			return self.page(status=404)
		if action == "manifest.webmanifest":
			return Response(json.dumps(manifest(app), ensure_ascii=False), mimetype="application/manifest+json")
		if action == "open" or frappe.request.args.get("launch") == "1":
			if frappe.session.user == "Guest":
				return redirect("/login?" + urlencode({"redirect-to": install_path(app) + "/open"}))
			if may_open(app):
				return redirect(app.entry_route)
			return self.page(app=app, status=403)
		return self.page(app=app)

	@staticmethod
	def page(app=None, apps=None, status=200):
		body = frappe.render_template("pwa_frappe/templates/app_center.html", {
			"app": app, "apps": apps, "status": status, "center": CENTER,
			"path_for": install_path, "release": __version__,
		})
		return Response(body, status=status, mimetype="text/html")
