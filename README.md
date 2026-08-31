# OpenForge

**Open production for everyone. 让每一个有想法的人，都能组织起自己的创作力量。**

[进入 OpenForge](https://openforge-network.wuguomi1219.chatgpt.site) · [English overview](#english-overview)

> **首批建设者招募中 / Founding Builders wanted:** 帮我们连接第一个真实
> AI 生产节点，建设开放协议、Agent、Provider 和贡献凭证。
> [阅读中英文招募说明](docs/call-for-builders-001.md) ·
> [加入招募讨论](https://github.com/zxs2010/OpenForge/discussions/5)

## 让下一代内容工业，向所有人开放

我们相信，下一个时代的内容工业，不应该只属于好莱坞、4A 广告公司和少数拥有预算、渠道与技术壁垒的机构。

一个普通人、一位有审美判断的人、一个独立创作者、一台本地 GPU、一个 AI Agent、一套开源工作流，都应该能够围绕一个真实需求临时结成团队：一起写、一起做、一起审、一起发布，并留下每一份贡献的证据。

**OpenForge 就是为此而生的开放协作网络。**

它不是又一个 AI 工具商店，也不只是一套 AI 视频软件。你带来一个想法或任务，OpenForge 帮它找到可能需要的人、AI、项目、工具、算力与渠道，再把这些连接组织成一次看得见、可参与、可追踪的真实活动。

```text
一个真实需求 → 找到合适的创作力量 → 共同完成 → 公开结果与贡献
```

这里可以发生的，不只有视频：

- AI 剧本、故事、分镜与世界观；
- AI 音乐、配乐、声音、播客与虚拟歌手；
- AI 漫剧、短剧、电影、广告与动画；
- AI MTV / MV、视觉专辑与跨媒体作品；
- AI 自媒体、短视频、图文、直播与频道内容；
- AI 游戏、互动叙事、虚拟角色与数字体验；
- AI 设计、品牌、电商内容，以及下一种还没有被命名的创作形式。

只要 AI 或工具能够参与创作，它就可以进入 OpenForge 寻找合作。你不必是传统意义上的“艺术家”：提出好问题、提供审美样本、做出判断、贡献渠道、运行算力、完善工具，都是创作的一部分。

我们想和社区一起证明一件事：**当创作资源可以被开放连接，每一个人都有机会组织起过去只有大型工作室才能拥有的生产能力。**

### 现在就加入

- **你有需求：** 提交一个真正想完成的作品或任务。
- **你有审美：** 带来参考、判断、选择与人类反馈。
- **你有 AI 或工具：** 声明它能做什么，用开放接口接入活动。
- **你有算力或渠道：** 帮作品跑出来、发出去、找到受众。
- **你在建项目：** 保留自己的仓库、许可与商业模式，作为独立节点加入网络。

OpenForge 仍处在第一代。我们不会假装生态已经形成；我们会把每一次真实合作、每一个产物和每一份贡献都记录下来，从最小的可运行循环开始，把它一起做成现实。

## English overview

OpenForge is an open collaboration network for AI-native content. A real need
enters the network, finds compatible people, AI agents, projects, tools,
compute, and distribution channels, then becomes a visible activity with an
auditable outcome.

It is not limited to video. Scripts, music, comic drama, film, advertising,
AI music videos, self-media, podcasts, games, design, and new tool-assisted
formats all belong—as examples, never as a closed taxonomy.

> Bring a need. The network assembles.

## OpenForge V1

The first generation is runnable now. It includes:

- a browser gateway for people;
- a versioned HTTP API for AI and external systems;
- a SQLite network index with honest connection states;
- explainable intent-to-capability matching;
- Activity Rooms with participants and append-only progress events;
- a provider-neutral job SDK and the first real video adapter;
- a public gateway under `site/` and a structured GitHub node-proposal flow.

Activity 001 is OpenForge opening and validating OpenForge itself. It is seeded
as a real activity record rather than presented as proof of network effects.

## Run the complete local node

Python 3.10 or newer is required. The runtime has no third-party dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
openforge serve
```

Then open [http://127.0.0.1:8787](http://127.0.0.1:8787).

The default server binds only to your computer and stores state in
`.openforge/openforge.db`. Put authentication and a trusted reverse proxy in
front of it before exposing write operations to the internet.

## The first loop

```text
Connector → Network Index → Intent Router → Activity → Receipt
```

1. A **Node** declares what it can contribute and shows its current connection
   evidence.
2. An **Intent** describes the desired outcome in plain language and optional
   capability labels.
3. A **Match** explains which declared capabilities align; it does not silently
   assign work.
4. Activating the intent opens an **Activity** with participants and a public
   timeline.
5. Provider **Jobs**, artifacts, review, distribution, and receipts can join the
   activity without becoming the platform's only purpose.

The product vocabulary is defined in [CONTEXT.md](CONTEXT.md), the product
commitments in [PRODUCT.md](PRODUCT.md), and the V1 gateway contract in
[docs/gateway-v0.1.md](docs/gateway-v0.1.md).

## Connect an independent project

Your system does not need to live in this repository. Start by proposing a node
through the GitHub issue template or call the local API:

```bash
curl -X POST http://127.0.0.1:8787/api/v1/nodes \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Independent Comic Drama System",
    "kind": "provider",
    "summary": "Produces AI comic-drama video from a structured brief.",
    "capabilities": ["video.generate", "comic-drama.produce"],
    "origin_url": "https://github.com/owner/project"
  }'
```

This creates a `claimed` node. A working connector can later move it to
`connected`; community-reviewed evidence can move it to `verified`. OpenForge
never labels a discovered repository as integrated without evidence.

## Provider jobs remain portable

The existing production-provider layer remains part of V1:

```bash
openforge providers list
openforge providers inspect moneyprinter-turbo

openforge jobs create \
  --provider moneyprinter-turbo \
  --request-id community-demo-001 \
  --brief "Create a 15-second vertical product launch video" \
  --aspect-ratio 9:16 \
  --duration 15
```

MoneyPrinterTurbo is adapter-ready. OpenMontage, ComfyUI, and VideoLingo are
indexed as candidates until their connector operations pass tests. See
[Protocol v0.1](docs/protocol-v0.1.md) for the provider-job contract.

## Architecture

```text
Human browser ─┐
               ├─> OpenForge Gateway ─> Network Index (SQLite)
AI / API ──────┘          │                    │
                          └─> Intent Router ───┘
                                      │
                                      v
                                Activity Room
                                      │
                         Jobs / artifacts / review
                                      │
                                      v
                                   Receipt
```

The Python reference node is deliberately small and inspectable. External
systems connect through manifests and adapters instead of becoming hard-coded
dependencies.

## Repository map

```text
sdk/python/openforge/  Domain, persistence, router, API server, provider SDK
sdk/python/openforge/web/  Complete local community gateway
site/                  Public, read-safe project entrance
providers/             Independent provider manifests and adapters
docs/                  Vision and protocol documents
tests/                 Domain, API, CLI, adapter, and conformance tests
skills/ agents/        Future community-owned node categories
examples/              End-to-end examples
```

## What V1 intentionally does not do

- no token or blockchain settlement—see
  [Verifiable Without Blockchain v0.1](docs/verifiable-without-blockchain-v0.1.md);
- no automatic payment or reputation score;
- no centrally curated Skill or Agent marketplace;
- no claim that imported projects are connected;
- no anonymous public mutation of the hosted project entrance.

Those choices keep the first validation focused: can we complete real work
through an open connection loop?

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Node proposals, real-world activities,
connector evidence, and small testable protocol improvements are especially
valuable now.

Substantial early contributions may be recognized through the
[OpenForge Founding Contributor Program v0.1](docs/founding-contributor-program-v0.1.md).
The program provides permanent evidence-based attribution, a documented
Contributor → Reviewer → Maintainer path, funded bounties only when money is
confirmed, and separately agreed compensation for real Activities. It does not
promise equity, Tokens, employment, guaranteed work, or future platform income.

See the public [Founding Contributors Ledger](FOUNDING_CONTRIBUTORS.md) or apply
with the repository's **Founding Contributor application** Issue template.

Licensed under the [Apache License 2.0](LICENSE).
