import type { Metadata } from "next";
import "@fontsource/newsreader/400.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenForge — Open production for everyone",
  description:
    "OpenForge connects needs, people, AI, projects, channels, providers, and compute into visible creative activities.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "OpenForge — Open production for everyone",
    description:
      "Route a real need through an open network and turn the connection into a visible activity.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
