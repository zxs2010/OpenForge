# MoneyPrinterTurbo Provider

This adapter connects OpenForge to the independently maintained
[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) HTTP API.
The upstream source is not copied into OpenForge.

## Supported today

- `video.generate`
- Create a task through `POST /api/v1/videos`
- Prevent duplicate creation for a request ID during the adapter process lifetime
- Normalize task state from `GET /api/v1/tasks/{task_id}`
- Return generated MP4 artifact URLs
- Send an API key through the `x-api-key` header when configured

MoneyPrinterTurbo v1 does not expose complete cost estimation or cancellation
for a running task. The adapter reports both limitations explicitly instead of
claiming unsupported behavior.

The current idempotency store is process-local. A durable OpenForge router must
persist request IDs across restarts before this adapter can claim full Protocol
v0.1 conformance.

## Run the upstream service

Install MoneyPrinterTurbo at the pinned catalog version and start its API:

```bash
uv run python main.py
```

The default OpenForge endpoint is `http://127.0.0.1:8080`. If the upstream
service has API authentication enabled, set the secret only in the environment:

```bash
export MONEYPRINTER_TURBO_API_KEY="your-api-key"
```

See `MoneyPrinterTurboProvider` in the Python SDK for programmatic use.
