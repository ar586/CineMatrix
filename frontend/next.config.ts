import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || (process.env.IS_DOCKER ? 'http://backend:7000' : 'http://localhost:7000');
    console.log('DEBUG: Proxying to', backendUrl);
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`, // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
