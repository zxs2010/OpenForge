"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  activityEvents,
  connectionLabels,
  getLocaleStorage,
  kindLabels,
  messages,
  nodeNames,
  nodeSummaries,
  readStoredLocale,
  writeStoredLocale,
  type Locale,
  type NodeKind,
} from "./i18n";
import {
  inferCapabilities,
  routeNodes,
  type Connection,
  type RoutedMatch,
} from "./routing";

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
  { id: "ai.openforge-router", name: "OpenForge 路由器", kind: "ai", summary: "提供可解释的需求与能力匹配。", capabilities: ["intent.route", "community.coordinate"], connection: "connected" },
  { id: "project.openforge", name: "OpenForge", kind: "project", summary: "面向 AI 原生内容的开放协作网络。", capabilities: ["network.index", "activity.host", "community.coordinate"], connection: "connected", url: "https://github.com/zxs2010/OpenForge" },
  { id: "channel.openforge-github", name: "OpenForge GitHub", kind: "channel", summary: "公开源码与社区贡献入口。", capabilities: ["code.host", "channel.distribute"], connection: "connected", url: "https://github.com/zxs2010/OpenForge" },
  { id: "community.moneyprinter-turbo", name: "MoneyPrinterTurbo", kind: "provider", summary: "已经可以运行的视频生产适配器。", capabilities: ["video.generate"], connection: "connected", url: "https://github.com/harry0703/MoneyPrinterTurbo" },
  { id: "community.comfyui", name: "ComfyUI", kind: "provider", summary: "已收录的社区生产节点候选。", capabilities: ["image.generate", "video.generate", "workflow.execute"], connection: "imported", url: "https://github.com/Comfy-Org/ComfyUI" },
  { id: "community.openmontage", name: "OpenMontage", kind: "provider", summary: "已收录的社区视频工作流候选。", capabilities: ["video.generate", "video.localize", "video.transform"], connection: "imported", url: "https://github.com/calesthio/OpenMontage" },
  { id: "community.videolingo", name: "VideoLingo", kind: "provider", summary: "已收录的视频本地化节点候选。", capabilities: ["audio.dub", "subtitle.generate", "video.localize"], connection: "imported", url: "https://github.com/Huanshere/VideoLingo" },
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

function applyDocumentLocale(locale: Locale) {
  const copy = messages[locale];
  const socialLocale = locale === "en" ? "en_US" : "zh_CN";
  const alternateSocialLocale = locale === "en" ? "zh_CN" : "en_US";
  document.documentElement.lang = locale;
  document.title = copy.metaTitle;
  document.querySelector('meta[name="description"]')?.setAttribute("content", copy.metaDescription);
  document.querySelector('meta[property="og:title"]')?.setAttribute("content", copy.metaTitle);
  document.querySelector('meta[property="og:description"]')?.setAttribute("content", copy.metaSocialDescription);
  document.querySelector('meta[property="og:locale"]')?.setAttribute("content", socialLocale);
  document.querySelector('meta[property="og:locale:alternate"]')?.setAttribute("content", alternateSocialLocale);
}

type HomeProps = {
  initialLocale?: Locale;
  detectLocale?: boolean;
};

