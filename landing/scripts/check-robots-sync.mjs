/**
 * Ensure landing/src/app/robots.ts still mentions every training-crawler User-agent
 * blocked in the repository root robots.txt (Disallow: /).
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const landingRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(landingRoot, "..");
const robotsTxt = path.join(repoRoot, "robots.txt");
const robotsTs = path.join(landingRoot, "src", "app", "robots.ts");

function parseRobotsTxtDisallowedAgents(raw) {
  const lines = raw.split(/\r?\n/);
  const blocked = new Set();
  let current = null;
  for (const line of lines) {
    const u = line.match(/^\s*User-agent:\s*(\S+)/i);
    if (u) {
      current = u[1].trim();
      continue;
    }
    const d = line.match(/^\s*Disallow:\s*(\S+)/i);
    if (d && current && current !== "*") {
      if (d[1].trim() === "/") blocked.add(current);
    }
  }
  return blocked;
}

const txtRaw = fs.readFileSync(robotsTxt, "utf8");
const tsRaw = fs.readFileSync(robotsTs, "utf8");
const blocked = parseRobotsTxtDisallowedAgents(txtRaw);

for (const agent of blocked) {
  if (!tsRaw.includes(`"${agent}"`)) {
    console.error(`robots.ts missing User-agent from root robots.txt: ${agent}`);
    process.exit(1);
  }
}

const tsAgents = [
  ...tsRaw.matchAll(/userAgent:\s*"([^"]+)"/gi),
].map((m) => m[1]).filter((a) => a !== "*");
const tsSet = new Set(tsAgents);
if (tsSet.size !== blocked.size) {
  const extra = [...tsSet].filter((a) => !blocked.has(a));
  const missing = [...blocked].filter((a) => !tsSet.has(a));
  console.error(
    `robots.ts User-agent count (${tsSet.size}) != robots.txt blocklist (${blocked.size}).`,
  );
  if (extra.length) console.error("Extra in robots.ts only:", extra.sort().join(", "));
  if (missing.length) console.error("Missing from robots.ts:", missing.sort().join(", "));
  process.exit(1);
}

console.log("robots.txt blocklist matches robots.ts:", blocked.size, "agents");
