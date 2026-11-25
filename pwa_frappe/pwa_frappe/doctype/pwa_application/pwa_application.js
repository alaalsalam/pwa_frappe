frappe.ui.form.on("PWA Application", {
	refresh: render_application_actions,
	enabled: render_application_actions,
});

function render_application_actions(frm) {
	const actions = frm.fields_dict.launch_url.$wrapper.find(".pwa-install-preview").empty();
	const add_link = (label, icon, href) => {
		const link = $("<a>", {href, target: "_blank", rel: "noopener", class: "btn btn-default btn-sm"});
		link.append($(frappe.utils.icon(icon, "sm")).attr("aria-hidden", "true"), document.createTextNode(" " + __(label)));
		actions.append(link, " ");
	};

	if (frm.is_new()) {
		actions.text(__("Save the application to preview its branding."));
		return;
	}

	const path = "/mis-apps/" + encodeURIComponent(frm.doc.name);
	add_link("Preview saved branding", "eye", path + "/preview");
	if (!frm.doc.__unsaved && frm.doc.enabled) {
		add_link("Open installation page", "external-link", path + "/install");
		add_link("View manifest", "file-code", path + "/manifest.webmanifest");
		$("<button>", {type: "button", class: "btn btn-default btn-sm"})
			.append($(frappe.utils.icon("copy", "sm")).attr("aria-hidden", "true"),
				document.createTextNode(" " + __("Copy installation link")))
			.on("click", async () => {
				try {
					await navigator.clipboard.writeText(new URL(path + "/install", window.location.origin).href);
					frappe.show_alert({message: __("Installation link copied"), indicator: "green"});
				} catch {
					frappe.msgprint(__("Copy the address from the installation page."));
				}
			}).appendTo(actions);
	}
}
