"use strict";

const installButton = document.querySelector("#install-app");
window.addEventListener("beforeinstallprompt", (event) => {
	event.preventDefault();
	installButton.hidden = false;
	installButton.onclick = async () => {
		installButton.hidden = true;
		await event.prompt();
	};
});
window.addEventListener("appinstalled", () => { installButton.hidden = true; });

if ("serviceWorker" in navigator) {
	navigator.serviceWorker.register("/mis-apps/sw.js").catch(console.error);
}

// Safari can launch the captured installation page on older releases.
if (window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true) {
	window.location.replace(document.querySelector("#open-app").href);
}
