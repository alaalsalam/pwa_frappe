"""Versioned MIS Development settings. Run from Bench as a site administrator."""
import json
from pathlib import Path

import frappe

from pwa_frappe.app_center import DOCTYPE


def apply():
	if frappe.local.site != "dev.mwe-mis.maward.org":
		frappe.throw("The MIS catalog targets dev.mwe-mis.maward.org.")
	frappe.only_for("System Manager")
	rows = json.loads(Path(__file__).with_name("mis.json").read_text(encoding="utf-8"))
	result = {"created": [], "updated": [], "unchanged": []}
	for row in rows:
		code = row["app_code"]
		base = f"/assets/pwa_frappe/mis/icons/{code}"
		values = {
			"version": "1.0.0", "background_color": "#f2f7f6", "enabled": 1,
			"icon_192": base + "-192.png", "icon_512": base + "-512.png",
			"maskable_512": base + "-maskable.png", **row,
		}
		if not frappe.db.exists(DOCTYPE, code):
			frappe.get_doc({"doctype": DOCTYPE, **values}).insert()
			result["created"].append(code)
			continue
		doc = frappe.get_doc(DOCTYPE, code)
		if any(doc.get(key) != value for key, value in values.items()):
			doc.update(values).save()
			result["updated"].append(code)
		else:
			result["unchanged"].append(code)
	return result
