frappe.listview_settings["PWA Application"] = {
	get_indicator(doc) {
		return doc.enabled
			? [__("Published"), "green", "enabled,=,1"]
			: [__("Unpublished"), "gray", "enabled,=,0"];
	},
	add_fields: ["enabled", "icon_192"],
};
