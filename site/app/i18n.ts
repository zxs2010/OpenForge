import type { Connection } from "./routing";

export type Locale = "zh-CN" | "en";
export type NodeKind = "human" | "ai" | "project" | "provider" | "compute" | "channel";

type LocaleStorage = Pick<Storage, "getItem" | "setItem">;

export function getLocaleStorage(
  scope: { readonly localStorage: LocaleStorage } = window,
): LocaleStorage | null {
  try {
    return scope.localStorage;
  } catch {
    return null;
  }
}

export function readStoredLocale(storage: LocaleStorage | null): Locale | null {
  if (!storage) return null;
  try {
    const value = storage.getItem("openforge-locale");
    return value === "zh-CN" || value === "en" ? value : null;
  } catch {
    return null;
  }
}

export function writeStoredLocale(storage: LocaleStorage | null, locale: Locale): void {
  if (!storage) return;
  try {
    storage.setItem("openforge-locale", locale);
  } catch {
    // Persistence is optional; the current page still changes language.
  }
}

const zh = {
  metaTitle: "OpenForge — 让创作向所有人开放",
  metaDescription: "OpenForge 是面向 AI 原生内容的开放协作网络，连接需求、创作者、AI、工具、算力、项目与渠道。",
  metaSocialDescription: "带来一个剧本、音乐、影像、自媒体或下一种内容需求，让开放网络组织起协作力量。",
  skip: "跳到需求路由",
  slogan: "让创作向所有人开放。",
  navLabel: "主导航",
  navAbout: "项目介绍",
  navNetwork: "开放网络",
  navActivity: "活动 001",
  navConnect: "加入网络",
  source: "GitHub 源码",
  languageLabel: "选择网站语言",
  intentMeta: "需求 / 待路由",
  demoMeta: "公开演示",
  hero: "面向 AI 原生内容的开放协作网络。",
  intro: "把需求、创作者、AI、工具、算力与渠道组织成一次真实活动。",
  outcomeLabel: "你想完成什么",
  outcomeDefault: "创作并发布一支拥有原创歌曲的 AI 音乐视频",
  capabilitiesLabel: "所需能力（如果已经知道）",
  routingAction: "为这个需求寻找协作者",
  routingProgress: "正在读取开放网络…",
  demoPrivacy: "公开演示不会保存你输入的内容。开源节点提供完整 API。",
  routingField: "开放网络匹配区",
  indexedNodes: (count: number) => `已收录 ${count} 个节点`,
  intentToken: "需求",
  readyTitle: "等待需求",
  readyBody: "提交你想完成的结果，查看可能的协作节点。",
  noRouteTitle: "暂未找到路径",
  noRouteBody: "尝试更宽泛的能力标签，或提交缺少的节点。",
  comparing: "正在比较节点声明的能力…",
  compatibleNodes: (count: number) => `找到 ${count} 个兼容节点`,
  matchExplanation: (reasons: string, hidden: number) =>
    `主要匹配能力：${reasons}；连接证据用于处理同分结果。${hidden ? ` 当前展示前 5 个，其余 ${hidden} 个仍保留在索引中。` : ""}`,
  openActivity: "发起协作活动",
  noCapability: "尚无节点声明所需能力",
  noCapabilityBody: "调整能力标签，或邀请缺少的贡献者加入网络。",
  connectionFirst: "先连接，再交易",
  connectionFirstBody: "V1 不提供定价，也不进行封闭市场排名。",
  activityMeta: "活动 001",
  active: "进行中",
  activityTitle: "开放并验证 OpenForge V1",
  activityBody: "第一个活动就是建设这个网络本身。这是一份真实项目记录，不是对网络效应的夸大宣传。",
  participants: "参与节点",
  events: "进展记录",
  inspectSource: "查看项目源码 →",
  aboutTitle: "OpenForge 是什么？",
  manifestoLead: "让每一个有想法的人，都能组织起自己的创作力量。",
  manifestoBody: "它不是又一个 AI 工具商店，也不只是一套视频软件。你带来一个想法或任务，OpenForge 帮它找到可能需要的人、AI、项目、工具、算力与渠道，再把这些连接组织成一次看得见、可参与、可追踪的真实活动。",
  manifestoClose: "带来一个真实需求，让开放网络组织起协作力量。每个参与者都保留自己的身份、工具、仓库与商业模式。",
  spectrumTitle: "剧本、音乐、影像、媒体，以及下一种内容。",
  fieldWrite: "写作",
  fieldWriteContent: "剧本 · 故事 · 分镜 · 世界观",
  fieldSound: "声音",
  fieldSoundContent: "音乐 · 配乐 · 声音 · 播客",
  fieldMotion: "影像",
  fieldMotionContent: "漫剧 · 电影 · 广告 · AI MTV / MV",
  fieldPublish: "发布",
  fieldPublishContent: "自媒体 · 短视频 · 图文 · 频道",
  fieldExplore: "探索",
  fieldExploreContent: "游戏 · 互动内容 · 虚拟角色 · 新形式",
  spectrumClose: "这些只是起点，不是边界。只要人、AI 或工具能够参与创作，它就值得进入这个网络。",
  draftMeta: "活动草案 · 公开演示",
  draftTitle: "这个需求现在有了协作空间。",
  draftBody: "下一步是邀请匹配的参与者、记录产物，并完成一份公开活动凭证。",
  continueGithub: "前往 GitHub 继续这个活动",
  networkTitle: "一个索引，连接独立节点。",
  networkBody: "“已收录”只表示被发现；“已连接”才表示存在可工作的接口。OpenForge 会始终公开这一区别。",
  nodeUnit: "个节点",
  providerUnit: "个生产节点",
  connectedUnit: "个已连接",
  filterLabel: "筛选开放网络",
  allNodes: "全部节点",
  indexLabel: "OpenForge 开放网络索引",
  node: "节点",
  kind: "类型",
  capabilities: "能力标签",
  connection: "连接状态",
  connectTitle: "保留你的仓库，加入开放网络。",
  connectBody: "你的 AI 系统、项目、渠道、算力服务或个人创作实践仍然保持独立。告诉社区你能贡献什么，并提供可以验证的接口或证据。",
  claimMeta: "节点 / 认领",
  claimTitle: "连接下一个真实节点",
  claimBody: "提交一份结构化 GitHub 申请。社区可以审查能力、证据、许可证与连接方式，无需把你的项目复制进 OpenForge。",
  proposeNode: "提交节点申请",
  protocolTitle: "人类从协作空间进入，AI 通过同一套动作接入。",
  protocolBody: "网页与 API 共享同一个模型：查看节点、提交需求、发起活动，并追加有意义的进展记录。",
  protocolSummary: "创作一支 AI 音乐视频",
  footerMeta: "Apache-2.0 · 协议 v0.1 · 参考节点 v0.1.0",
  buildWithUs: "一起建设 OpenForge",
};

