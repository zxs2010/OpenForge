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
first protocol draft, and the boundaries for future reference implementations.
No API should be considered stable yet.

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
[Protocol v0.1](docs/protocol-v0.1.md) for the first interoperability draft.

## Repository map

```text
agents/       Agent adapters and manifests
cli/          Command-line client
docs/         Vision, protocol, and design documents
examples/     End-to-end examples
providers/    Production-provider adapters
sdk/          SDKs and shared protocol types
skills/       Reusable production skills and manifests
```

## Contributing

OpenForge is at the stage where clear use cases and small, testable protocol
proposals are especially valuable. Start with [CONTRIBUTING.md](CONTRIBUTING.md)
and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
