# OpenForge Gateway v0.1

**Status:** Experimental reference implementation

**Scope:** Node discovery, intent matching, and community activities

Gateway v0.1 is the layer above the provider Job protocol. An Activity can
coordinate several people, AI systems, projects, channels, or provider Jobs.

## Run locally

```bash
openforge serve --host 127.0.0.1 --port 8787 \
  --database .openforge/openforge.db
```

The default is intentionally local. V0.1 does not ship public authentication or
multi-tenant authorization. Do not expose its write endpoints directly to the
internet; use a trusted reverse proxy and explicit access policy.

## HTTP resources

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Process health. |
| `GET` | `/api/v1/meta` | Node and protocol version. |
| `GET` | `/api/v1/network` | Nodes, kind counts, and connection-state counts. |
| `POST` | `/api/v1/nodes` | Claim an independently operated node. |
| `GET` | `/api/v1/intents` | List submitted intents. |
| `POST` | `/api/v1/intents` | Submit and immediately match an intent. |
| `POST` | `/api/v1/intents/{id}/activate` | Idempotently open its Activity. |
| `GET` | `/api/v1/activities` | List Activity summaries. |
| `GET` | `/api/v1/activities/{id}` | Read participants and timeline. |
| `POST` | `/api/v1/activities/{id}/events` | Append progress and optionally move state. |

All writes require `Content-Type: application/json`, accept no more than 64 KiB,
and reject unknown Host headers or browser requests from a different origin.
The local page reads a per-process write token from `/api/v1/meta` and sends it
as `X-OpenForge-Token`; non-browser clients without an `Origin` header can call
the loopback API directly. This is CSRF and DNS-rebinding protection for a
single-user reference node, not public authentication. Error responses use:

```json
{"error":{"code":"invalid_request","message":"summary is required"}}
```

## Submit an intent

```http
POST /api/v1/intents
Content-Type: application/json

{
  "summary": "Create a 15-second AI comic-drama trailer",
  "desired_capabilities": ["video.generate"]
}
```

The response contains the stored Intent and ordered Matches. Every Match names
the capability that produced it. Connection evidence is used only as a
deterministic tie-breaker; it is not a reputation score.

When capability labels are omitted, V0.1 applies a small visible keyword map.
This is a bootstrap router, not an LLM quality claim. Future routers can compete
behind the same Intent and Match records.

## Activate an Activity

`POST /api/v1/intents/{id}/activate` creates one Activity per Intent. Repeating
the call returns the same Activity. Matches become proposed participants in
their ranked order; the Activity begins in `recruiting`.

```text
draft → recruiting → planned → active → awaiting_review → completed
  └───────────────────────────────→ cancelled / failed
```

Events are append-only semantic records such as `activity.opened`,
`artifact.published`, or `review.requested`. Internal diagnostic logs are not
Activity Events.

## Connect an external repository

An external system first appears as a Node:

```json
{
  "name": "Independent Comic Drama System",
  "kind": "provider",
  "summary": "Produces comic-drama video from a structured brief.",
  "capabilities": ["video.generate", "comic-drama.produce"],
  "origin_url": "https://github.com/owner/project"
}
```

This claim does not execute the system. A provider connector then implements
the five operations in [Protocol v0.1](protocol-v0.1.md): estimate, create,
status, cancel, and result. The external repository remains independently
installed and licensed.

## Seed evidence

The reference node idempotently seeds:

- the OpenForge project, router, and GitHub channel;
- Activity 001;
- the four public provider manifests in `providers/`.

Only MoneyPrinterTurbo is seeded as `connected`; catalog candidates are
`imported`. These are integration facts, not quality rankings.
