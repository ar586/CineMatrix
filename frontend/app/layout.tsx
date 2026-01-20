import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import Sidebar from "@/components/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:4000'),
  title: {
    template: '%s | CineMatrix',
    default: 'CineMatrix',
  },
  description: "Real-time AI-driven sentiment analysis for movies, tracking audience reactions across Reddit, YouTube, and News.",
  keywords: ['Movie Sentiment', 'AI Analysis', 'Box Office Prediction', 'Film Analytics', 'Cinema Trends'],
  openGraph: {
    title: 'CineMatrix - Real-time Movie Sentiment',
    description: 'Track movie sentiment in real-time using AI.',
    siteName: 'CineMatrix',
    type: 'website',
    images: ['/og-image.jpg'], // Assuming you might have one or will basic generic one
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CineMatrix',
    description: 'Real-time AI movie sentiment tracking.',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <AuthProvider>
          <Sidebar />
          <main style={{ minHeight: '100vh', padding: '2rem', paddingLeft: '4rem' }}>
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
