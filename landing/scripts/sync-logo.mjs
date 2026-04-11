import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const landingRoot = path.join(__dirname, "..");
const repoRoot = path.join(landingRoot, "..");
const src = path.join(repoRoot, "docs", "multimedia", "logo-ethical-awareness.png");
const dest = path.join(landingRoot, "public", "logo-ethical-awareness.png");

if (!fs.existsSync(src)) {
  console.error("sync-logo: missing source (canonical asset):", src);
  process.exit(1);
}
fs.mkdirSync(path.dirname(dest), { recursive: true });
fs.copyFileSync(src, dest);
