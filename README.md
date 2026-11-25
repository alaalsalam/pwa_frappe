# PWA Frappe

PWA Frappe adds installation manifests and a service worker to Frappe. MIS Development uses a central catalog and a separate installation page for each system.

## MIS App Center

Open [MIS App Center](https://dev.mwe-mis.maward.org/mis-apps) and choose a system. On Android, use the browser's install action from that system's page. On iPhone, use Safari's **Share → Add to Home Screen** and enable **Open as Web App** if offered. A page only shows its interactive Install button after the browser sends an installation prompt.

The system's stable identity is `/mis-apps/<application-code>`. Its manifest scope is `/mis-apps/<application-code>/`, with `/install` as its initial page and `/open` handing off to Frappe's ordinary login and native Desk entry. The browser may show navigation controls on the existing Desk or login route, depending on its handling of out-of-scope pages. Business permissions and data access remain with the target application and Frappe.

## Manage a catalog entry

1. Open **PWA Application** in Desk as a System Manager. Create an entry with a permanent code, bilingual names, a short home-screen name, colors, version, an installed app and its verified existing entry route.
2. Upload public PNGs at 192 × 192 and 512 × 512. The optional maskable 512 × 512 icon should keep important art within the centered safe area.
3. Save with **Published** cleared. Use **Preview branding** to check the entry. Publishing makes its install page, manifest and Open action available.
4. Turn off **Published** to take an entry out of the center. Keep the original code when changing branding, version or the target entry route for an already distributed application.

The checked-in MIS catalog is a deployment configuration. Reapply it only when its values should replace the managed rows in Development. Unrelated records are preserved and rerunning the same catalog produces no duplicate records.

```bash
bench --site dev.mwe-mis.maward.org execute pwa_frappe.catalog.apply
```

## Runtime and rollback

MIS Development uses Frappe and ERPNext 16.60. Install the app from this repository in the existing bench, then install it only on the intended site. The center uses static CSS and JavaScript from `pwa_frappe/public`. Bench's public assets link must exist. A shared asset rebuild is unnecessary when the assets link is already in place.

For a code update, keep the previous Git SHA and take a private site backup before metadata changes. Reapply the catalog when changing its checked-in values, then verify manifests and public asset responses on the target site. Change versioned CSS or JS filenames when changing their cacheable content. During rollback, unpublish affected catalog rows and restore the prior verified code and configuration through the existing site release procedure. Keep a safe service worker at the original worker URLs until client browsers can update. The upstream worker predating this fork's hardening is unsuitable as a live rollback target.

## Caching and notifications

The worker handles an offline message for the installation center and has an exact allowlist of versioned, public static resources. It fetches cache candidates without credentials or redirects and respects private, no-store and no-cache policies. The worker does not store navigation responses, Desk data, APIs, attachments or transactions. Activation removes older cache names belonging to the PWA worker and preserves other application caches.

The legacy `Web App Manifest` Single, `/manifest.json` and generic `/install` remain available. External push subscriptions and delivery are inactive in the MIS release. Frappe's own notifications use their normal Desk behavior.

The bundled MIT license is in [license.txt](license.txt).
