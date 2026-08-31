# OpenForge Protocol v0.1

**Status:** Draft
**Stability:** Experimental; breaking changes are expected
**Scope:** Provider interoperability and auditable asynchronous jobs

## 1. Purpose

This document defines the minimum contract between an OpenForge production
router and a production provider. It is transport-neutral. HTTP, local process,
queue, and in-process adapters may all implement the same operations.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY**
describe conformance requirements.

## 2. Identifiers and versioning

- Protocol versions use `major.minor` form, beginning with `0.1`.
- Provider, job, artifact, skill, and agent identifiers MUST be stable strings
  within the authority that issues them.
- Implementations MUST preserve unknown optional fields when acting as a proxy.
- Extensions SHOULD use namespaced keys such as `example.org/render_seed`.
- Breaking contract changes require a new protocol version.

## 3. Provider descriptor

A provider publishes a descriptor that a router can inspect before dispatch.

```json
{
  "protocol_version": "0.1",
  "provider": {
    "id": "example.org/video-provider-001",
    "version": "0.1.0",
    "display_name": "Example Video Provider"
  },
  "capabilities": [
    {
      "kind": "video.generate",
      "input_media_types": ["text/plain", "application/json"],
      "output_media_types": ["video/mp4"],
      "constraints": {
        "duration_seconds": {"min": 1, "max": 60},
        "aspect_ratios": ["16:9", "9:16", "1:1"]
      }
    }
  ]
}
```

The descriptor MUST state its protocol version, provider identity, provider
version, and capabilities. A provider MUST reject unsupported job kinds or
constraints before accepting a job.

## 4. Job request

```json
{
  "protocol_version": "0.1",
  "request_id": "req_01J...",
  "kind": "video.generate",
  "inputs": [
    {
      "name": "brief",
      "media_type": "text/plain",
      "value": "Create a 15-second product video."
    }
  ],
  "parameters": {
    "duration_seconds": 15,
    "aspect_ratio": "9:16"
  },
  "constraints": {
    "max_cost": {"amount": "10.00", "currency": "USD"},
    "deadline": "2026-09-01T12:00:00Z",
    "human_review_required": true
  },
  "metadata": {}
}
```

`request_id` is an idempotency key. Repeating `create_job` with the same
provider and request ID MUST return the original accepted job or an explicit
conflict; it MUST NOT silently create duplicate billable work.

Monetary amounts MUST be decimal strings, not binary floating-point numbers.
Timestamps MUST use RFC 3339 UTC form.

## 5. Provider operations

Every conforming provider implements these logical operations:

| Operation | Purpose |
| --- | --- |
| `estimate_cost(request)` | Return a non-binding estimate and assumptions. |
| `create_job(request)` | Validate and accept an idempotent job request. |
| `get_status(job_id)` | Return current state and observable progress. |
| `cancel_job(job_id)` | Request cancellation and report its outcome. |
| `get_result(job_id)` | Return artifacts, provenance, and final receipt. |

An HTTP binding may map them to `POST /estimates`, `POST /jobs`,
`GET /jobs/{job_id}`, `POST /jobs/{job_id}/cancel`, and
`GET /jobs/{job_id}/result`. Those paths are a recommendation, not a
requirement of the transport-neutral protocol.

## 6. Job lifecycle

The base states are:

```text
queued -> running -> awaiting_review -> succeeded
   |         |              |
   |         |              `-> failed
   |         `-> failed
   `-> cancelled

