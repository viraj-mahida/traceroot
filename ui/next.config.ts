import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable eslint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
