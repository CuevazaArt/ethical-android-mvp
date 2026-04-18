# landing/

Static HTML site for **Ethos Kernel** by MoSex Macchina Lab.

No npm or Node.js build step required. All pages are self-contained.

## Pages

| File | Description |
|------|-------------|
| `public/index.html` | Project landing page (features, quick start, architecture, history) |
| `public/dashboard.html` | Real-time operator dashboard — Chart.js radars, live chat, health panel |
| `public/mobile.html` | LAN mobile WebSocket chat client (no install required) |
| `public/guardian.html` | Guardian Angel operator reference and configuration guide |
| `public/ethos-transparency.html` | Transparency and limits summary (safety posture, caveats, reporting) |

## Serve locally

```bash
# From repo root — serves landing/public/ at http://localhost:9000
python -m http.server 9000 --directory landing/public
```

Open `http://localhost:9000/` for the landing page or `http://localhost:9000/dashboard.html` for the live dashboard.

## Dashboard quick start

1. Start the chat server: `python -m src.chat_server`
2. Serve this directory: `python -m http.server 9000 --directory landing/public`
3. Open `http://localhost:9000/dashboard.html`
4. Enter `ws://localhost:8765/ws/chat` (default) and click **Connect**

The dashboard connects directly to the kernel WebSocket and displays:
- Real-time radar charts (ethical pole weights, perception confidence, governance state)
- Live ethical score history (line chart)
- MalAbs safety gate status and block log
- Kernel identity and DAO governance snapshot
- Health data from `GET /health`

## LAN / mobile

From a phone on the same WiFi:
1. Find your PC's LAN IP (e.g. `192.168.1.10`)
2. Start the server with `HOST=0.0.0.0 python -m src.chat_server`
3. Open `http://192.168.1.10:9000/mobile.html` on the phone

## Crawling / SEO

Training-oriented crawlers are blocked via the parent `robots.txt` at the repo root.
Content-discovery crawlers are allowed.

---

*MoSex Macchina Lab — [mosexmacchinalab.com](https://mosexmacchinalab.com) · Apache 2.0*