export default function Home({
  initialLocale = "zh-CN",
  detectLocale = true,
}: HomeProps = {}) {
  const [locale, setLocale] = useState<Locale>(initialLocale);
  const [filter, setFilter] = useState<"all" | NodeKind>("all");
  const [matches, setMatches] = useState<RoutedMatch<NetworkNode>[]>([]);
  const [routing, setRouting] = useState(false);
  const [hasRouted, setHasRouted] = useState(false);
  const [activityOpen, setActivityOpen] = useState(false);
  const t = messages[locale];
  const kinds = kindLabels[locale];
  const connections = connectionLabels[locale];
  const events = activityEvents[locale];

  useEffect(() => {
    if (!detectLocale) {
      applyDocumentLocale(initialLocale);
      return;
    }
    const saved = readStoredLocale(getLocaleStorage());
    const detected: Locale = saved
      ? saved
      : navigator.language.toLowerCase().startsWith("zh") ? "zh-CN" : "en";
    const timer = window.setTimeout(() => {
      setLocale(detected);
      applyDocumentLocale(detected);
      window.history.replaceState(null, "", detected === "en" ? "/en" : "/");
    }, 0);
    return () => window.clearTimeout(timer);
  }, [detectLocale, initialLocale]);

  function changeLocale(next: Locale) {
    setLocale(next);
    writeStoredLocale(getLocaleStorage(), next);
    applyDocumentLocale(next);
    window.history.replaceState(null, "", next === "en" ? "/en" : "/");
  }

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
    <div className="site-shell" lang={locale}>
      <a className="skip-link" href="#route">{t.skip}</a>
      <header className="masthead">
        <a className="wordmark" href="#route"><span className="registration-mark" aria-hidden="true" />OPENFORGE</a>
        <p>{t.slogan}</p>
        <nav aria-label={t.navLabel}>
          <a href="#about">{t.navAbout}</a><a href="#network">{t.navNetwork}</a><a href="#activity">{t.navActivity}</a><a href="#connect">{t.navConnect}</a>
        </nav>
        <div className="language-switch" role="group" aria-label={t.languageLabel}>
          <button type="button" lang="zh-CN" aria-pressed={locale === "zh-CN"} onClick={() => changeLocale("zh-CN")}>中文</button>
          <button type="button" lang="en" aria-pressed={locale === "en"} onClick={() => changeLocale("en")}>EN</button>
        </div>
        <a className="source-link" href="https://github.com/zxs2010/OpenForge">{t.source}</a>
      </header>

      <main>
        <section className="workbench" id="route" aria-labelledby="route-title">
          <div className="intent-sheet">
            <div className="sheet-meta"><span>{t.intentMeta}</span><span>{t.demoMeta}</span></div>
            <h1 id="route-title">{t.hero}</h1>
            <p className="intro">{t.intro}</p>
            <form onSubmit={routeIntent}>
              <label htmlFor="summary">{t.outcomeLabel}</label>
              <textarea id="summary" name="summary" rows={4} placeholder={t.outcomeDefault} required />
              <label htmlFor="capabilities">{t.capabilitiesLabel}</label>
              <input id="capabilities" name="capabilities" placeholder="music.compose, video.generate, channel.distribute" />
              <button className="route-action" type="submit" disabled={routing}>{routing ? t.routingProgress : t.routingAction}<span aria-hidden="true">→</span></button>
              <small>{t.demoPrivacy}</small>
            </form>
          </div>

          <div className={`routing-field ${routing ? "routing" : ""} ${matches.length ? "matched" : ""} ${hasRouted ? "routed" : ""}`}>
            <div className="route-head"><span>{t.routingField}</span><span>{t.indexedNodes(nodes.length)}</span></div>
            <div className="route-stage">
              <svg viewBox="0 0 680 530" preserveAspectRatio="none" aria-hidden="true">
                <path className="trunk" d="M20 265H215" />
                {[70, 165, 265, 365, 460].map((y, index) => <path className={`branch ${activeSlots.has(index) ? "lit" : ""}`} key={y} d={`M215 265C330 265 315 ${y} 430 ${y}H665`} />)}
                <circle cx="215" cy="265" r="7" />
              </svg>
              <span className="intent-token">{t.intentToken}</span>
              <ol className="route-nodes">
                {displayedNodes.map((node, index) => {
                  const match = matches.find((candidate) => candidate.node.id === node.id);
                  return <li className={`${match ? "lit" : ""} slot-${displayedSlots[index] + 1}`} key={node.id}>
                    <strong>{nodeNames[locale][node.id] ?? node.name}</strong><small>{match ? `${match.reasons.join(", ")} · ` : ""}{kinds[node.kind]} · {connections[node.connection]}</small>
                  </li>
                })}
              </ol>
              {!hasRouted && !routing && <p className="ready"><strong>{t.readyTitle}</strong><span>{t.readyBody}</span></p>}
              {hasRouted && !matches.length && <p className="ready empty"><strong>{t.noRouteTitle}</strong><span>{t.noRouteBody}</span></p>}
            </div>
            <div className="route-result" aria-live="polite">
              {routing ? <p>{t.comparing}</p> : matches.length ? <><p><strong>{t.compatibleNodes(matches.length)}</strong><span>{t.matchExplanation(matches[0].reasons.join(", "), hiddenMatchCount)}</span></p><button type="button" onClick={() => setActivityOpen(true)}>{t.openActivity}</button></> : hasRouted ? <p><strong>{t.noCapability}</strong><span>{t.noCapabilityBody}</span></p> : <p><strong>{t.connectionFirst}</strong><span>{t.connectionFirstBody}</span></p>}
            </div>
          </div>

          <aside className="ledger" id="activity">
            <div className="sheet-meta"><span>{t.activityMeta}</span><span className="stamp">{t.active}</span></div>
            <h2>{t.activityTitle}</h2>
            <p>{t.activityBody}</p>
            <dl><div><dt>{t.participants}</dt><dd>3</dd></div><div><dt>{t.events}</dt><dd>{events.length}</dd></div></dl>
            <ol>{events.map(([title, message]) => <li key={title}><strong>{title}</strong><span>{message}</span></li>)}</ol>
            <a href="https://github.com/zxs2010/OpenForge">{t.inspectSource}</a>
          </aside>
        </section>

        <section className="manifesto" id="about" aria-labelledby="about-title">
          <div className="manifesto-thesis">
            <h2 id="about-title">{t.aboutTitle}</h2>
            <p className="manifesto-lead">{t.manifestoLead}</p>
            <p>{t.manifestoBody}</p>
            <p>{t.manifestoClose}</p>
          </div>
          <div className="content-spectrum">
            <h3>{t.spectrumTitle}</h3>
            <ol>
              <li><span>{t.fieldWrite}</span><strong>{t.fieldWriteContent}</strong></li>
              <li><span>{t.fieldSound}</span><strong>{t.fieldSoundContent}</strong></li>
              <li><span>{t.fieldMotion}</span><strong>{t.fieldMotionContent}</strong></li>
              <li><span>{t.fieldPublish}</span><strong>{t.fieldPublishContent}</strong></li>
              <li><span>{t.fieldExplore}</span><strong>{t.fieldExploreContent}</strong></li>
            </ol>
            <p>{t.spectrumClose}</p>
          </div>
        </section>

        {activityOpen && <section className="draft-activity" aria-live="polite">
          <div><span>{t.draftMeta}</span><h2>{t.draftTitle}</h2><p>{t.draftBody}</p></div>
          <div className="draft-participants">{matches.map((match) => <span key={match.node.id}>{nodeNames[locale][match.node.id] ?? match.node.name} / {kinds[match.node.kind]}</span>)}</div>
          <a href="https://github.com/zxs2010/OpenForge/issues/new">{t.continueGithub}</a>
        </section>}

        <section className="network" id="network" aria-labelledby="network-title">
          <div className="section-head"><div><h2 id="network-title">{t.networkTitle}</h2><p>{t.networkBody}</p></div><div className="counts"><span><strong>{networkCounts.nodes}</strong> {t.nodeUnit}</span><span><strong>{networkCounts.providers}</strong> {t.providerUnit}</span><span><strong>{networkCounts.connected}</strong> {t.connectedUnit}</span></div></div>
          <div className="filters" role="group" aria-label={t.filterLabel}>
            {(["all", "ai", "project", "provider", "channel"] as const).map((kind) => <button key={kind} type="button" aria-pressed={filter === kind} onClick={() => setFilter(kind)}>{kind === "all" ? t.allNodes : kinds[kind]}</button>)}
          </div>
          <div className="node-table" role="table" aria-label={t.indexLabel}>
            <div className="node-row headings" role="row"><span role="columnheader">{t.node}</span><span role="columnheader">{t.kind}</span><span role="columnheader">{t.capabilities}</span><span role="columnheader">{t.connection}</span></div>
            {filteredNodes.map((node) => <div className="node-row" role="row" key={node.id}>
              <span className="node-name" role="cell">{node.url ? <a href={node.url}>{nodeNames[locale][node.id] ?? node.name}</a> : <strong>{nodeNames[locale][node.id] ?? node.name}</strong>}<small>{nodeSummaries[locale][node.id] ?? node.summary}</small></span>
              <span className="kind" role="cell">{kinds[node.kind]}</span>
              <span className="caps" role="cell">{node.capabilities.map((capability) => <code key={capability}>{capability}</code>)}</span>
              <span className="connection" role="cell"><StatusDot status={node.connection} />{connections[node.connection]}</span>
            </div>)}
          </div>
        </section>

        <section className="connect" id="connect">
          <div><h2>{t.connectTitle}</h2><p>{t.connectBody}</p></div>
          <div className="join-sheet"><span>{t.claimMeta}</span><h3>{t.claimTitle}</h3><p>{t.claimBody}</p><a href="https://github.com/zxs2010/OpenForge/issues/new?template=connect-node.yml">{t.proposeNode} <span aria-hidden="true">→</span></a></div>
        </section>

        <section className="protocol">
          <div><h2>{t.protocolTitle}</h2><p>{t.protocolBody}</p></div>
          <pre><code><b>POST</b> /api/v1/intents{"\n"}{"{"}{"\n"}  &quot;summary&quot;: &quot;{t.protocolSummary}&quot;,{"\n"}  &quot;desired_capabilities&quot;: [{"\n"}    &quot;music.compose&quot;,{"\n"}    &quot;video.generate&quot;{"\n"}  ]{"\n"}{"}"}</code></pre>
        </section>
      </main>

      <footer><a className="wordmark" href="#route">OPENFORGE</a><p>{t.footerMeta}</p><a href="https://github.com/zxs2010/OpenForge">{t.buildWithUs}</a></footer>
    </div>
  );
}
