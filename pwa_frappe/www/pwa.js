"use strict";

if ("serviceWorker" in navigator) {
	window.addEventListener("load", () => {
		navigator.serviceWorker.register("/sw.js").catch(console.error);
	});
}
window.addEventListener("beforeinstallprompt", (event) => {
	const button = document.querySelector(".btn-pwa-install");
	if (!button) return;
	event.preventDefault();
	button.hidden = false;
	button.onclick = async () => {
		button.hidden = true;
		await event.prompt();
	};
});
