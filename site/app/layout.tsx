import type { Metadata } from "next";
import "@fontsource/newsreader/400.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenForge — Open production for everyone",
  description:
    "OpenForge is an open collaboration network for AI-native content, connecting needs, creators, AI, tools, compute, projects, and channels.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "OpenForge — Open production for everyone",
    description:
      "Bring a need for scripts, music, video, self-media, or the next creative format. The open network assembles.",
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
