"""OpenForge command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

from openforge.catalog import ProviderCatalog
from openforge.models import JobInput, JobRequest, OpenForgeError
from openforge.providers.moneyprinter_turbo import MoneyPrinterTurboProvider


def _default_catalog_path() -> Path:
    return Path(__file__).resolve().parents[3] / "providers"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openforge",
        description="Inspect and exercise OpenForge community providers.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=_default_catalog_path(),
        help="path to the provider catalog",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    providers = commands.add_parser("providers", help="inspect provider catalog entries")
    provider_commands = providers.add_subparsers(dest="provider_command", required=True)
    list_command = provider_commands.add_parser("list", help="list known providers")
    list_command.add_argument("--json", action="store_true", dest="as_json")
    inspect_command = provider_commands.add_parser("inspect", help="show one provider")
    inspect_command.add_argument("provider")

    jobs = commands.add_parser("jobs", help="submit and inspect production jobs")
    job_commands = jobs.add_subparsers(dest="job_command", required=True)
    create_command = job_commands.add_parser("create", help="create a video job")
    _add_provider_connection_arguments(create_command)
    create_command.add_argument(
        "--request-id",
        default=f"req-{uuid4()}",
        help="idempotency key; reuse it only when retrying the same request",
    )
    create_command.add_argument("--brief", required=True)
    create_command.add_argument("--script")
    create_command.add_argument(
        "--aspect-ratio",
        choices=("16:9", "9:16", "1:1"),
        default="9:16",
    )
    create_command.add_argument("--duration", type=_duration, default=15)
    create_command.add_argument("--language", default="")

    for name in ("status", "result", "cancel"):
        job_command = job_commands.add_parser(name, help=f"{name} a production job")
        _add_provider_connection_arguments(job_command)
        job_command.add_argument("--job-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process-compatible exit code."""
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "providers":
            return _run_provider_command(args)
        return _run_job_command(args)
    except (OpenForgeError, ValueError) as exc:
        print(f"openforge: {exc}", file=sys.stderr)
        return 1


def _run_provider_command(args: argparse.Namespace) -> int:
    catalog = ProviderCatalog.load(args.catalog)
    if args.provider_command == "list":
        values = [manifest.to_dict() for manifest in catalog.manifests]
        if args.as_json:
            print(json.dumps(values, indent=2, sort_keys=True))
        else:
            for manifest in catalog.manifests:
                print(
                    f"{manifest.slug}\t{manifest.status}\t{manifest.integration}\t"
                    f"{manifest.upstream.repository}@{manifest.upstream.ref}"
                )
        return 0
    manifest = catalog.get(args.provider)
    print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
    return 0


def _run_job_command(args: argparse.Namespace) -> int:
    provider = MoneyPrinterTurboProvider(base_url=args.base_url)
    if args.job_command == "create":
        inputs = [JobInput(name="brief", media_type="text/plain", value=args.brief)]
        if args.script:
            inputs.append(JobInput(name="script", media_type="text/plain", value=args.script))
        parameters: dict[str, object] = {
            "aspect_ratio": args.aspect_ratio,
            "duration_seconds": args.duration,
        }
        if args.language:
            parameters["language"] = args.language
        request = JobRequest(
            request_id=args.request_id,
            kind="video.generate",
            inputs=tuple(inputs),
            parameters=parameters,
        )
        status = provider.create_job(request)
        print(
            json.dumps(
                {
                    "job_id": status.job_id,
                    "state": status.state.value,
                    "progress": status.progress,
                },
                sort_keys=True,
            )
        )
        return 0
    if args.job_command == "status":
        status = provider.get_status(args.job_id)
        print(
            json.dumps(
                {
                    "job_id": status.job_id,
                    "state": status.state.value,
                    "progress": status.progress,
                    "message": status.message,
                },
                sort_keys=True,
            )
        )
        return 0
    if args.job_command == "cancel":
        cancellation = provider.cancel_job(args.job_id)
        print(
            json.dumps(
                {
                    "job_id": cancellation.job_id,
                    "accepted": cancellation.accepted,
                    "reason": cancellation.reason,
                },
                sort_keys=True,
            )
        )
        return 0
    result = provider.get_result(args.job_id)
    print(
        json.dumps(
            {
                "job_id": result.job_id,
                "state": result.state.value,
                "artifacts": [
                    {
                        "id": artifact.id,
                        "media_type": artifact.media_type,
                        "uri": artifact.uri,
                        "role": artifact.role,
                    }
                    for artifact in result.artifacts
                ],
                "receipt": {
                    "provider_id": result.receipt.provider_id,
                    "total": (
                        str(result.receipt.total) if result.receipt.total is not None else None
                    ),
                    "currency": result.receipt.currency,
                },
            },
            sort_keys=True,
        )
    )
    return 0


def _add_provider_connection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--provider",
        choices=("moneyprinter-turbo",),
        required=True,
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8080",
        help="trusted MoneyPrinterTurbo HTTP origin",
    )


def _duration(value: str) -> int:
    try:
        duration = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("duration must be an integer") from exc
    if not 1 <= duration <= 3_600:
        raise argparse.ArgumentTypeError("duration must be between 1 and 3600")
    return duration
