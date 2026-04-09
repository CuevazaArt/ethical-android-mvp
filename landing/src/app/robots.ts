import type { MetadataRoute } from "next";

import { SITE_URL } from "@/config/site";

export default function robots(): MetadataRoute.Robots {
  const base = SITE_URL.replace(/\/$/, "");
  // Default: no indexación ni scraping de contenido (protección de IP / anti-crawling).
  // Para permitir SEO en un entorno concreto, cambiar a allow: "/" y revisar ai.txt + LICENSE.
  const disallowAll = "/";
  return {
    rules: [
      { userAgent: "*", disallow: disallowAll },
      { userAgent: "GPTBot", disallow: disallowAll },
      { userAgent: "ChatGPT-User", disallow: disallowAll },
      { userAgent: "Google-Extended", disallow: disallowAll },
      { userAgent: "CCBot", disallow: disallowAll },
      { userAgent: "anthropic-ai", disallow: disallowAll },
      { userAgent: "Claude-Web", disallow: disallowAll },
      { userAgent: "Bytespider", disallow: disallowAll },
      { userAgent: "FacebookBot", disallow: disallowAll },
    ],
    host: base.replace(/^https?:\/\//, ""),
  };
}
