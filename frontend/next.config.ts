import type { NextConfig } from "next";

const backendUrl =
  process.env.BACKEND_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://backend:7000"
    : "http://localhost:7000");

const nextConfig: NextConfig = {
  // Expose backend URL to server-side code (used by api.ts INTERNAL_API_URL)
  env: {
    INTERNAL_API_URL: `${backendUrl}/api`,
  },

  async rewrites() {
    return [
      {
        // Client-side API calls go through this proxy
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
