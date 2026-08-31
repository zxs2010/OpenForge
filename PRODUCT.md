# OpenForge Product Truth

## Product

OpenForge is an open connection layer for creative production. It helps a real
need find compatible people, AI agents, projects, channels, skills, providers,
and compute, then turns those connections into a visible activity with an
auditable outcome.

Its unique mechanism is a public flow from **node → intent → match → activity →
receipt**. OpenForge coordinates the flow; independent systems keep their own
repositories, identities, interfaces, and business models.

## People and situations

- A requester arrives with an outcome but does not know which tools or people
  can deliver it.
- A person, AI agent, project, channel, or provider wants to expose a useful
  capability without moving into a proprietary marketplace.
- A small production team needs to prove that an open network can complete a
  real project and show who contributed what.
- A community operator needs a shared activity room rather than another static
  directory of links.

## First release promise

A visitor can immediately understand what OpenForge connects, inspect the live
network, register an external node, submit a need, see compatible nodes, open an
activity, and record progress and results. The same operations are available to
AI systems through a versioned HTTP API.

Activity 001 is OpenForge building and opening OpenForge itself. The first
external production proof will connect the founder's independently hosted AI
comic-drama system through the same node and connector boundary used by every
other participant.

## Positioning

OpenForge is not a video generator, a Skill store, an Agent store, a token, or a
centrally controlled marketplace. Those can emerge as nodes or community
projects later. The first product is the shared connection and activity layer.

## Technical commitments

- Web reference node plus a stable, machine-readable API.
- Python 3.10+, SQLite, and browser-native HTML/CSS/JavaScript for a small,
  inspectable first implementation with no runtime dependencies.
- Open interfaces, replaceable connectors, portable data, and honest connection
  states (`imported`, `claimed`, `connected`, `verified`).
- Default local binding for the reference server; public deployment requires a
  trusted reverse proxy and access policy.
- No automatic settlement, token economics, or unverifiable quality claims in
  V1.

## Brand and voice

**Name:** OpenForge

**Line:** Open production for everyone.
**Voice:** direct, collaborative, concrete, and technically honest. Explain the
opportunity in human language; expose protocol detail when it helps someone
connect.

The experience should feel like an active civic exchange for production—not a
corporate SaaS dashboard and not a speculative crypto market. It should show the
network working before it explains the network.

## Evidence and unknowns

Current evidence includes the provider protocol, a Python SDK, a working
MoneyPrinterTurbo adapter, and a catalog containing MoneyPrinterTurbo,
OpenMontage, ComfyUI, and VideoLingo. These entries prove discovery and adapter
boundaries; they do not yet prove demand, delivery quality, or network effects.

The first release is validated only when a real activity attracts participants,
produces an artifact or decision, and records a useful receipt. Pricing,
reputation, governance, and marketplace structure remain open questions.

## Product principles

1. Start from needs and activities, not inventories of tools.
2. Show connection status and evidence honestly.
3. Let humans and AI use the same network through different interfaces.
4. Keep execution systems independent and replaceable.
5. Make every activity legible: purpose, participants, events, artifacts, and
   outcome.
6. Build the smallest loop we can run ourselves in the real world.
