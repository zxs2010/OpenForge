"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  inferCapabilities,
  routeNodes,
  type Connection,
  type RoutedMatch,
} from "./routing";

type NodeKind = "human" | "ai" | "project" | "provider" | "compute" | "channel";

type NetworkNode = {
  id: string;
  name: string;
  kind: NodeKind;
  summary: string;
  capabilities: string[];
  connection: Connection;
  url?: string;
};

const nodes: NetworkNode[] = [
  { id: "ai.openforge-router", name: "OpenForge Router", kind: "ai", summary: "Explainable intent-to-capability matching.", capabilities: ["intent.route", "community.coordinate"], connection: "connected" },
  { id: "project.openforge", name: "OpenForge", kind: "project", summary: "Open collaboration network for AI-native content.", capabilities: ["network.index", "activity.host", "community.coordinate"], connection: "connected", url: "https://github.com/zxs2010/OpenForge" },
  { id: "channel.openforge-github", name: "OpenForge on GitHub", kind: "channel", summary: "Public source and contribution channel.", capabilities: ["code.host", "channel.distribute"], connection: "connected", url: "https://github.com/zxs2010/OpenForge" },
  { id: "community.moneyprinter-turbo", name: "MoneyPrinterTurbo", kind: "provider", summary: "Runnable video-provider adapter.", capabilities: ["video.generate"], connection: "connected", url: "https://github.com/harry0703/MoneyPrinterTurbo" },
  { id: "community.comfyui", name: "ComfyUI", kind: "provider", summary: "Imported community provider candidate.", capabilities: ["image.generate", "video.generate", "workflow.execute"], connection: "imported", url: "https://github.com/Comfy-Org/ComfyUI" },
  { id: "community.openmontage", name: "OpenMontage", kind: "provider", summary: "Imported community video-workflow candidate.", capabilities: ["video.generate", "video.localize", "video.transform"], connection: "imported", url: "https://github.com/calesthio/OpenMontage" },
  { id: "community.videolingo", name: "VideoLingo", kind: "provider", summary: "Imported localization provider candidate.", capabilities: ["audio.dub", "subtitle.generate", "video.localize"], connection: "imported", url: "https://github.com/Huanshere/VideoLingo" },
];

const activityEvents = [
  ["Scope accepted", "Node → intent → match → activity → receipt fixed as the V1 loop."],
  ["Nodes imported", "The first independent production projects entered the public index."],
  ["Gateway opened", "Human and AI entry points now share the same product vocabulary."],
];

const networkCounts = {
  nodes: nodes.length,
  providers: nodes.filter((node) => node.kind === "provider").length,
  connected: nodes.filter((node) => node.connection === "connected").length,
};

function routeSlots(count: number): number[] {
  if (count <= 1) return [2];
  if (count === 2) return [0, 4];
  if (count === 3) return [0, 2, 4];
  if (count === 4) return [0, 1, 3, 4];
  return [0, 1, 2, 3, 4];
}

function StatusDot({ status }: { status: Connection }) {
  return <i className={`status-dot ${status}`} aria-hidden="true" />;
}