type MessageShape<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => unknown
    ? (...args: A) => string
    : string;
};

const en: MessageShape<typeof zh> = {
  metaTitle: "OpenForge — Open production for everyone",
  metaDescription: "OpenForge is an open collaboration network for AI-native content, connecting needs, creators, AI, tools, compute, projects, and channels.",
  metaSocialDescription: "Bring a need for scripts, music, video, self-media, or the next creative format. Let the open network assemble.",
  skip: "Skip to intent routing",
  slogan: "Open production for everyone.",
  navLabel: "Primary navigation",
  navAbout: "About",
  navNetwork: "Network",
  navActivity: "Activity 001",
  navConnect: "Connect",
  source: "GitHub source",
  languageLabel: "Choose website language",
  intentMeta: "INTENT / OPEN",
  demoMeta: "PUBLIC DEMO",
  hero: "The open network for AI-native content.",
  intro: "Turn needs, creators, AI, tools, compute, and channels into real creative activities.",
  outcomeLabel: "What do you want to make?",
  outcomeDefault: "Create and release an AI music video with an original song",
  capabilitiesLabel: "Capabilities, if known",
  routingAction: "Find collaborators for this need",
  routingProgress: "Reading the open network…",
  demoPrivacy: "This public demo does not save your text. The open-source node provides the full API.",
  routingField: "OPEN NETWORK ROUTING FIELD",
  indexedNodes: (count: number) => `${count} indexed nodes`,
  intentToken: "INTENT",
  readyTitle: "Ready to route",
  readyBody: "Submit an outcome to reveal compatible nodes.",
  noRouteTitle: "No route yet",
  noRouteBody: "Try a broader capability or propose the missing node.",
  comparing: "Comparing declared capabilities…",
  compatibleNodes: (count: number) => `${count} compatible ${count === 1 ? "node" : "nodes"}`,
  matchExplanation: (reasons: string, hidden: number) =>
    `Matched on ${reasons}; connection evidence breaks ties.${hidden ? ` Showing the first 5; ${hidden} additional ${hidden === 1 ? "match remains" : "matches remain"} indexed.` : ""}`,
  openActivity: "Open an activity",
  noCapability: "No compatible node is declared",
  noCapabilityBody: "Adjust the capability label or connect the missing contributor.",
  connectionFirst: "Connection before transaction",
  connectionFirstBody: "V1 has no pricing or closed-market ranking.",
  activityMeta: "ACTIVITY 001",
  active: "ACTIVE",
  activityTitle: "Open and validate OpenForge V1",
  activityBody: "The first activity is building the network itself. This is a live project record, not a network-effect claim.",
  participants: "Participants",
  events: "Events",
  inspectSource: "Inspect the source →",
  aboutTitle: "What is OpenForge?",
  manifestoLead: "Give every person with an idea the power to assemble a creative force.",
  manifestoBody: "OpenForge is not another AI tool store, and it is not only video software. Bring an idea or task; the network finds people, AI, projects, tools, compute, and channels, then organizes those connections into a visible, participatory, traceable activity.",
  manifestoClose: "Bring a real need. Let the open network assemble. Every participant keeps their identity, tools, repository, and business model.",
  spectrumTitle: "Scripts. Music. Video. Media. Whatever comes next.",
  fieldWrite: "WRITE",
  fieldWriteContent: "Scripts · stories · storyboards · worlds",
  fieldSound: "SOUND",
  fieldSoundContent: "Music · scores · voice · podcasts",
  fieldMotion: "MOTION",
  fieldMotionContent: "Comic drama · film · advertising · AI MTV / MV",
  fieldPublish: "PUBLISH",
  fieldPublishContent: "Social media · short video · posts · channels",
  fieldExplore: "EXPLORE",
  fieldExploreContent: "Games · interactive content · virtual characters · new forms",
  spectrumClose: "Starting points, not limits. If people, AI, or tools can help make it, it belongs in the network.",
  draftMeta: "ACTIVITY DRAFT · PUBLIC DEMO",
  draftTitle: "Your need now has a collaboration space.",
  draftBody: "Next, invite matched participants, record artifacts, and complete a public activity receipt.",
  continueGithub: "Continue this activity on GitHub",
  networkTitle: "One index. Independent nodes.",
  networkBody: "Imported means discovered. Connected means a working interface exists. OpenForge keeps that distinction visible.",
  nodeUnit: "nodes",
  providerUnit: "providers",
  connectedUnit: "connected",
  filterLabel: "Filter the open network",
  allNodes: "All nodes",
  indexLabel: "OpenForge network index",
  node: "Node",
  kind: "Kind",
  capabilities: "Capabilities",
  connection: "Connection",
  connectTitle: "Keep your repository. Join the network.",
  connectBody: "Your AI system, project, channel, compute service, or human practice stays independent. Tell the community what it contributes and which interface or evidence proves it.",
  claimMeta: "NODE / CLAIM",
  claimTitle: "Connect the next real node",
  claimBody: "Open a structured GitHub request. The community can review capabilities, evidence, licenses, and connectors without copying your project into OpenForge.",
  proposeNode: "Propose a node",
  protocolTitle: "Humans enter through the room. AI enters through the same verbs.",
  protocolBody: "The browser and API share one model: list nodes, submit an intent, activate an activity, and append meaningful events.",
  protocolSummary: "Create an AI music video",
  footerMeta: "Apache-2.0 · Protocol v0.1 · Reference node v0.1.0",
  buildWithUs: "Build OpenForge with us",
};

