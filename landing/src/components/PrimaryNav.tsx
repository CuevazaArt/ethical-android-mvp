"use client";

import Link from "next/link";

import { REPO_URL, repoFile } from "@/config/site";

type PanelLink = {
  href: string;
  label: string;
  external?: boolean;
};

function NavPanel({ links }: { links: PanelLink[] }) {
  return (
    <div className="nav-details-panel">
      {links.map((item) =>
        item.external ? (
          <a
            key={item.href + item.label}
            href={item.href}
            className="nav-details-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            {item.label}
          </a>
        ) : (
          <Link key={item.href + item.label} href={item.href} className="nav-details-link">
            {item.label}
          </Link>
        ),
      )}
    </div>
  );
}

function NavDisclosure({ label, links }: { label: string; links: PanelLink[] }) {
  return (
    <details className="nav-details group relative">
      <summary className="nav-details-summary">
        <span>{label}</span>
        <span className="nav-details-chevron" aria-hidden>
          ▾
        </span>
      </summary>
      <NavPanel links={links} />
    </details>
  );
}

const PROJECT_LINKS: PanelLink[] = [
  { href: "#hostable", label: "Hostable core" },
  { href: "#model", label: "Model" },
  { href: "#theory", label: "Theory" },
  { href: "#research", label: "Research" },
  { href: "#mission", label: "Mission & values" },
];

const COMMUNITY_LINKS: PanelLink[] = [
  { href: "#contact", label: "Contact" },
  { href: "#collaborate", label: "Collaborate" },
  { href: "#support", label: "Support & funding" },
];

const PARTNER_LINKS: PanelLink[] = [
  { href: "/investors", label: "Investors" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/blockchain-dao", label: "BlockChainDAO" },
  { href: "/donate", label: "Donate" },
];

const RESOURCE_LINKS: PanelLink[] = [
  { href: "/one-pager", label: "One-pager" },
  { href: "/demo", label: "Live demo" },
  { href: repoFile("BIBLIOGRAPHY.md"), label: "Bibliography", external: true },
  { href: REPO_URL, label: "GitHub", external: true },
];

export function PrimaryNav() {
  return (
    <nav
      className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-zinc-300"
      aria-label="Primary"
    >
      <Link href="/about" className="transition-colors hover:text-white">
        Who we are
      </Link>
      <NavDisclosure label="Project" links={PROJECT_LINKS} />
      <NavDisclosure label="Community" links={COMMUNITY_LINKS} />
      <a href="#engage" className="transition-colors hover:text-white">
        Engage
      </a>
      <NavDisclosure label="Partners" links={PARTNER_LINKS} />
      <NavDisclosure label="Resources" links={RESOURCE_LINKS} />
    </nav>
  );
}
