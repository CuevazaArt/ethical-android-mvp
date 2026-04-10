import type { Metadata } from "next";
import Link from "next/link";

import { DonateRippleAccent } from "@/components/page-accents/DonateRippleAccent";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

export const metadata: Metadata = {
  title: "Donate",
  description:
    "Support Ethos Kernel research — donation options coming soon.",
  robots: { index: true, follow: true },
};

export default function DonatePage() {
  return (
    <div className="relative flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/" className="transition-colors hover:text-white">
                Home
              </Link>
              <Link href="/about" className="transition-colors hover:text-white">
                Who we are
              </Link>
              <Link href="/demo" className="transition-colors hover:text-white">
                Live demo
              </Link>
              <a
                href="https://github.com/CuevazaArt/ethical-android-mvp/blob/main/CONTRIBUTING.md"
                className="transition-colors hover:text-white"
                target="_blank"
                rel="noopener noreferrer"
              >
                Contributing
              </a>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <DonateRippleAccent />

      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto flex w-full max-w-lg flex-1 flex-col px-6 py-16 text-center outline-none focus-visible:ring-2 focus-visible:ring-violet-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050508]"
      >
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
          Coming soon
        </p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-white md:text-3xl">
          Support this research
        </h1>
        <p className="mt-5 text-sm leading-relaxed text-zinc-400">
          We are preparing a <strong className="font-medium text-zinc-300">simple, transparent way to donate</strong>{" "}
          to MosEx Macchina Lab and keep the Ethos Kernel prototype open,
          documented, and accessible. If you believe in{" "}
          <strong className="font-medium text-zinc-300">inspectable machine ethics</strong>, check
          back here — this page will go live when the channel is ready.
        </p>
        <p className="mt-6 text-sm leading-relaxed text-zinc-500">
          Want to help <strong className="font-medium text-zinc-400">now</strong>? Star the repo, open a{" "}
          <a
            href="https://github.com/CuevazaArt/ethical-android-mvp/issues/new?template=collaboration.yml"
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
            target="_blank"
            rel="noopener noreferrer"
          >
            partnership or funding
          </a>{" "}
          thread, or read{" "}
          <a
            href="https://github.com/CuevazaArt/ethical-android-mvp/blob/main/CONTRIBUTING.md"
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
            target="_blank"
            rel="noopener noreferrer"
          >
            Contributing
          </a>
          .
        </p>
      </main>
    </div>
  );
}
