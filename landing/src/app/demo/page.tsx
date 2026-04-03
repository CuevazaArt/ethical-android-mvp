import Link from "next/link";

import { DemoIntroPanel } from "@/components/DemoIntroPanel";
import { SiteBrand } from "@/components/SiteBrand";

export default function DemoPage() {
  return (
    <div className="flex h-dvh flex-col bg-[#050508]">
      <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] px-4 py-3 md:px-5">
        <SiteBrand />
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="text-xs text-zinc-500">Ethical Android — dashboard</span>
          <Link
            href="/#contact"
            className="text-zinc-400 transition-colors hover:text-white"
          >
            Contact
          </Link>
          <Link
            href="/#collaborate"
            className="text-zinc-400 transition-colors hover:text-white"
          >
            Collaborate
          </Link>
          <Link
            href="/donate"
            className="text-zinc-400 transition-colors hover:text-white"
          >
            Donate
          </Link>
          <Link
            href="/"
            className="font-medium text-violet-300 transition hover:text-white"
          >
            ← Home
          </Link>
        </div>
      </header>

      <DemoIntroPanel />

      <iframe
        src="/dashboard.html"
        title="Ethical Android interactive dashboard"
        className="min-h-0 w-full flex-1 border-0 bg-black"
      />
    </div>
  );
}
