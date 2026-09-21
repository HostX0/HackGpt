"""Turn one completed reviewed-adapter receipt into ordinary reviewable report evidence.

This is a reporting bridge only. It performs no adapter I/O or model inference and it
never upgrades candidate observations to an independently verified state.
"""
from __future__ import annotations

import copy
import hashlib

from . import __version__
from .engine import LIMITATION, digest, seal
from .execution_receipts import normalize_execution_receipt


def _report_id(lifecycle_id: str) -> str:
    return hashlib.sha256(("adapter-report:" + lifecycle_id).encode("utf-8")).hexdigest()[:32]


def _target(summary: dict) -> str:
    if isinstance(summary.get("target"), str):
        return summary["target"]
    label = summary.get("project_label") or "project"
    asset = summary.get("asset_key") or "asset"
    return f"project://{label}#{asset}"


def build_adapter_report(record: dict) -> dict:
    if not isinstance(record, dict) or record.get("status") != "completed":
        raise ValueError("Only a completed reviewed adapter run can become a report")
    lifecycle_id = record.get("id")
    if not isinstance(lifecycle_id, str) or len(lifecycle_id) != 32:
        raise ValueError("Adapter lifecycle record has an invalid id")
    receipt = normalize_execution_receipt(record.get("receipt"))
    result = receipt["result"]
    findings = copy.deepcopy(result.get("findings", []))
    for finding in findings:
        if finding.get("verification") != "candidate":
            raise ValueError("Adapter report bridge refuses self-verified findings")
        finding["observed_at"] = record["updated_at"]

    result_status = result.get("status")
    status = "completed" if result_status == "completed" else ("failed" if result_status == "error" else "partial")
    check_status = "inconclusive" if result_status in {"partial", "skipped"} else result_status
    adapter = receipt["declaration"]["adapter"]
    event = {
        "sequence": 1,
        "at": record["updated_at"],
        "kind": "adapter_receipt_imported",
        "message": "Reviewed adapter receipt added to report as candidate observations.",
        "details": {
            "lifecycle_id": lifecycle_id,
            "plan_sha256": record["plan_sha256"],
            "adapter": adapter["id"],
            "adapter_version": adapter["version"],
            "candidate_findings": len(findings),
        },
        "previous_sha256": "0" * 64,
    }
    event["sha256"] = digest(event)
    report = {
        "schema_version": "1.0",
        "engine_version": __version__,
        "id": _report_id(lifecycle_id),
        "started_at": record["created_at"],
        "finished_at": record["updated_at"],
        "status": status,
        "mode": "analyst",
        "target": _target(receipt["request_summary"]),
        "environment": "reviewed_adapter_receipt",
        "authorization": "Exact reviewed adapter plan " + record["plan_sha256"][:16],
        "verification_approved": False,
        "findings": findings,
        "checks": [{
            "tool": adapter["id"],
            "status": check_status,
            "adapter": copy.deepcopy(adapter),
            "coverage": copy.deepcopy(result.get("coverage", {})),
            "receipt_usage": copy.deepcopy(receipt["usage"]),
            "plan_sha256": record["plan_sha256"],
            **({"reason": result["error"]} if result.get("error") else {}),
        }],
        "events": [event],
        "verdict": "observations_need_context" if findings else "no_findings_in_executed_checks",
        "execution_budget": {
            "wall_clock_seconds": receipt["declaration"]["limits"]["timeout_seconds"],
            "native_http_requests": receipt["declaration"]["limits"]["max_requests"],
            "enforcement": "exact approved adapter declaration; this report bridge performs no additional I/O",
        },
        "ai": {
            "status": "not_requested",
            "interpretation": None,
            "provider": None,
            "model": None,
            "processing_policy": "not_used",
            "cloud_processing_approved": False,
            "data_disclosure": "No model request was made while importing the reviewed adapter receipt.",
        },
        "limitations": [
            LIMITATION,
            "Reviewed adapter findings remain candidate observations; this bridge does not independently verify them.",
            "The report reflects only the approved adapter receipt and its declared coverage, not untested application behavior.",
            "Checksums are unsigned integrity aids, not proof of authorship.",
        ],
        "provenance": {
            "kind": "reviewed_adapter_receipt",
            "lifecycle_id": lifecycle_id,
            "plan_sha256": record["plan_sha256"],
            "receipt_schema": receipt["schema"],
            "adapter": copy.deepcopy(adapter),
            "request_summary": copy.deepcopy(receipt["request_summary"]),
        },
        "durability": {
            "status": "durable",
            "storage": "sqlite",
            "terminal_publication": "adapter_receipt_report_transaction",
            "checkpoint_gap_observed": False,
        },
    }
    return seal(report)
