from __future__ import annotations

import json
from pathlib import Path

import pytest
from openforge.catalog import CatalogError, ProviderCatalog

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_repository_catalog_lists_first_community_projects() -> None:
    catalog = ProviderCatalog.load(REPOSITORY_ROOT / "providers")

    assert [manifest.slug for manifest in catalog.manifests] == [
        "comfyui",
        "moneyprinter-turbo",
        "openmontage",
        "videolingo",
    ]
    moneyprinter = catalog.get("moneyprinter-turbo")
    assert moneyprinter.status == "adapter-ready"
    assert moneyprinter.upstream.repository == "harry0703/MoneyPrinterTurbo"
    assert moneyprinter.upstream.ref == "v1.3.5"
    assert moneyprinter.upstream.license == "MIT"


def test_catalog_rejects_duplicate_provider_ids(tmp_path: Path) -> None:
    manifest = {
        "schema_version": "0.1",
        "id": "community.example",
        "slug": "example",
        "name": "Example",
        "status": "candidate",
        "integration": "http",
        "capabilities": ["video.generate"],
        "upstream": {
            "repository": "example/project",
            "ref": "main",
            "license": "MIT",
        },
    }
    for directory in (tmp_path / "one", tmp_path / "two"):
        directory.mkdir()
        (directory / "provider.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(CatalogError, match="duplicate provider id"):
        ProviderCatalog.load(tmp_path)


def test_catalog_rejects_non_github_repository(tmp_path: Path) -> None:
    directory = tmp_path / "bad"
    directory.mkdir()
    (directory / "provider.json").write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "id": "community.bad",
                "slug": "bad",
                "name": "Bad",
                "status": "candidate",
                "integration": "http",
                "capabilities": ["video.generate"],
                "upstream": {
                    "repository": "https://example.com/untrusted/archive",
                    "ref": "main",
                    "license": "Unknown",
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CatalogError, match="owner/name"):
        ProviderCatalog.load(tmp_path)
