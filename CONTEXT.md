# OpenForge Domain Context

This document defines the shared product vocabulary. These terms name domain
concepts; they do not prescribe storage, transport, or user-interface details.

## Core Terms

### Node

- **Definition:** Any discoverable entity that can request, contribute,
  distribute, or execute work in the network.
- **Examples:** A person, AI agent, project, skill, production provider, compute
  resource, distribution channel, creator, aesthetic reviewer, musician,
  scriptwriter, or AI content system.
- **Related:** Connector, Capability, Participant, Network Index.
- **Avoid:** Resource (too narrow), account (implies ownership or login), vendor
  (excludes people and community projects).

### Connector

- **Definition:** A versioned boundary that lets an independently operated node
  describe itself or exchange work with OpenForge.
- **Examples:** Provider manifest import, HTTP production adapter, future agent
  protocol bridge.
- **Related:** Node, Capability, Job.
- **Avoid:** Plugin when referring to the protocol boundary; a plugin is only one
  possible implementation.

### Capability

- **Definition:** A stable label for something a node can contribute or perform.
- **Examples:** `video.generate`, `script.write`, `music.compose`,
  `social.publish`, `mtv.produce`, `channel.distribute`.
- **Related:** Node, Intent, Match.
- **Avoid:** Skill as a synonym; a Skill is a node that packages reusable
  expertise, while a Capability is what any node declares.

### Network Index

- **Definition:** The discoverable collection of nodes and their current public
  connection metadata.
- **Examples:** Connected providers, imported open-source projects, claimed human
  contributors.
- **Related:** Node, Connection Status, Match.
- **Avoid:** Marketplace; indexing does not imply pricing, ranking, or payment.

### Connection Status

- **Definition:** The evidence level of a node's relationship with the network.
- **Examples:** `imported`, `claimed`, `connected`, `verified`.
- **Related:** Node, Connector, Network Index.
- **Avoid:** Active when only a repository was discovered.

### Intent

- **Definition:** A request for an outcome, expressed in human language plus
  optional desired capabilities and constraints.
- **Examples:** “Launch OpenForge V1,” “Make a 15-second product video.”
- **Related:** Match, Activity, Capability.
- **Avoid:** Job; an Intent can require several participants and jobs.

### Content Field

- **Definition:** An open-ended label describing the kind of content an Intent
  or Activity aims to create.
- **Examples:** Story, script, music, voice, podcast, comic drama, film,
  advertising, AI MTV/MV, self-media, game, interactive narrative, virtual
  character, design.
- **Related:** Intent, Activity, Capability, Artifact.
- **Avoid:** Vertical when it implies a closed business silo; marketplace
  category when it implies that only pre-listed forms are welcome.

### Match

- **Definition:** An explainable compatibility suggestion between an Intent and
  one or more nodes.
- **Examples:** A video provider matched because it declares
  `video.generate`.
- **Related:** Intent, Node, Capability.
- **Avoid:** Assignment; a Match is a proposal until an Activity includes it.

### Activity

- **Definition:** The community's shared unit of coordinated work, with a purpose,
  participants, lifecycle, timeline, artifacts, and outcome.
- **Examples:** Activity 001: build and open OpenForge V1.
- **Related:** Intent, Participant, Event, Job, Receipt.
- **Avoid:** Project (may be a participating node), campaign (too specific), Job
  (an execution unit inside an Activity).

### Participant

- **Definition:** A node that has been included in a specific Activity with a
  stated role.
- **Examples:** Requester, coordinator, provider, reviewer, distributor.
- **Related:** Node, Activity, Contribution.
- **Avoid:** User; AI agents and external projects may also participate.

### Event

- **Definition:** An append-only statement of meaningful progress or a state
  transition inside an Activity.
- **Examples:** Participant joined, plan accepted, artifact published, review
  requested.
- **Related:** Activity, Artifact, Receipt.
- **Avoid:** Log when the record communicates product meaning rather than internal
  diagnostics.

### Job

- **Definition:** A versioned execution request sent to one production provider.
- **Examples:** Generate a video, render subtitles, run a local workflow.
- **Related:** Activity, Connector, Provider, Artifact.
- **Avoid:** Activity; one Activity may contain zero, one, or many Jobs.

### Artifact

- **Definition:** A durable output reference produced or attached during an
  Activity or Job.
- **Examples:** Script draft, music master, podcast episode, video URL, AI MTV,
  social post, repository commit, campaign brief, review document.
- **Related:** Event, Job, Receipt.
- **Avoid:** Result when referring only to a file; an outcome can also be a
  decision or verified learning.

### Receipt

- **Definition:** An auditable summary of an Activity or Job's contributors,
  artifacts, usage, costs when known, and outcome.
- **Examples:** Provider cost receipt, public activity completion record.
- **Related:** Activity, Contribution, Artifact, Job.
- **Avoid:** Payment; a Receipt records facts and may exist without money.

### Contribution

- **Definition:** A participant's declared input to an Activity, linked to
  evidence when available.
- **Examples:** Human review, GPU time, script draft, distribution placement.
- **Related:** Participant, Receipt, Artifact.
- **Avoid:** Ownership or reward; those require separate governance rules.

## Lifecycle Summaries

- **Node:** imported → claimed → connected → verified. A node can remain at any
  earlier status indefinitely; status is evidence, not a mandatory funnel.
- **Intent:** open → matched → activated → closed.
- **Activity:** draft → recruiting → planned → active → awaiting_review →
  completed. It may also become cancelled or failed.
- **Job:** queued → running → awaiting_review → succeeded, with cancellation and
  failure paths defined by Protocol v0.1.
