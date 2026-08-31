from __future__ import annotations

import pytest
from openforge.models import JobInput, JobRequest, JobState, JobStatus, ValidationError


def test_job_request_returns_named_text_input() -> None:
    request = JobRequest(
        request_id="req-001",
        kind="video.generate",
        inputs=(JobInput(name="brief", media_type="text/plain", value="Launch film"),),
        parameters={"aspect_ratio": "9:16"},
    )

    assert request.text_input("brief") == "Launch film"
    assert request.parameters["aspect_ratio"] == "9:16"


@pytest.mark.parametrize(
    ("request_id", "message"),
    [
        ("", "request_id"),
        ("../escape", "request_id"),
        ("contains spaces", "request_id"),
        ("x" * 129, "request_id"),
    ],
)
def test_job_request_rejects_unsafe_request_id(request_id: str, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        JobRequest(
            request_id=request_id,
            kind="video.generate",
            inputs=(JobInput(name="brief", media_type="text/plain", value="Film"),),
        )


def test_text_input_rejects_missing_or_oversized_values() -> None:
    request = JobRequest(
        request_id="req-001",
        kind="video.generate",
        inputs=(JobInput(name="title", media_type="text/plain", value="Film"),),
    )

    with pytest.raises(ValidationError, match="brief"):
        request.text_input("brief")

    with pytest.raises(ValidationError, match="maximum length"):
        JobInput(
            name="brief",
            media_type="text/plain",
            value="x" * 8_001,
        )


@pytest.mark.parametrize("progress", [-1, 101])
def test_job_status_rejects_progress_outside_percentage_range(progress: int) -> None:
    with pytest.raises(ValidationError, match="progress"):
        JobStatus(job_id="job-001", state=JobState.RUNNING, progress=progress)
