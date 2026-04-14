import Link from "next/link";

import {
  KERNEL_PACKAGE_VERSION,
  TRANSPARENCY_DOC_HREF,
} from "@/config/projectReality";

/**
 * Site-wide honesty strip: matches pyproject/README so marketing visuals (math, 3D) do not
 * imply a shipped product, PyPI publication, external benchmarks, or on-chain DAO.
 */
export function ProjectRealityBanner() {
  return (
    <aside
      className="border-b border-amber-500/20 bg-amber-950/40 px-4 py-2.5 text-xs leading-relaxed text-amber-100/95"
      role="note"
      aria-label="Project maturity and distribution facts"
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-1.5 md:flex-row md:flex-wrap md:items-baseline md:gap-x-2 md:gap-y-1">
        <span className="shrink-0 font-medium text-amber-200/95">
          Research reference — not a released product:
        </span>
        <span className="text-amber-100/90">
          Kernel <strong className="font-semibold text-amber-50">{KERNEL_PACKAGE_VERSION}</strong>
          {" · "}
          install from Git (not published to PyPI)
          {" · "}
          evidence today is internal pytest invariants, not an independent external benchmark
          {" · "}
          DAO / governance in the tree is mock / simulated (not on-chain production)
        </span>
        <Link
          href={TRANSPARENCY_DOC_HREF}
          className="shrink-0 text-amber-300/95 underline decoration-amber-400/45 underline-offset-2 hover:text-amber-100 md:ml-auto"
          target="_blank"
          rel="noopener noreferrer"
        >
          Transparency &amp; limits
        </Link>
      </div>
    </aside>
  );
}
