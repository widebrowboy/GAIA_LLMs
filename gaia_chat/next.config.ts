import type { NextConfig } from "next";

// Next.js 15.3.4 버전 설정
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // 크로스 오리진 요청 경고 해결을 위한 설정
  // 타입 오류를 방지하기 위해 as any 사용
  experimental: {
    allowedDevOrigins: ['localhost', '127.0.0.1']
  } as any
} as NextConfig;

export default nextConfig;
