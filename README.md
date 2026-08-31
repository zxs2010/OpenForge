# OpenForge

**Open production for everyone.**

Public gateway: [openforge-network.wuguomi1219.chatgpt.site](https://openforge-network.wuguomi1219.chatgpt.site)

OpenForge is an open connection and activity layer for creative production. A
real need enters the network, finds compatible people, AI agents, projects,
channels, providers, skills, or compute, and becomes a visible activity with an
auditable outcome.

> 中文：OpenForge 不是又一个 AI 工具市场。它先把需求、项目、人、AI、渠道与算力连接起来，让社区围绕真实活动形成生产生态。

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

- no token or blockchain settlement;
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

Licensed under the [Apache License 2.0](LICENSE).
