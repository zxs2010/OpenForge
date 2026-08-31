import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { inferCapabilities, routeNodes } from "../app/routing.ts";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the OpenForge public gateway", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>OpenForge — Open production for everyone<\/title>/i);
  assert.match(html, /Bring a need\. Leave with a network\./);
  assert.match(html, /NETWORK REGISTRATION FIELD/);
  assert.match(html, /ACTIVITY 001/);
  assert.match(html, /One index\. Independent nodes\./);
  assert.match(html, /Keep your repository\. Join the network\./);
  assert.match(html, /https:\/\/github\.com\/zxs2010\/OpenForge/);
  assert.doesNotMatch(html, /codex-preview|loading skeleton|react-loading-skeleton/i);
});

test("ships an interactive, accessible project entrance", async () => {
  const [page, layout, packageJson] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);

  assert.match(page, /function routeIntent/);
  assert.match(page, /aria-live="polite"/);
  assert.match(page, /role="columnheader"/);
  assert.match(page, /lang="zh-CN"/);
  assert.match(page, /No compatible node is declared/);
  assert.match(page, /match\.reasons\.join/);
  assert.match(page, /matches\.slice\(0, 5\)/);
  assert.match(page, /additional matches remain indexed/);
  assert.match(page, /This public demo does not save your text/);
  assert.match(page, /issues\/new\?template=connect-node\.yml/);
  assert.match(layout, /OpenForge — Open production for everyone/);
  assert.match(layout, /@fontsource\/newsreader\/400\.css/);
  assert.doesNotMatch(page, /_sites-preview|SkeletonPreview/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(styles, /input::placeholder, textarea::placeholder/);
  assert.doesNotMatch(styles, /\.node-row\.headings\s*\{\s*display:\s*none/);
});

test("mirrors the reference node's deterministic routing contract", () => {
  assert.deepEqual(inferCapabilities("Dub this video for a Chinese launch"), [
    "audio.dub",
    "community.coordinate",
    "video.generate",
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
