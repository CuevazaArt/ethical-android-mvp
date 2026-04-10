import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { REPO_URL, SITE_URL } from "@/config/site";

const siteJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      name: "MosEx Macchina Lab",
      url: SITE_URL,
      sameAs: [REPO_URL],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: "MosEx Macchina Lab — Ethos Kernel",
      description:
        "Research prototype: artificial ethical consciousness with Bayesian inference, narrative memory, and multipolar evaluation — validated in simulation.",
      publisher: { "@id": `${SITE_URL}/#organization` },
      inLanguage: "en-US",
    },
  ],
} as const;

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "MosEx Macchina Lab — Ethos Kernel",
    template: "%s · MosEx Macchina Lab",
  },
  description:
    "Research prototype: artificial ethical consciousness with Bayesian inference, narrative memory, and multipolar evaluation — validated in simulation.",
  openGraph: {
    title: "MosEx Macchina Lab — Ethos Kernel",
    description:
      "Behavioral prototype of an ethical autonomous agent. Interactive dashboard and open source simulations.",
    url: SITE_URL,
    siteName: "MosEx Macchina Lab",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "MosEx Macchina Lab — Ethos Kernel",
    description:
      "Research prototype: ethical AI consciousness model with interactive dashboard.",
  },
  icons: {
    icon: "/logo-ethical-awareness.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-[#050508]">
        <a href="#main-content" className="skip-to-main">
          Skip to main content
        </a>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(siteJsonLd) }}
        />
        {children}
      </body>
    </html>
  );
}
