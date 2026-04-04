import Link from "next/link";

import { DemoSignalAccent } from "@/components/page-accents/DemoSignalAccent";
import { DemoIntroPanel } from "@/components/DemoIntroPanel";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

export default function DemoPage() {
  return (
    <div className="flex h-dvh flex-col bg-[#050508]">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-5">
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-3">
            <SiteBrand />
            <LanguageSwitcherPlaceholder />
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-white/[0.06] pt-3 text-sm md:border-0 md:pt-0">
            <span className="w-full text-xs text-zinc-500 md:w-auto">
              Ethical Android — dashboard
            </span>
            <Link
              href="/about"
              className="text-zinc-400 transition-colors hover:text-white"
            >
              Who we are
            </Link>
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
              className="ml-auto font-medium text-violet-300 transition hover:text-white md:ml-0"
            >
              ← Home
            </Link>
          </div>
        </div>
      </header>

      <DemoSignalAccent />

      <DemoIntroPanel />

      <iframe
        src="/dashboard.html"
        title="Ethical Android interactive dashboard"
        className="min-h-0 w-full flex-1 border-0 bg-black"
      />
    </div>
  );
}
