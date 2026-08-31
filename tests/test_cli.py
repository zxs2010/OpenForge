from __future__ import annotations

import json
from pathlib import Path

import openforge.cli as cli_module
from openforge.cli import main
from openforge.models import (
    Artifact,
    CancellationResult,
    CostEstimate,
    JobRequest,
    JobResult,
    JobState,
    JobStatus,
    ProviderDescriptor,
    Receipt,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_cli_lists_community_providers_as_json(capsys) -> None:
    exit_code = main(
        [
            "--catalog",
            str(REPOSITORY_ROOT / "providers"),
            "providers",
            "list",
            "--json",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert [item["slug"] for item in output] == [
        "comfyui",
        "moneyprinter-turbo",
        "openmontage",
        "videolingo",
    ]


def test_cli_inspects_one_provider(capsys) -> None:
    exit_code = main(
        [
            "--catalog",
            str(REPOSITORY_ROOT / "providers"),
            "providers",
            "inspect",
            "moneyprinter-turbo",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "harry0703/MoneyPrinterTurbo" in output
    assert "adapter-ready" in output


class FakeProvider:
    descriptor = ProviderDescriptor(
        id="community.moneyprinter-turbo",
        name="MoneyPrinterTurbo",
        version="test",
        capabilities=("video.generate",),
    )

    def __init__(self) -> None:
        self.requests: list[JobRequest] = []

    def estimate_cost(self, request: JobRequest) -> CostEstimate:
        return CostEstimate(False, None, None)

    def create_job(self, request: JobRequest) -> JobStatus:
        self.requests.append(request)
        return JobStatus("task-123", JobState.QUEUED, 0)

    def get_status(self, job_id: str) -> JobStatus:
        return JobStatus(job_id, JobState.RUNNING, 25)

    def cancel_job(self, job_id: str) -> CancellationResult:
        return CancellationResult(job_id, False, "unsupported")

    def get_result(self, job_id: str) -> JobResult:
        return JobResult(
            job_id=job_id,
            state=JobState.SUCCEEDED,
            artifacts=(Artifact("video-1", "video/mp4", "https://example.test/final.mp4"),),
            receipt=Receipt(
                provider_id=self.descriptor.id,
                total=None,
                currency=None,
            ),
        )


def test_cli_creates_moneyprinter_job_with_normalized_request(monkeypatch, capsys) -> None:
    provider = FakeProvider()
    monkeypatch.setattr(
        cli_module,
        "MoneyPrinterTurboProvider",
        lambda **_: provider,
    )

    exit_code = main(
        [
            "jobs",
            "create",
            "--provider",
            "moneyprinter-turbo",
            "--request-id",
            "demo-001",
            "--brief",
            "Create a product video",
            "--aspect-ratio",
            "9:16",
            "--duration",
            "15",
            "--language",
            "zh-CN",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output == {"job_id": "task-123", "progress": 0, "state": "queued"}
    assert provider.requests[0].request_id == "demo-001"
    assert provider.requests[0].text_input("brief") == "Create a product video"
    assert provider.requests[0].parameters["duration_seconds"] == 15


def test_cli_returns_normalized_job_result(monkeypatch, capsys) -> None:
    provider = FakeProvider()
    monkeypatch.setattr(
        cli_module,
        "MoneyPrinterTurboProvider",
        lambda **_: provider,
    )

    exit_code = main(
        [
            "jobs",
            "result",
            "--provider",
            "moneyprinter-turbo",
            "--job-id",
            "task-123",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["state"] == "succeeded"
    assert output["artifacts"][0]["uri"] == "https://example.test/final.mp4"
    assert output["receipt"]["total"] is None
