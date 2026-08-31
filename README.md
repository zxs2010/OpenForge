# OpenForge

**Open production for everyone.**

OpenForge is an open protocol and reference platform for coordinating people,
AI agents, reusable skills, production providers, and compute into auditable
creative workflows.

The first reference use case is AI-assisted video production. The protocol is
intentionally media-agnostic so the same foundation can later support audio,
design, games, software, and other production work.

> 中文简介：OpenForge 希望把人、AI Agent、Skill、生产服务与算力组织成一个开放、可替换、可审计的生产网络。

## Project status

OpenForge is **pre-alpha**. The repository currently defines the vision, the
first protocol draft, a dependency-free Python SDK, a machine-readable community
provider catalog, and the first runnable adapter. No API should be considered
stable yet.

## How it fits together

```text
Production request
        |
        v
Production Router ----> Skills / Agents
        |
        v
Provider Interface
        |----> AI video system
        |----> ComfyUI or local GPU workflow
        |----> Third-party production API
        `----> Future providers
        |
        v
Result + provenance + usage receipt + human review
```

OpenForge separates orchestration from execution. A production system connects
through a provider adapter instead of becoming a permanent dependency of the
network.

## Core concepts

- **Job** — a versioned request with inputs, constraints, and lifecycle state.
- **Provider** — an adapter that estimates, accepts, tracks, cancels, and returns
  production work.
- **Skill** — a reusable capability with declared inputs and outputs.
- **Agent** — an autonomous or human-supervised participant that plans or acts.
- **Receipt** — an auditable record of usage, price, provenance, and result.

Read [the vision](docs/vision.md) for the product direction and
[Protocol v0.1](docs/protocol-v0.1.md) for the first interoperability draft. The
[community validation plan](docs/community-validation.md) explains how existing
open-source projects become providers without being copied into the core.

## Try the community catalog

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
openforge providers list
openforge providers inspect moneyprinter-turbo
```

The first catalog contains MoneyPrinterTurbo, OpenMontage, ComfyUI, and
VideoLingo. Entries pin an upstream release or immutable commit and record the
license and current adapter status.

## Run the first real adapter

Start a separately installed MoneyPrinterTurbo v1.3.5 API service, then submit
the same provider-neutral request through OpenForge:

```bash
openforge jobs create \
  --provider moneyprinter-turbo \
  --request-id community-demo-001 \
  --brief "Create a 15-second vertical product launch video" \
  --aspect-ratio 9:16 \
  --duration 15 \
  --language zh-CN
```

Use the returned task ID to inspect state and retrieve the final artifact:

```bash
openforge jobs status --provider moneyprinter-turbo --job-id TASK_ID
openforge jobs result --provider moneyprinter-turbo --job-id TASK_ID
```

The upstream API key, when enabled, is read only from the
`MONEYPRINTER_TURBO_API_KEY` environment variable.

## Repository map

```text
agents/       Agent adapters and manifests
cli/          Command-line client
docs/         Vision, protocol, and design documents
examples/     End-to-end examples
providers/    Production-provider adapters
sdk/          SDKs and shared protocol types
skills/       Reusable production skills and manifests
tests/        Contract, adapter, CLI, and security behavior tests
```

## Contributing

OpenForge is at the stage where clear use cases and small, testable protocol
proposals are especially valuable. Start with [CONTRIBUTING.md](CONTRIBUTING.md)
and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
