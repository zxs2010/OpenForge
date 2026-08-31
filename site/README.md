# OpenForge Public Gateway

This directory contains the public, read-safe entrance to OpenForge. It lets a
visitor understand and exercise the V1 connection loop without exposing the
write API of a local reference node.

The public intent form performs the same deterministic capability matching in
the browser and clearly labels the result as an unsaved demo. Durable network
records and Activity events belong to the Python reference node or a future
authenticated hosted node.

## Run

```bash
npm install
npm run dev
```

## Verify

```bash
npm run lint
npm test
```

The site is built with vinext for the Sites hosting runtime. Hosting metadata is
kept in `.openai/hosting.json`; no runtime secret, database, or object-storage
binding is required for this release.
