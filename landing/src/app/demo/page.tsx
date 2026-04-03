import Link from "next/link";

import { DemoIntroPanel } from "@/components/DemoIntroPanel";

export default function DemoPage() {
  return (
    <div className="flex h-dvh flex-col bg-[#050508]">
      <header className="flex shrink-0 items-center justify-between border-b border-white/[0.08] px-4 py-3 md:px-5">
        <Link
          href="/"
          className="text-sm font-medium text-violet-300 transition hover:text-white"
        >
          ← Back
        </Link>
        <span className="text-xs text-zinc-500">Ethical Android — dashboard</span>
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
