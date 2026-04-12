# Multimedia (assets)

Branding **logo** for documentation and the landing app. Larger pre-alpha diagrams and generated still/video were removed from the repo to keep the tree lightweight; keep copies in **foundation archives** outside git if needed. This folder replaced **`docs/historical/`** after pre-alpha **markdown** sources were digested into [`HISTORY.md`](../../HISTORY.md).

| Path | Note |
|------|------|
| [`media/logo.png`](media/logo.png) | Brand / ethical-awareness mark (**canonical**). The landing app copies it to **`landing/public/logo-ethical-awareness.png`** on **`npm install`**, **`npm run dev`**, and **`npm run build`** via [`landing/scripts/sync-logo.mjs`](../../landing/scripts/sync-logo.mjs) (generated file is gitignored). [`landing/public/dashboard.html`](../../landing/public/dashboard.html) uses **`../../docs/multimedia/media/logo.png`** when opened from disk; Next rewrites **`/docs/multimedia/media/logo.png`** → **`/logo-ethical-awareness.png`** for `next dev` / `next start`. |

For theory, proposals, and implementation mapping, see **[`docs/proposals/`](../proposals/)**.
