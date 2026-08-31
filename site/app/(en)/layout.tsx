import type { Metadata } from "next";
import "@fontsource/newsreader/400.css";
import "../globals.css";
import { messages } from "../i18n";

const t = messages.en;

export const metadata: Metadata = {
  title: t.metaTitle,
  description: t.metaDescription,
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: t.metaTitle,
    description: t.metaSocialDescription,
    type: "website",
    locale: "en_US",
    alternateLocale: ["zh_CN"],
  },
};

export default function EnglishLayout({
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
