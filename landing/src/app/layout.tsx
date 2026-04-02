import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://mosexmacchinalab.com"),
  title: {
    default: "Mosex Macchina Lab — Ethical Android MVP",
    template: "%s · Mosex Macchina Lab",
  },
  description:
    "Research prototype: artificial ethical consciousness with Bayesian inference, narrative memory, and multipolar evaluation — validated in simulation.",
  openGraph: {
    title: "Mosex Macchina Lab — Ethical Android MVP",
    description:
      "Behavioral prototype of an ethical autonomous agent. Interactive dashboard and open source simulations.",
    url: "https://mosexmacchinalab.com",
    siteName: "Mosex Macchina Lab",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Mosex Macchina Lab — Ethical Android MVP",
    description:
      "Research prototype: ethical AI consciousness model with interactive dashboard.",
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
      <body className="flex min-h-full flex-col bg-[#050508]">{children}</body>
    </html>
  );
}
