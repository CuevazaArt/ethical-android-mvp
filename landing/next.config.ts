import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static HTML in public/ uses ../../docs/multimedia/... (works as file://). Under next dev/start,
  // map that URL to the synced copy in public/.
  async rewrites() {
    return [
      {
        source: "/docs/multimedia/logo-ethical-awareness.png",
        destination: "/logo-ethical-awareness.png",
      },
    ];
  },
};

export default nextConfig;
