from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openforge.models import JobInput, JobRequest, JobState
from openforge.provider import ProductionProvider
from openforge.providers.moneyprinter_turbo import MoneyPrinterTurboProvider


class ContractTransport:
    def request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        if method == "POST":
            return {"status": 200, "data": {"task_id": "contract-job"}}
        return {
            "status": 200,
            "data": {
                "task_id": "contract-job",
                "state": 1,
                "progress": 100,
                "videos": ["/tasks/contract-job/final.mp4"],
            },
        }


def test_moneyprinter_implements_openforge_provider_contract() -> None:
    provider: ProductionProvider = MoneyPrinterTurboProvider(
        transport=ContractTransport()
    )
    request = JobRequest(
        request_id="contract-request",
        kind="video.generate",
        inputs=(JobInput(name="brief", media_type="text/plain", value="Test"),),
    )

    assert provider.descriptor.id == "community.moneyprinter-turbo"
    assert provider.estimate_cost(request).available is False
    assert provider.create_job(request).state is JobState.QUEUED
    assert provider.get_status("contract-job").state is JobState.SUCCEEDED
    assert provider.cancel_job("contract-job").accepted is False
    assert provider.get_result("contract-job").state is JobState.SUCCEEDED
