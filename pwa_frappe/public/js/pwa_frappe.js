document.addEventListener("DOMContentLoaded", () => {
	if (window.frappe?.boot?.pwa_configure_desk && !document.querySelector('link[rel="manifest"]')) {
		const link = document.createElement("link");
		link.rel = "manifest";
		link.href = "/manifest.json";
		document.head.append(link);
	}
});
