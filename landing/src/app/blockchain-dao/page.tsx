import type { Metadata } from "next";
import Link from "next/link";

import { BlockchainDaoAccent } from "@/components/page-accents/BlockchainDaoAccent";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

const REPO = "https://github.com/CuevazaArt/ethical-android-mvp";
const MOCK_DAO = `${REPO}/blob/main/src/modules/mock_dao.py`;

export const metadata: Metadata = {
  title: "BlockChainDAO",
  description:
    "How on-chain governance fits the Ethical Android stack today (mock DAO) and how it could evolve toward testnet or production contracts.",
  robots: { index: true, follow: true },
};

export default function BlockchainDaoPage() {
  return (
    <div className="relative flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/" className="transition-colors hover:text-white">
                Home
              </Link>
              <Link href="/investors" className="transition-colors hover:text-white">
                Investors
              </Link>
              <Link href="/roadmap" className="transition-colors hover:text-white">
                Roadmap
              </Link>
              <Link href="/demo" className="transition-colors hover:text-white">
                Live demo
              </Link>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <BlockchainDaoAccent />

      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto w-full max-w-3xl flex-1 px-6 py-12 outline-none focus-visible:ring-2 focus-visible:ring-violet-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050508] md:py-16"
      >
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
          Governance layer
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white md:text-4xl">
          BlockChainDAO
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-zinc-400 md:text-[15px]">
          <strong className="font-medium text-zinc-300">BlockChainDAO</strong> names the path from
          today&apos;s <strong className="font-medium text-zinc-300">in-process mock</strong> to a
          future <strong className="font-medium text-zinc-300">decentralized ethical oracle</strong>{" "}
          that can anchor votes, audits, and solidarity-style alerts on a public ledger — only when
          requirements, law, and partner risk are explicit. Nothing here is an offer of securities or
          a commitment to launch a token.
        </p>

        <section className="mt-12 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Place in the project</h2>
          <p className="mt-2 text-sm leading-relaxed text-zinc-500">
            The ethical kernel runs poles, vetoes, narrative memory, and simulation modules in
            Python. The DAO module sits at the <strong className="font-medium text-zinc-400">governance boundary</strong>:
            it models how community and stakeholders could ratify calibrations, review incidents,
            and record decisions with quadratic-style voting and reputation vectors — the same
            conceptual slot a chain would occupy later.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            <li>
              <strong className="font-medium text-zinc-300">Today:</strong>{" "}
              <a
                href={MOCK_DAO}
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
                target="_blank"
                rel="noopener noreferrer"
              >
                <code className="text-zinc-300">mock_dao.py</code>
              </a>{" "}
              simulates proposals, voting, audit records, and a Solidarity Alert Protocol with no
              real network or assets.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Pipeline:</strong> in the interactive
              stack, governance hooks appear after deliberation modules so collective rules can
              complement — not replace — kernel vetoes and safety predicates.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Ecosystem fit:</strong> see{" "}
              <Link
                href="/investors"
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
              >
                investors — Native DAO
              </Link>{" "}
              for why decentralized legitimacy matters next to hardware and insurance narratives.
            </li>
          </ul>
        </section>

        <section className="mt-12 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Future deployment &amp; development</h2>
          <p className="mt-2 text-sm leading-relaxed text-zinc-500">
            Moving from mock to chain is a <strong className="font-medium text-zinc-400">product and compliance project</strong>, not
            a config flip. The intended sequence is: document threat models and roles, map mock
            contracts to minimal on-chain equivalents, run controlled testnet experiments with
            non-production data, then consider mainnet only with legal review and partner
            agreements.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            <li>
              <strong className="font-medium text-zinc-300">Engineering:</strong> ABI-stable
              interfaces between the kernel and a signer or indexer; idempotent audit exports;
              optional privacy layers where public voting is inappropriate.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Research:</strong> align quadratic and
              reputation mechanics with the same ethical predicates the kernel already enforces, so
              on-chain governance cannot bypass MalAbs-class vetoes without an explicit, reviewed
              change path.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Milestones:</strong> tracked with the
              broader program on the{" "}
              <Link
                href="/roadmap"
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
              >
                roadmap
              </Link>{" "}
              page (governance beyond mock DAO).
            </li>
          </ul>
        </section>

        <section className="mt-12 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Collaborate</h2>
          <p className="mt-3 text-sm leading-relaxed text-zinc-400">
            Protocol design, security review, and jurisdiction-specific counsel are welcome via the
            repo&apos;s collaboration templates. For sensitive disclosures, follow{" "}
            <a
              href={`${REPO}/blob/main/SECURITY.md`}
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
              target="_blank"
              rel="noopener noreferrer"
            >
              SECURITY.md
            </a>
            .
          </p>
        </section>

        <p className="mt-10 text-center text-xs text-zinc-600 md:text-left">
          BlockChainDAO is a research direction; on-chain deployment timelines depend on funding,
          partners, and regulatory clarity.
        </p>
      </main>
    </div>
  );
}
