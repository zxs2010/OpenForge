import type { Metadata } from "next";
import "@fontsource/newsreader/400.css";
import "../globals.css";

export const metadata: Metadata = {
  title: "OpenForge — 让创作向所有人开放",
  description:
    "OpenForge 是面向 AI 原生内容的开放协作网络，连接需求、创作者、AI、工具、算力、项目与渠道。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "OpenForge — 让创作向所有人开放",
    description:
      "带来一个剧本、音乐、影像、自媒体或下一种内容需求，让开放网络组织起协作力量。",
    type: "website",
    locale: "zh_CN",
    alternateLocale: ["en_US"],
  },
};

export default function ChineseLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
