frappe.ui.form.on("PWA Application", {
	refresh(frm) {
		if (frm.is_new() || !frm.doc.enabled) return;
		const url = "/mis-apps/" + encodeURIComponent(frm.doc.name);
		const preview = $("<a>", {href: url, target: "_blank", rel: "noopener", text: __("Preview installation")});
		frm.fields_dict.launch_url.$wrapper.find(".pwa-install-preview").empty().append(preview);
	},
});