export const messages = { "zh-CN": zh, en } as const;

export const kindLabels: Record<Locale, Record<NodeKind, string>> = {
  "zh-CN": { human: "个人", ai: "AI", project: "项目", provider: "生产节点", compute: "算力", channel: "渠道" },
  en: { human: "Human", ai: "AI", project: "Project", provider: "Provider", compute: "Compute", channel: "Channel" },
};

export const connectionLabels: Record<Locale, Record<Connection, string>> = {
  "zh-CN": { imported: "已收录", claimed: "已认领", connected: "已连接", verified: "已验证" },
  en: { imported: "Imported", claimed: "Claimed", connected: "Connected", verified: "Verified" },
};

export const nodeSummaries: Record<Locale, Record<string, string>> = {
  "zh-CN": {
    "ai.openforge-router": "提供可解释的需求与能力匹配。",
    "project.openforge": "面向 AI 原生内容的开放协作网络。",
    "channel.openforge-github": "公开源码与社区贡献入口。",
    "community.moneyprinter-turbo": "已经可以运行的视频生产适配器。",
    "community.comfyui": "已收录的社区生产节点候选。",
    "community.openmontage": "已收录的社区视频工作流候选。",
    "community.videolingo": "已收录的视频本地化节点候选。",
  },
  en: {
    "ai.openforge-router": "Explainable intent-to-capability matching.",
    "project.openforge": "Open collaboration network for AI-native content.",
    "channel.openforge-github": "Public source and contribution channel.",
    "community.moneyprinter-turbo": "Runnable video-provider adapter.",
    "community.comfyui": "Imported community provider candidate.",
    "community.openmontage": "Imported community video-workflow candidate.",
    "community.videolingo": "Imported localization provider candidate.",
  },
};

export const nodeNames: Record<Locale, Record<string, string>> = {
  "zh-CN": {
    "ai.openforge-router": "OpenForge 路由器",
  },
  en: {
    "ai.openforge-router": "OpenForge Router",
  },
};

export const activityEvents: Record<Locale, string[][]> = {
  "zh-CN": [
    ["范围确认", "节点 → 需求 → 匹配 → 活动 → 凭证，确定为 V1 的核心循环。"],
    ["节点收录", "首批独立生产项目进入公开索引。"],
    ["入口开放", "人类与 AI 入口开始共享同一套产品语言。"],
  ],
  en: [
    ["Scope accepted", "Node → intent → match → activity → receipt is fixed as the V1 loop."],
    ["Nodes imported", "The first independent production projects entered the public index."],
    ["Gateway opened", "Human and AI entry points now share the same product vocabulary."],
  ],
};
