# Community Validation Plan

OpenForge validates an open production community by connecting existing
projects before building replacement implementations.

## Hypothesis

An independent production tool can join OpenForge through a thin adapter. A
requester should be able to submit the same job contract to more than one tool,
observe a common lifecycle, and receive normalized artifacts and receipts
without changing the client.

## Rules

1. Upstream projects remain independently installed, licensed, and versioned.
2. Every catalog entry pins a release tag or immutable commit.
3. OpenForge adapters translate contracts; they do not copy upstream source.
4. Unsupported operations are reported explicitly.
5. A provider is `adapter-ready` only after its implemented operations pass
   offline contract tests; limitations remain visible in its manifest.
6. Real-provider tests are opt-in and must never require secrets in source code.

Full Protocol v0.1 conformance is a higher bar. It includes durable idempotency,
all lifecycle operations, receipts, and real-upstream evidence.

## First provider set

| Project | OpenForge role | Integration | Initial status |
| --- | --- | --- | --- |
| MoneyPrinterTurbo | Short-video production | HTTP API | Adapter ready |
| OpenMontage | Agentic end-to-end production | Agent + checkpoints | Candidate |
| ComfyUI | Local/hosted generation workflows | HTTP + WebSocket | Candidate |
| VideoLingo | Translation, subtitles, and dubbing | CLI | Candidate |

## Proof of openness

The first cross-provider scenario uses one request:

```json
{
  "protocol_version": "0.1",
  "request_id": "community-demo-001",
  "kind": "video.generate",
  "inputs": [
    {
      "name": "brief",
      "media_type": "text/plain",
      "value": "Create a 15-second vertical product launch video."
    }
  ],
  "parameters": {
    "duration_seconds": 15,
    "aspect_ratio": "9:16"
  }
}
```

The scenario passes when at least two independent providers can:

- accept the request without client-specific fields;
- expose normalized job state;
- return at least one verifiable video artifact;
- state whether cost is known or unavailable;
- preserve the selected upstream project and version as provenance.

Quality can differ. Interoperable control and truthful reporting are the first
community milestone.

## Adding a project

Contributors start with a `providers/<slug>/provider.json` manifest and a short
README describing the upstream boundary. An adapter then implements the five
Provider v0.1 operations and is exercised with recorded, secret-free fixtures.
