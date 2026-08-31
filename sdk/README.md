# SDK

The first Python SDK lives in `sdk/python/openforge`. It contains transport-
neutral protocol models, the `ProductionProvider` interface, the community
catalog reader, and the first MoneyPrinterTurbo adapter.

The SDK has no runtime package dependencies in v0.1. Development tools are
available through the root `pyproject.toml` `dev` extra.
