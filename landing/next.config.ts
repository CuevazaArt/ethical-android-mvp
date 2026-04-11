import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static HTML in public/ uses ../../docs/multimedia/media/... (works as file://). Under next dev/start,
  // map that URL to the synced copy in public/.
  async rewrites() {
    return [
      {
        source: "/docs/multimedia/media/logo.png",
        destination: "/logo-ethical-awareness.png",
      },
    ];
  },
};

export default nextConfig;
