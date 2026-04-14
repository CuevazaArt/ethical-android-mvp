/**
 * Single source for “what the repo actually is” on the landing (version, distribution, validation).
 * Keep aligned with pyproject.toml and README; kernelRepo.json is synced via npm run sync-kernel-meta.
 */
import kernelRepo from "./kernelRepo.json";
import { repoFile } from "./site";

export const KERNEL_PACKAGE_VERSION = kernelRepo.pyprojectVersion;
export const LANDING_PACKAGE_VERSION = kernelRepo.landingPackageVersion;

/** Repo doc on scope, limits, and what is not claimed. */
export const TRANSPARENCY_DOC_HREF = repoFile("docs/TRANSPARENCY_AND_LIMITS.md");
