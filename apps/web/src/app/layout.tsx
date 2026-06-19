import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { ShellProviders } from "@/components/providers";
import { getSiteUrl } from "@/lib/site";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
  preload: false,
});

const siteUrl = getSiteUrl();

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Jober — Assisted job applications",
    template: "%s | Jober",
  },
  description:
    "AI-assisted job applications with human review before every submit. Build your queue, watch the fills, approve and send.",
  keywords: [
    "job application automation",
    "assisted job applications",
    "AI job application",
    "human-in-the-loop",
    "job search tool",
    "cover letter generator",
    "ATS form fill",
  ],
  authors: [{ name: "Jober" }],
  creator: "Jober",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    siteName: "Jober",
    title: "Jober — Assisted job applications",
    description:
      "AI fills the form, you read the diff and hit submit. Your applications, your standard, your control.",
    images: [
      {
        url: "/images/og-cover.png",
        width: 1200,
        height: 630,
        alt: "Jober — AI-assisted job applications",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Jober — Assisted job applications",
    description:
      "AI fills the form, you read the diff and hit submit. Human-in-the-loop by design.",
    images: ["/images/og-cover.png"],
    creator: "@joberapp",
  },
  alternates: {
    canonical: siteUrl,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover" as const,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <ShellProviders>{children}</ShellProviders>
      </body>
    </html>
  );
}
