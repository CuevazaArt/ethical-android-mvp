import type { MetadataRoute } from "next";

import { SITE_URL } from "@/config/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = SITE_URL.replace(/\/$/, "");
  return [
    { url: `${base}/`, lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    { url: `${base}/about`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.85 },
    { url: `${base}/demo`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: `${base}/donate`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.75 },
    { url: `${base}/investors`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.85 },
    { url: `${base}/roadmap`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.85 },
    { url: `${base}/blockchain-dao`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/one-pager`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
  ];
}
