frappe.ui.form.on("PWA Application", {
	refresh(frm) {
		if (frm.is_new()) return;
		const url = "/mis-apps/" + encodeURIComponent(frm.doc.name);
		const actions = frm.fields_dict.launch_url.$wrapper.find(".pwa-install-preview").empty();
		actions.append($("<a>", {
			href: url + "/preview", target: "_blank", rel: "noopener", text: __("Preview branding"),
		}));
		if (frm.doc.enabled) {
			actions.append(" · ", $("<a>", {
				href: url + "/install", target: "_blank", rel: "noopener", text: __("Open installation page"),
			}));
		}
	},
});
