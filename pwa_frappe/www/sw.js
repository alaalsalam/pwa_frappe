"use strict";

const CACHE = "pwa-frappe-public-v1";
const ASSETS = new Map([
	["/assets/pwa_frappe/mis/center-v1.css", "text/css"],
	["/assets/pwa_frappe/mis/center-v1.js", /^(application|text)\/javascript$/],
]);

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
	event.waitUntil((async () => {
		const keys = await caches.keys();
		await Promise.all(keys.filter((key) =>
			key !== CACHE && /^(pwa-frappe-public-v\d+|frappe-cache-v\d+)$/.test(key)
		).map((key) => caches.delete(key)));
		await self.clients.claim();
	})());
});

async function publicAsset(path, expectedType) {
	const asset = new Request(new URL(path, self.location.origin), {
		credentials: "omit", redirect: "error", cache: "no-cache",
	});
	let response;
	try {
		response = await fetch(asset);
	} catch (error) {
		const cache = await caches.open(CACHE);
		const cached = await cache.match(asset);
		if (cached) return cached;
		throw error;
	}

	const policy = response.headers.get("Cache-Control") || "";
	const type = (response.headers.get("Content-Type") || "").split(";")[0].toLowerCase();
	const matchesType = typeof expectedType === "string" ? type === expectedType : expectedType.test(type);
	const cache = await caches.open(CACHE);
	if (response.status === 200 && response.type === "basic" && matchesType
		&& /(?:^|,)\s*(?:public|max-age=[1-9]\d*)\s*(?:,|$)/i.test(policy)
		&& !/(?:^|,)\s*(?:private|no-store|no-cache)\b/i.test(policy)
		&& /^(?:accept-encoding)?$/i.test(response.headers.get("Vary") || "")) {
		await cache.put(asset, response.clone()).catch(() => {});
	} else {
		await cache.delete(asset);
	}
	return response;
}

const OFFLINE_PAGE = '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8">'
	+ '<meta name="viewport" content="width=device-width,initial-scale=1">'
	+ '<title>الاتصال غير متاح | MIS</title><main><h1>الاتصال غير متاح</h1>'
	+ '<p>تحقق من اتصال الإنترنت ثم أعد تحميل الصفحة.</p></main></html>';

self.addEventListener("fetch", (event) => {
	const request = event.request;
	const url = new URL(request.url);
	if (request.method !== "GET" || url.origin !== self.location.origin) return;
	if (request.mode === "navigate" && (url.pathname === "/mis-apps" || url.pathname.startsWith("/mis-apps/"))) {
		event.respondWith(fetch(request, {cache: "no-store"}).catch(() => new Response(OFFLINE_PAGE, {
			status: 503, headers: {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store"},
		})));
		return;
	}
	const expectedType = ASSETS.get(url.pathname);
	if (!expectedType || url.search || request.headers.has("Authorization") || request.headers.has("Range")
		|| !["script", "style"].includes(request.destination)) return;
	event.respondWith(publicAsset(url.pathname, expectedType).catch(() => fetch(request)));
});
