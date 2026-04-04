import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * HSTS only on Vercel production (or when explicitly forced). Avoids pinning HSTS on
 * localhost (`next start`) or Vercel preview URLs.
 */
function shouldSendHsts(): boolean {
  if (process.env.VERCEL_ENV === "production") return true;
  if (process.env.FORCE_HSTS === "1") return true;
  return false;
}

/** Baseline headers for every matched response. */
function applyBaseline(res: NextResponse) {
  res.headers.set("X-DNS-Prefetch-Control", "on");
  /* No X-Frame-Options: SAMEORIGIN — it blocks Vercel’s dashboard preview iframe
   * (parent vercel.com ≠ child *.vercel.app). Frame policy is CSP frame-ancestors only. */
  res.headers.set("X-Content-Type-Options", "nosniff");
  res.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  res.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=(), payment=()",
  );
  if (shouldSendHsts()) {
    res.headers.set(
      "Strict-Transport-Security",
      "max-age=63072000; includeSubDomains; preload",
    );
  }
}

/**
 * Main app: no third-party script CDNs. Next/React need inline + eval in dev/build pipeline.
 * frame-src allows the /demo iframe to load /dashboard.html from the same origin.
 */
const cspApp =
  "default-src 'self'; " +
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: blob:; " +
  "font-src 'self' data:; " +
  "connect-src 'self'; " +
  "frame-src 'self'; " +
  "frame-ancestors 'self' https://vercel.com; " +
  "base-uri 'self'; " +
  "form-action 'self'; " +
  (shouldSendHsts() ? "upgrade-insecure-requests; " : "");

/**
 * dashboard.html: pinned scripts from unpkg (with SRI on tags) + Babel in-browser compile.
 */
const cspDashboard =
  "default-src 'self'; " +
  "script-src 'self' https://unpkg.com 'unsafe-inline' 'unsafe-eval'; " +
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
  "font-src 'self' https://fonts.gstatic.com data:; " +
  "img-src 'self' data:; " +
  "connect-src 'self'; " +
  "frame-ancestors 'self' https://vercel.com; " +
  "base-uri 'self'; " +
  "form-action 'self'; " +
  (shouldSendHsts() ? "upgrade-insecure-requests; " : "");

export function middleware(request: NextRequest) {
  const res = NextResponse.next();
  applyBaseline(res);

  if (request.nextUrl.pathname === "/dashboard.html") {
    res.headers.set("Content-Security-Policy", cspDashboard.trim());
  } else {
    res.headers.set("Content-Security-Policy", cspApp.trim());
  }

  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
