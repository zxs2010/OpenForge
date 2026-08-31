# Contributing to OpenForge

Thank you for helping build an open production network. OpenForge is in an
early design phase, so contributions that clarify real workflows and improve
interoperability are especially useful.

## Good first contributions

- Propose a real node with capability and connection evidence.
- Run a small Activity and document its participants, artifacts, and outcome.
- Document a real production workflow and its constraints.
- Propose or review a provider capability or job schema.
- Add a small, provider-neutral example.
- Improve terminology, error semantics, security guidance, or accessibility.

## Before opening a change

For a broad protocol or architecture change, open an issue first. Describe the
problem, the users affected, alternatives considered, compatibility impact, and
how the proposal could be tested. Small documentation fixes can go directly to
a pull request.

## Contribution workflow

1. Fork the repository and create a focused branch.
2. Keep each change small enough to review independently.
3. Add or update examples and tests when behavior changes.
4. Update the relevant specification text and note compatibility concerns.
5. Open a pull request that explains the problem and the chosen approach.

## Adding a community provider

1. Add `providers/<slug>/provider.json` with the upstream GitHub repository,
   pinned release or commit, license, capabilities, and honest operation status.
2. Add a short README describing the boundary between OpenForge and upstream.
3. Implement the `ProductionProvider` interface without copying upstream code.
4. Use recorded, secret-free responses for offline adapter tests.
5. Keep real-provider tests opt-in and read credentials only from environment
   variables.
6. Document missing cancellation, estimates, idempotency, or receipts rather
   than simulating support.

An adapter can be useful before it is fully conformant, but its limitations
must remain machine-readable in the provider manifest.

## Proposing any network node

Use the **Connect a node** issue template for a person, AI agent, project,
skill, provider, compute resource, or channel. Name the public operator or
source, capability labels, connection evidence, and interface when one exists.
Do not include API keys, private data, or an unverified quality claim.

Discovery creates an `imported` record. An operator claim, working connector,
and reviewed evidence are separate steps; contributions should not collapse
them into one “active” label.

Protocol proposals should use normative language only where conformance can be
tested. New fields should be optional or versioned unless a breaking version is
being proposed.

## Review expectations

Maintainers review changes for clarity, provider neutrality, security,
portability, and backward compatibility. A proposal may need more than one
implementation before it is considered stable.

All participation must follow the [Code of Conduct](CODE_OF_CONDUCT.md).
By submitting a contribution, you agree that it may be distributed under the
project's [Apache License 2.0](LICENSE).
