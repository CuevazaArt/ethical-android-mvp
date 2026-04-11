# Multimedia (assets)

Static **images, video, and logo** for documentation and branding. This folder replaced **`docs/historical/`** after pre-alpha **markdown** sources were digested into [`HISTORY.md`](../../HISTORY.md).

| Path | Note |
|------|------|
| [`media/logo.png`](media/logo.png) | Brand / ethical-awareness mark (**canonical**). The landing app copies it to **`landing/public/logo-ethical-awareness.png`** on **`npm install`**, **`npm run dev`**, and **`npm run build`** via [`landing/scripts/sync-logo.mjs`](../../landing/scripts/sync-logo.mjs) (generated file is gitignored). [`landing/public/dashboard.html`](../../landing/public/dashboard.html) uses **`../../docs/multimedia/media/logo.png`** when opened from disk; Next rewrites **`/docs/multimedia/media/logo.png`** → **`/logo-ethical-awareness.png`** for `next dev` / `next start`. |
| [`media/brujula_etica_jerarquica.png`](media/brujula_etica_jerarquica.png) | Pre-alpha ethical compass diagram. |
| [`media/esquema_androide_etico.png`](media/esquema_androide_etico.png) | Pre-alpha android schematic. |
| [`media/esquema_prototipo_python.png`](media/esquema_prototipo_python.png) | Pre-alpha Python prototype diagram. |
| [`media/generated_image_2026-04-08.jpg`](media/generated_image_2026-04-08.jpg) | Generated still (April 2026). |
| [`media/generated_video_2026-04-08.mp4`](media/generated_video_2026-04-08.mp4) | Short generated clip (April 2026). |

For theory, proposals, and implementation mapping, see **[`docs/proposals/`](../proposals/)**.
