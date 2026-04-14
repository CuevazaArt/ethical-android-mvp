import type { MetadataRoute } from "next";

import { SITE_URL } from "@/config/site";

export default function robots(): MetadataRoute.Robots {
  const base = SITE_URL.replace(/\/$/, "");
  // SEO: allow search engines (campaign/discovery). Block user agents oriented
  // to training/corpus crawling (courtesy signal; not strong security).
  const d = "/";
  return {
    rules: [
      { userAgent: "*", allow: "/" },
      { userAgent: "GPTBot", disallow: d },
      { userAgent: "ChatGPT-User", disallow: d },
      { userAgent: "Google-Extended", disallow: d },
      { userAgent: "CCBot", disallow: d },
      { userAgent: "anthropic-ai", disallow: d },
      { userAgent: "Claude-Web", disallow: d },
      { userAgent: "Bytespider", disallow: d },
      { userAgent: "FacebookBot", disallow: d },
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base.replace(/^https?:\/\//, ""),
  };
}
