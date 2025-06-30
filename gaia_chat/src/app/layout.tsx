import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ClientProviders from "@/components/ClientProviders";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GAIA-BT - 신약개발 연구 AI 어시스턴트",
  description: "신약개발 전문 AI 연구 어시스턴트 채팅 인터페이스 - 임상시험, 약물 개발, 의료 문서 분석",
  keywords: "신약개발, 임상시험, AI 어시스턴트, 의료 연구, 약물 개발, 바이오텍, 제약",
  authors: [{ name: "GAIA-BT Team" }],
  robots: "index, follow",
  other: {
    charset: "utf-8"
  }
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#3b82f6"
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" dir="ltr">
      <head>
        {/* 한국어 웹폰트 프리로딩 */}
        <link
          rel="preconnect"
          href="https://fonts.googleapis.com"
        />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap"
          as="style"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
        {/* 한국어 의료 문서 최적화 메타태그 */}
        <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="GAIA-BT" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased korean-text`}
        style={{ 
          fontFamily: "'Pretendard', 'Noto Sans KR', 'Malgun Gothic', '맑은 고딕', 'Apple Gothic', 'Apple SD Gothic Neo', system-ui, sans-serif"
        }}
      >
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}
