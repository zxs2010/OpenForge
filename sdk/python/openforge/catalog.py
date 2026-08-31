"""Read-only catalog of independently maintained community providers."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

MAX_MANIFEST_BYTES = 64 * 1024
_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_VALID_STATUSES = {"adapter-ready", "candidate", "paused"}
_VALID_INTEGRATIONS = {"http", "http-websocket", "agent-checkpoint", "cli"}


class CatalogError(ValueError):
    """Raised when a provider catalog or manifest is invalid."""


@dataclass(frozen=True, slots=True)
class UpstreamProject:
    """Pinned upstream open-source project information."""

    repository: str
    ref: str
    license: str


@dataclass(frozen=True, slots=True)
class ProviderManifest:
    """One catalog entry describing an external provider integration."""

    schema_version: str
    id: str
    slug: str
    name: str
    status: str
    integration: str
    capabilities: tuple[str, ...]
    upstream: UpstreamProject
    operations: Mapping[str, str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], source: Path) -> ProviderManifest:
        """Validate and construct one manifest from decoded JSON."""
        try:
            upstream_value = value["upstream"]
            if not isinstance(upstream_value, Mapping):
                raise TypeError("upstream must be an object")
            repository = _required_string(upstream_value, "repository")
            if not _REPOSITORY_PATTERN.fullmatch(repository):
                raise CatalogError(
                    f"{source}: upstream repository must use GitHub owner/name form"
                )
            upstream = UpstreamProject(
                repository=repository,
                ref=_required_string(upstream_value, "ref"),
                license=_required_string(upstream_value, "license"),
            )
            capabilities_value = value["capabilities"]
            if not isinstance(capabilities_value, list) or not capabilities_value:
                raise TypeError("capabilities must be a non-empty array")
            capabilities = tuple(_plain_string(item, "capability") for item in capabilities_value)
            operations_value = value.get("operations", {})
            if not isinstance(operations_value, Mapping):
                raise TypeError("operations must be an object")
            operations = MappingProxyType(
                {
                    _plain_string(key, "operation name"): _plain_string(state, "operation state")
                    for key, state in operations_value.items()
                }
            )
            status = _required_string(value, "status")
            if status not in _VALID_STATUSES:
                raise CatalogError(f"{source}: unsupported provider status {status!r}")
            integration = _required_string(value, "integration")
            if integration not in _VALID_INTEGRATIONS:
                raise CatalogError(f"{source}: unsupported integration {integration!r}")
            schema_version = _required_string(value, "schema_version")
            if schema_version != "0.1":
                raise CatalogError(f"{source}: schema_version must be 0.1")
            return cls(
                schema_version=schema_version,
                id=_required_string(value, "id"),
                slug=_required_string(value, "slug"),
                name=_required_string(value, "name"),
                status=status,
                integration=integration,
                capabilities=capabilities,
                upstream=upstream,
                operations=operations,
            )
        except (KeyError, TypeError) as exc:
            raise CatalogError(f"{source}: invalid provider manifest: {exc}") from exc

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "status": self.status,
            "integration": self.integration,
            "capabilities": list(self.capabilities),
            "upstream": {
                "repository": self.upstream.repository,
                "ref": self.upstream.ref,
                "license": self.upstream.license,
            },
            "operations": dict(self.operations),
        }


@dataclass(frozen=True, slots=True)
class ProviderCatalog:
    """Validated collection of provider manifests."""

    manifests: tuple[ProviderManifest, ...]

    @classmethod
    def load(cls, directory: Path) -> ProviderCatalog:
        """Load all direct child provider manifests without executing provider code."""
        directory = directory.resolve()
        if not directory.is_dir():
            raise CatalogError(f"provider catalog directory does not exist: {directory}")
        manifests: list[ProviderManifest] = []
        seen_ids: set[str] = set()
        seen_slugs: set[str] = set()
        for path in sorted(directory.glob("*/provider.json")):
            if path.stat().st_size > MAX_MANIFEST_BYTES:
                raise CatalogError(f"{path}: provider manifest exceeds size limit")
            try:
                decoded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise CatalogError(f"{path}: unable to read provider manifest") from exc
            if not isinstance(decoded, Mapping):
                raise CatalogError(f"{path}: provider manifest must be a JSON object")
            manifest = ProviderManifest.from_mapping(decoded, path)
            if manifest.id in seen_ids:
                raise CatalogError(f"duplicate provider id: {manifest.id}")
            if manifest.slug in seen_slugs:
                raise CatalogError(f"duplicate provider slug: {manifest.slug}")
            seen_ids.add(manifest.id)
            seen_slugs.add(manifest.slug)
            manifests.append(manifest)
        if not manifests:
            raise CatalogError(f"no provider manifests found in {directory}")
        manifests.sort(key=lambda item: item.slug)
        return cls(manifests=tuple(manifests))

    def get(self, identifier: str) -> ProviderManifest:
        """Return a manifest by slug or provider ID."""
        for manifest in self.manifests:
            if identifier in {manifest.slug, manifest.id}:
                return manifest
        raise CatalogError(f"unknown provider: {identifier}")


def _required_string(value: Mapping[str, Any], key: str) -> str:
    try:
        return _plain_string(value[key], key)
    except KeyError as exc:
        raise KeyError(f"missing required field {key!r}") from exc


def _plain_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field_name} must be a non-empty string")
    if len(value) > 256 or not value.isprintable():
        raise TypeError(f"{field_name} is too long or contains control characters")
    return value
