import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // In Docker (production start), default to backend service name
    const isProd = process.env.NODE_ENV === 'production';
    const backendUrl = process.env.BACKEND_URL || (isProd ? 'http://backend:7000' : 'http://localhost:7000');
    console.log('Middleware Config:', { isProd, backendUrl, envBackend: process.env.BACKEND_URL });
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`, // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
