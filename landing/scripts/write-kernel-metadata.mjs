/**
 * Sync monorepo metadata into landing/src/config/kernelRepo.json for display + CI drift checks.
 * Reads ../../pyproject.toml (repo root) when present; otherwise keeps pyprojectVersion fallback.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const landingRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(landingRoot, "..");
const pyprojectPath = path.join(repoRoot, "pyproject.toml");
const pkgPath = path.join(landingRoot, "package.json");
const outPath = path.join(landingRoot, "src", "config", "kernelRepo.json");

function readPyprojectVersion() {
  if (!fs.existsSync(pyprojectPath)) {
    return process.env.NEXT_PUBLIC_KERNEL_PYPROJECT_VERSION || "0.0.0";
  }
  const raw = fs.readFileSync(pyprojectPath, "utf8");
  const m = raw.match(/^version\s*=\s*"([^"]+)"/m);
  return m ? m[1] : "0.0.0";
}

function readLandingVersion() {
  const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"));
  return pkg.version || "0.0.0";
}

const payload = {
  pyprojectVersion: readPyprojectVersion(),
  landingPackageVersion: readLandingVersion(),
  sourcePyproject: "pyproject.toml",
  sourceLandingPackage: "landing/package.json",
  note: "Regenerate: npm run sync-kernel-meta (from landing/). CI fails on drift vs committed file.",
};

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, `${JSON.stringify(payload, null, 2)}\n`);