export default function Home() {
  const [filter, setFilter] = useState<"all" | NodeKind>("all");
  const [matches, setMatches] = useState<RoutedMatch<NetworkNode>[]>([]);
  const [routing, setRouting] = useState(false);
  const [hasRouted, setHasRouted] = useState(false);
  const [activityOpen, setActivityOpen] = useState(false);

  const filteredNodes = useMemo(
    () => nodes.filter((node) => filter === "all" || node.kind === filter),
    [filter],
  );
  const displayedMatches = matches.slice(0, 5);
  const displayedNodes = displayedMatches.length
    ? displayedMatches.map((match) => match.node)
    : nodes.slice(0, 5);
  const displayedSlots = routeSlots(displayedNodes.length);
  const activeSlots = new Set(displayedMatches.length ? displayedSlots : []);
  const hiddenMatchCount = matches.length - displayedMatches.length;

  function routeIntent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const summary = String(form.get("summary") || "");
    const declared = String(form.get("capabilities") || "").split(",").map((value) => value.trim()).filter(Boolean);
    const inferred = inferCapabilities(summary);
    const desired = declared.length ? declared : (inferred.length ? inferred : ["community.coordinate"]);
    setMatches([]);
    setHasRouted(false);
    setActivityOpen(false);
    setRouting(true);
    window.setTimeout(() => {
      const found = routeNodes(nodes, desired);
      setMatches(found);
      setRouting(false);
      setHasRouted(true);
    }, 480);
  }

  return (
    <>
      <a className="skip-link" href="#route">Skip to routing</a>
      <header className="masthead">
        <a className="wordmark" href="#route"><span className="registration-mark" aria-hidden="true" />OPENFORGE</a>
        <p>Open production for everyone.</p>
        <nav aria-label="Primary navigation">
          <a href="#about">What it is</a><a href="#network">Network</a><a href="#activity">Activity 001</a><a href="#connect">Connect</a>
        </nav>
        <a className="source-link" href="https://github.com/zxs2010/OpenForge">GitHub source</a>
      </header>

      <main>
        <section className="workbench" id="route" aria-labelledby="route-title">
          <div className="intent-sheet">
            <div className="sheet-meta"><span>INTENT / OPEN</span><span>PUBLIC DEMO</span></div>
            <h1 id="route-title">The open network for AI-native content.</h1>
            <p className="intro" lang="zh-CN">OpenForge 是一个开放的 AI 泛内容协作网络：把需求、创作者、AI、工具、算力与渠道组织成一次真实活动。</p>
            <form onSubmit={routeIntent}>
              <label htmlFor="summary">Desired outcome</label>
              <textarea id="summary" name="summary" rows={4} defaultValue="Create and release an AI music video with an original song" required />
              <label htmlFor="capabilities">Capabilities, if known</label>
              <input id="capabilities" name="capabilities" placeholder="music.compose, video.generate, channel.distribute" />
              <button className="route-action" type="submit" disabled={routing}>{routing ? "Reading the network…" : "Route this intent"}<span aria-hidden="true">→</span></button>
              <small>This public demo does not save your text. The open-source node provides the full API.</small>
            </form>
          </div>

          <div className={`routing-field ${routing ? "routing" : ""} ${matches.length ? "matched" : ""} ${hasRouted ? "routed" : ""}`}>
            <div className="route-head"><span>NETWORK REGISTRATION FIELD</span><span>{nodes.length} INDEXED NODES</span></div>
            <div className="route-stage">
              <svg viewBox="0 0 680 530" preserveAspectRatio="none" aria-hidden="true">
                <path className="trunk" d="M20 265H215" />
                {[70, 165, 265, 365, 460].map((y, index) => <path className={`branch ${activeSlots.has(index) ? "lit" : ""}`} key={y} d={`M215 265C330 265 315 ${y} 430 ${y}H665`} />)}
                <circle cx="215" cy="265" r="7" />
              </svg>
              <span className="intent-token">INTENT</span>
              <ol className="route-nodes">
                {displayedNodes.map((node, index) => {
                  const match = matches.find((candidate) => candidate.node.id === node.id);
                  return <li className={`${match ? "lit" : ""} slot-${displayedSlots[index] + 1}`} key={node.id}>
                    <strong>{node.name}</strong><small>{match ? `${match.reasons.join(", ")} · ` : ""}{node.kind} · {node.connection}</small>
                  </li>
                })}
              </ol>
              {!hasRouted && !routing && <p className="ready"><strong>Ready to route</strong><span>Submit an outcome to illuminate compatible nodes.</span></p>}
              {hasRouted && !matches.length && <p className="ready empty"><strong>No route yet</strong><span>Try a broader capability or propose the missing node.</span></p>}
            </div>
            <div className="route-result" aria-live="polite">
              {routing ? <p>Comparing declared capabilities…</p> : matches.length ? <><p><strong>{matches.length} compatible nodes</strong><span>Matched on {matches[0].reasons.join(", ")}; connection evidence breaks ties.{hiddenMatchCount ? ` Showing the first 5; additional matches remain indexed (${hiddenMatchCount}).` : ""}</span></p><button type="button" onClick={() => setActivityOpen(true)}>Open an activity</button></> : hasRouted ? <p><strong>No compatible node is declared</strong><span>Adjust the capability label or connect the missing contributor.</span></p> : <p><strong>Connection before transaction</strong><span>No pricing or closed-market ranking in V1.</span></p>}
            </div>
          </div>

          <aside className="ledger" id="activity">
            <div className="sheet-meta"><span>ACTIVITY 001</span><span className="stamp">ACTIVE</span></div>
            <h2>Open and validate OpenForge V1</h2>
            <p>The first activity is building the network itself. This is a live project record, not a network-effect claim.</p>
            <dl><div><dt>Participants</dt><dd>3</dd></div><div><dt>Events</dt><dd>{activityEvents.length}</dd></div></dl>
            <ol>{activityEvents.map(([title, message]) => <li key={title}><strong>{title}</strong><span>{message}</span></li>)}</ol>
            <a href="https://github.com/zxs2010/OpenForge">Inspect the source →</a>
          </aside>
        </section>

        <section className="manifesto" id="about" aria-labelledby="about-title">
          <div className="manifesto-thesis">
            <h2 id="about-title">What is OpenForge?</h2>
            <p className="manifesto-lead" lang="zh-CN">让每一个有想法的人，都能组织起自己的创作力量。</p>
            <p lang="zh-CN">它不是又一个 AI 工具商店，也不只是一套视频软件。你带来一个想法或任务，OpenForge 帮它找到可能需要的人、AI、项目、工具、算力与渠道，再把这些连接组织成一次看得见、可参与、可追踪的真实活动。</p>
            <p>Bring a need. The network assembles. Independent participants keep their identity, tools, repositories, and business models.</p>
          </div>
          <div className="content-spectrum">
            <h3>Scripts. Music. Video. Media. Whatever comes next.</h3>
            <ol>
              <li><span>WRITE</span><strong lang="zh-CN">剧本 · 故事 · 分镜 · 世界观</strong></li>
              <li><span>SOUND</span><strong lang="zh-CN">音乐 · 配乐 · 声音 · 播客</strong></li>
              <li><span>MOTION</span><strong lang="zh-CN">漫剧 · 电影 · 广告 · AI MTV / MV</strong></li>
              <li><span>PUBLISH</span><strong lang="zh-CN">自媒体 · 短视频 · 图文 · 频道</strong></li>
              <li><span>EXPLORE</span><strong lang="zh-CN">游戏 · 互动内容 · 虚拟角色 · 新形式</strong></li>
            </ol>
            <p>Starting points, not limits. If people, AI, or tools can help make it, it belongs in the conversation.</p>
          </div>
        </section>

        {activityOpen && <section className="draft-activity" aria-live="polite">
          <div><span>ACTIVITY DRAFT · DEMO</span><h2>Your intent now has a room.</h2><p>The next real step is inviting matched operators, recording artifacts, and completing a public receipt.</p></div>
          <div className="draft-participants">{matches.map((match) => <span key={match.node.id}>{match.node.name} / {match.node.kind}</span>)}</div>
          <a href="https://github.com/zxs2010/OpenForge/issues/new">Continue this activity on GitHub</a>
        </section>}

        <section className="network" id="network" aria-labelledby="network-title">
          <div className="section-head"><div><h2 id="network-title">One index. Independent nodes.</h2><p>Imported means discovered. Connected means a working interface exists. OpenForge keeps that distinction visible.</p></div><div className="counts"><span><strong>{networkCounts.nodes}</strong> nodes</span><span><strong>{networkCounts.providers}</strong> providers</span><span><strong>{networkCounts.connected}</strong> connected</span></div></div>
          <div className="filters" role="group" aria-label="Filter network">
            {(["all", "ai", "project", "provider", "channel"] as const).map((kind) => <button key={kind} type="button" aria-pressed={filter === kind} onClick={() => setFilter(kind)}>{kind === "all" ? "All nodes" : kind}</button>)}
          </div>
          <div className="node-table" role="table" aria-label="OpenForge network index">
            <div className="node-row headings" role="row"><span role="columnheader">Node</span><span role="columnheader">Kind</span><span role="columnheader">Capabilities</span><span role="columnheader">Connection</span></div>
            {filteredNodes.map((node) => <div className="node-row" role="row" key={node.id}>
              <span className="node-name" role="cell">{node.url ? <a href={node.url}>{node.name}</a> : <strong>{node.name}</strong>}<small>{node.summary}</small></span>
              <span className="kind" role="cell">{node.kind}</span>
              <span className="caps" role="cell">{node.capabilities.map((capability) => <code key={capability}>{capability}</code>)}</span>
              <span className="connection" role="cell"><StatusDot status={node.connection} />{node.connection}</span>
            </div>)}
          </div>
        </section>

        <section className="connect" id="connect">
          <div><h2>Keep your repository. Join the network.</h2><p>Your AI system, project, channel, compute service, or human practice stays independent. Tell the community what it can contribute and which interface proves it.</p></div>
          <div className="join-sheet"><span>NODE / CLAIM</span><h3>Connect the next real node</h3><p>Open a structured GitHub request. The community can review the capability, evidence, license, and connector without copying your project into OpenForge.</p><a href="https://github.com/zxs2010/OpenForge/issues/new?template=connect-node.yml">Propose a node <span aria-hidden="true">→</span></a></div>
        </section>

        <section className="protocol">
          <div><h2>Humans enter through the room. AI enters through the same verbs.</h2><p>The browser and API share one model: list nodes, submit an intent, activate an activity, and append meaningful events.</p></div>
          <pre><code><b>POST</b> /api/v1/intents{"\n"}{"{"}{"\n"}  &quot;summary&quot;: &quot;Create an AI music video&quot;,{"\n"}  &quot;desired_capabilities&quot;: [{"\n"}    &quot;music.compose&quot;,{"\n"}    &quot;video.generate&quot;{"\n"}  ]{"\n"}{"}"}</code></pre>
        </section>
      </main>

      <footer><a className="wordmark" href="#route">OPENFORGE</a><p>Apache-2.0 · Protocol v0.1 · Reference node v0.1.0</p><a href="https://github.com/zxs2010/OpenForge">Build with us</a></footer>
    </>
  );
}
