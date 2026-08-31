import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  messages,
  nodeSummaries,
  getLocaleStorage,
  readStoredLocale,
  writeStoredLocale,
} from "../app/i18n.ts";
import { inferCapabilities, routeNodes } from "../app/routing.ts";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the OpenForge public gateway", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<html lang="zh-CN">/);
  assert.match(html, /<title>OpenForge — 让创作向所有人开放<\/title>/i);
  assert.match(html, /面向 AI 原生内容的开放协作网络。/);
  assert.match(html, /OpenForge 是什么？/);
  assert.match(html, /让每一个有想法的人，都能组织起自己的创作力量/);
  assert.match(html, /剧本、音乐、影像、媒体，以及下一种内容。/);
  assert.match(html, /AI MTV \/ MV/);
  assert.match(html, /开放网络匹配区/);
  assert.match(html, /活动 001/);
  assert.match(html, /一个索引，连接独立节点。/);
  assert.match(html, /保留你的仓库，加入开放网络。/);
  assert.match(html, /https:\/\/github\.com\/zxs2010\/OpenForge/);
  assert.doesNotMatch(html, /codex-preview|loading skeleton|react-loading-skeleton/i);
});

test("server-renders a complete English route with localized metadata", async () => {
  const response = await render("/en");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<html lang="en">/);
  assert.match(html, /<title>OpenForge — Open production for everyone<\/title>/i);
  assert.match(html, /The open network for AI-native content\./);
  assert.match(html, /What is OpenForge\?/);
  assert.match(html, /Scripts\. Music\. Video\. Media\. Whatever comes next\./);
  assert.match(html, /One index\. Independent nodes\./);
  assert.match(html, /Keep your repository\. Join the network\./);
  assert.match(html, /class="site-shell" lang="en"/);
  assert.doesNotMatch(html, /面向 AI 原生内容的开放协作网络。/);
});

test("ships an interactive, accessible project entrance", async () => {
  const [page, layout, i18n, packageJson] = await Promise.all([
    readFile(new URL("../app/OpenForgeHome.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/(zh)/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/i18n.ts", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);

  assert.match(page, /function routeIntent/);
  assert.match(page, /aria-live="polite"/);
  assert.match(page, /role="columnheader"/);
  assert.match(page, /type Locale/);
  assert.match(i18n, /openforge-locale/);
  assert.match(page, /aria-pressed=\{locale === "zh-CN"\}/);
  assert.match(page, /lang="zh-CN"/);
  assert.match(page, /lang="en"/);
  assert.match(page, /meta\[name="description"\]/);
  assert.match(page, /window\.history\.replaceState/);
  assert.match(i18n, /自媒体/);
  assert.match(i18n, /Social media/);
  assert.match(page, /music\.compose/);
  assert.match(i18n, /No compatible node is declared/);
  assert.match(page, /match\.reasons\.join/);
  assert.match(page, /matches\.slice\(0, 5\)/);
  assert.match(i18n, /additional/);
  assert.match(i18n, /This public demo does not save your text/);
  assert.match(page, /issues\/new\?template=connect-node\.yml/);
  assert.match(layout, /OpenForge — 让创作向所有人开放/);
  assert.match(layout, /<html lang="zh-CN">/);
  assert.match(layout, /@fontsource\/newsreader\/400\.css/);
  assert.doesNotMatch(page, /_sites-preview|SkeletonPreview/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(styles, /input::placeholder, textarea::placeholder/);
  assert.doesNotMatch(styles, /\.node-row\.headings\s*\{\s*display:\s*none/);
});

test("keeps Chinese and English message catalogs in parity", () => {
  assert.deepEqual(
    Object.keys(messages["zh-CN"]).sort(),
    Object.keys(messages.en).sort(),
  );
  assert.equal(messages["zh-CN"].navNetwork, "开放网络");
  assert.equal(messages.en.navNetwork, "Network");
  assert.match(messages["zh-CN"].matchExplanation("music.compose", 2), /其余 2 个/);
  assert.match(messages.en.matchExplanation("music.compose", 2), /2 additional matches/);
  assert.deepEqual(
    Object.keys(nodeSummaries["zh-CN"]).sort(),
    Object.keys(nodeSummaries.en).sort(),
  );
});

test("keeps locale switching usable when browser storage is denied", () => {
  const deniedStorage = {
    getItem() { throw new Error("denied"); },
    setItem() { throw new Error("denied"); },
  };
  assert.equal(readStoredLocale(deniedStorage), null);
  assert.doesNotThrow(() => writeStoredLocale(deniedStorage, "en"));
  const deniedHost = {};
  Object.defineProperty(deniedHost, "localStorage", {
    get() { throw new Error("denied"); },
  });
  assert.equal(getLocaleStorage(deniedHost), null);
});

test("mirrors the reference node's deterministic routing contract", () => {
  assert.deepEqual(inferCapabilities("Dub this video for a Chinese launch"), [
    "audio.dub",
    "community.coordinate",
    "video.generate",
  ]);
  assert.deepEqual(
    inferCapabilities("Create an AI music video with an original song"),
    ["community.coordinate", "music.compose", "video.generate"],
  );
  assert.deepEqual(inferCapabilities("制作一档自媒体播客"), [
    "community.coordinate",
    "social.publish",
  ]);

  const candidates = [
    { id: "imported", name: "Alpha", capabilities: ["audio.dub"], connection: "imported" },
    { id: "verified", name: "Zulu", capabilities: ["audio.dub"], connection: "verified" },
    { id: "connected", name: "Beta", capabilities: ["audio.dub", "video.generate"], connection: "connected" },
  ];
  assert.deepEqual(
    routeNodes(candidates, ["audio.dub", "video.generate"]).map((match) => [match.node.id, match.score]),
    [["connected", 212], ["verified", 120], ["imported", 100]],
  );
});

test("public worker sets browser security headers and patched React versions", async () => {
  const response = await render();
  assert.match(response.headers.get("content-security-policy") ?? "", /frame-ancestors 'none'/);
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  assert.equal(response.headers.get("referrer-policy"), "no-referrer");

  const packageJson = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
  assert.equal(packageJson.dependencies.react, "19.2.8");
  assert.equal(packageJson.dependencies["react-dom"], "19.2.8");
  assert.equal(packageJson.devDependencies["react-server-dom-webpack"], "19.2.8");
});