queued/running/awaiting_review -> cancelling -> cancelled
```

- `queued`: accepted but execution has not begun.
- `running`: execution has begun.
- `awaiting_review`: artifacts exist but required review is incomplete.
- `cancelling`: cancellation was accepted but work has not stopped.
- `cancelled`: no further production work will occur.
- `succeeded`: required artifacts and a final receipt are available.
- `failed`: the provider cannot complete the job without a new request.

`succeeded`, `failed`, and `cancelled` are terminal. Providers MAY expose more
detailed substates but MUST map them to one base state. Progress values are
advisory and MUST NOT replace state.

Cancellation is a request, not proof that underlying work stopped immediately.
The final receipt MUST include usage incurred before cancellation.

## 7. Status and errors

A status response includes the job ID, base state, provider version, creation
and update timestamps, and an optional progress object. State changes SHOULD be
append-only events with unique event IDs.

Errors use a stable machine-readable code and a safe human-readable message:

```json
{
  "error": {
    "code": "unsupported_constraint",
    "message": "The requested duration exceeds the provider limit.",
    "retryable": false,
    "details": {"field": "parameters.duration_seconds", "maximum": 60}
  }
}
```

Baseline codes are `invalid_request`, `unsupported_capability`,
`unsupported_constraint`, `authentication_failed`, `authorization_failed`,
`not_found`, `conflict`, `rate_limited`, `provider_unavailable`,
`budget_exceeded`, and `internal_error`. Providers MAY add namespaced codes.

## 8. Result and artifacts

A successful result contains one or more artifacts:

```json
{
  "job_id": "job_01J...",
  "state": "succeeded",
  "artifacts": [
    {
      "id": "artifact_01J...",
      "role": "primary",
      "media_type": "video/mp4",
      "uri": "https://provider.example/results/artifact_01J...",
      "sha256": "hex-encoded-digest",
      "size_bytes": 12345678
    }
  ],
  "provenance": {
    "provider_id": "example.org/video-provider-001",
    "provider_version": "0.1.0",
    "skills": [],
    "agents": []
  },
  "receipt": {}
}
```

Artifact URIs SHOULD be time-limited or access-controlled when results are not
public. A digest SHOULD be supplied so a consumer can verify downloaded bytes.
The provider MUST declare when provenance fields are withheld and why.

## 9. Estimates and receipts

An estimate states its currency, total, expiry, assumptions, and optional line
items. It MUST identify whether taxes, transfer fees, and human work are
included.

A final receipt contains:

```json
{
  "currency": "USD",
  "total": "4.25",
  "line_items": [
    {
      "resource": "gpu_time",
      "quantity": "2.5",
      "unit": "minute",
      "unit_price": "1.50",
      "amount": "3.75"
    },
    {
      "resource": "storage",
      "quantity": "1",
      "unit": "gigabyte_day",
      "unit_price": "0.50",
      "amount": "0.50"
    }
  ],
  "estimate_total": "4.00",
  "variance_reason": "Render retry after a provider-side transient failure."
}
```

Quantities, prices, and totals MUST be decimal strings. The receipt MUST use one
currency, make line-item arithmetic reproducible, and explain material variance
from the accepted estimate. Protocol v0.1 records cost but does not prescribe a
payment rail or settlement currency.

## 10. Skills and agents

Jobs MAY reference versioned skills and agents. Each reference includes an ID,
version or immutable digest, declared input/output contract, and execution role.
Providers MUST NOT substitute a materially different skill or agent when the
request pins an immutable version.

Agent-initiated external actions, spending above a requester-defined threshold,
and publication of artifacts SHOULD require an explicit policy decision or
human approval.

## 11. Security and privacy

Implementations MUST authenticate callers, authorize access per job and
artifact, validate all referenced resources, and avoid exposing credentials in
events, logs, errors, or receipts. Providers SHOULD support short-lived
credentials and signed callbacks.

Remote resource fetching creates server-side request-forgery risk. Providers
MUST restrict schemes, network destinations, redirects, and response sizes.
Untrusted input and generated media MUST be treated as data, not executable
instructions. Retention and deletion behavior SHOULD be declared before job
acceptance.

## 12. Conformance

A v0.1 provider is conforming when it:

1. Publishes a valid descriptor.
2. Implements all five provider operations.
3. Enforces idempotent job creation.
4. Maps every job to a base lifecycle state.
5. Returns structured errors.
6. Returns final usage, price, and provenance information for terminal jobs.
7. Passes the protocol conformance fixtures once those fixtures are published.

Draft conformance indicates interoperability with this document, not security,
quality, legal compliance, or fitness for a particular production use.

## 13. Open questions for v0.2

- Capability negotiation and schema discovery.
- Streaming events and callback signatures.
- Human-review handoff and revision semantics.
- Multi-provider parent/child jobs.
- Privacy-preserving provenance and selective disclosure.
- Estimate reservation, dispute, and settlement interfaces.
- Content policy declarations and jurisdiction-specific requirements.
