"""Provider interface implemented by all OpenForge production adapters."""

from __future__ import annotations

from typing import Protocol

from openforge.models import (
    CancellationResult,
    CostEstimate,
    JobRequest,
    JobResult,
    JobStatus,
    ProviderDescriptor,
)


class ProductionProvider(Protocol):
    """Transport-neutral OpenForge Provider v0.1 contract."""

    @property
    def descriptor(self) -> ProviderDescriptor:
        """Describe provider identity and supported job kinds."""

    def estimate_cost(self, request: JobRequest) -> CostEstimate:
        """Return a non-binding estimate or an explicit unavailable result."""

    def create_job(self, request: JobRequest) -> JobStatus:
        """Accept an idempotent production request."""

    def get_status(self, job_id: str) -> JobStatus:
        """Return current normalized lifecycle state."""

    def cancel_job(self, job_id: str) -> CancellationResult:
        """Request cancellation and report whether it was accepted."""

    def get_result(self, job_id: str) -> JobResult:
        """Return terminal artifacts, provenance, and receipt information."""
