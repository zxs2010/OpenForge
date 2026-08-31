# OpenForge Vision

## The idea

Creative production is becoming a networked activity. A single request may
need a writer, a visual skill, an agent, a model API, local GPU capacity, human
review, and a delivery system. Today those parts are commonly bound together in
closed products or one-off integrations.

OpenForge aims to make the coordination layer open.

The project defines shared contracts for describing work, selecting compatible
capabilities, dispatching jobs, tracking state, returning artifacts, and
recording provenance and cost. Implementations remain free to compete on user
experience, routing, quality, models, infrastructure, and business models.

## What we are building

OpenForge is intended to become:

1. An open protocol for production jobs, capabilities, and receipts.
2. Provider interfaces that prevent orchestration from depending on one vendor.
3. Registries for reusable skills, agents, and production providers.
4. Reference SDKs and a CLI for building and testing interoperable systems.
5. A community where humans and AI systems can contribute production capacity.

OpenForge is not intended to be a single model, a single video application, a
marketplace controlled by one operator, or a promise that all creative work can
be automated.

## Design principles

### Open interfaces

Core contracts should be implementable without permission from a central
operator. Protocol text, schemas, and conformance fixtures should be public.

### Replaceable providers

Routers depend on declared capabilities, not vendor-specific behavior. A local
workflow, a hosted API, and a human production team can all be providers.

### Verifiable production

Every completed job should be able to return its inputs, outputs, state history,
provenance, usage, and price at an appropriate level of disclosure.

### Human agency

People must be able to set constraints, approve consequential actions, review
results, and stop work. Automation should make responsibility clearer, not
erase it.

### Composable capabilities

Small skills and agents should be reusable across workflows. Composition must
preserve version information and make failures attributable.

### Progressive decentralization

The first implementation may use a simple registry and router. The contracts
should not require one permanent registry, marketplace, or settlement operator.

### Sustainable participation

Cost and contribution records should make fair compensation possible without
requiring the protocol to choose a single currency or payment rail.

## First reference use case: AI video

The initial demonstration will connect an existing AI video production system
as the first provider. A request such as “create a 15-second product video” can
be decomposed, routed, produced, reviewed, and returned with a usage receipt.

This use case is demanding enough to exercise asynchronous jobs, multiple
artifacts, model and compute choices, human review, cancellation, partial
failure, and cost reconciliation. It is a reference use case, not the boundary
of the project.

## Participants

- **Requesters** define desired outcomes and constraints.
- **Routers** match work with capabilities and policies.
- **Providers** execute production work.
- **Skill authors** publish reusable transformations or expertise.
- **Agent authors** publish planning and execution participants.
- **Reviewers** approve, reject, or improve outputs.
- **Registry operators** help participants discover compatible components.

A participant can hold more than one role.

## Near-term milestones

- Validate Protocol v0.1 against one real video provider and one mock provider.
- Publish machine-readable schemas and conformance fixtures.
- Build a minimal SDK and CLI that submit and inspect jobs.
- Capture estimates and final receipts with explainable variance.
- Document human-review and cancellation paths.
- Use implementation evidence to revise the protocol before declaring stability.

## Success

OpenForge succeeds when a requester can move a production job between
independent providers with predictable behavior, understand what happened and
what it cost, and retain meaningful control over the work and its artifacts.
