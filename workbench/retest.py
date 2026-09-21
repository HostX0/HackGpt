"""Coverage-aware comparison of two finalized assessment reports.

The comparator deliberately avoids claiming a finding is fixed merely because it is absent.
It distinguishes persistent/new findings from not-reproduced and not-retested outcomes and
binds prior remediation guidance/evidence to the exact recheck without claiming remediation
was actually applied.
"""
from __future__ import annotations

import hashlib
from typing import Any


def _tool_for_rule(rule: str) -> str | None:
    if rule.startswith("web/"):
        return "native-web-headers"
    if rule.startswith("header/"):
        return "http_baseline"  # legacy reports before the registry-backed web adapter
    if rule == "lab/missing-authorization":
        return "verify_lab_canary"
    return None


def _completed_tools(report: dict[str, Any]) -> set[str]:
    result = set()
    for check in report.get("checks", []):
        if isinstance(check, dict) and check.get("status") == "completed" and isinstance(check.get("tool"), str):
            result.add(check["tool"])
    return result


def _tool_observation(report: dict[str, Any], tool: str | None) -> dict[str, Any]:
    if not tool:
        return {"tool": None, "status": "unmapped", "reason": "No comparable execution mapping exists for this rule."}
    observations = []
    for check in report.get("checks", []):
        if not isinstance(check, dict) or check.get("tool") != tool:
            continue
        observations.append({
            "status": check.get("status") if isinstance(check.get("status"), str) else "unknown",
            "reason": check.get("reason") if isinstance(check.get("reason"), str) else None,
        })
    if not observations:
        return {"tool": tool, "status": "not_executed", "reason": "Mapped check is absent from the current run."}
    if any(item["status"] == "completed" for item in observations):
        return {"tool": tool, "status": "completed", "reason": None}
    # Keep the first explicit non-success state. Multiple retries are intentionally not
    # collapsed into success unless at least one check actually completed.
    first = observations[0]
    return {"tool": tool, "status": first["status"], "reason": first["reason"]}


def _sha256_text(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _recheck_binding(previous_run: str, current_run: str, finding: dict[str, Any], coverage: dict[str, Any], comparable_scope: bool) -> dict[str, Any]:
    """Create a non-secret review link from prior evidence/remediation to this recheck."""
    remediation = finding.get("remediation")
    evidence_sha = finding.get("evidence_sha256")
    return {
        "previous_run": previous_run,
        "current_run": current_run,
        "previous_finding_id": finding.get("id") if isinstance(finding.get("id"), str) else None,
        "previous_evidence_sha256": evidence_sha if isinstance(evidence_sha, str) else None,
        "remediation_sha256": _sha256_text(remediation),
        "remediation_guidance_present": isinstance(remediation, str) and bool(remediation),
        "remediation_applied": "unknown",
        "comparable_scope": comparable_scope,
        "coverage": coverage,
    }


def compare_reports(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("reports must be objects")
    for report in (previous, current):
        if not isinstance(report.get("id"), str) or not isinstance(report.get("findings", []), list) or not isinstance(report.get("checks", []), list):
            raise ValueError("invalid report shape")
        if report.get("status") == "running":
            raise ValueError("running reports cannot be compared")

    same_target = previous.get("target") == current.get("target")
    same_environment = previous.get("environment") == current.get("environment")
    comparable_scope = same_target and same_environment
    current_tools = _completed_tools(current)
    old = {item.get("fingerprint"): item for item in previous.get("findings", []) if isinstance(item, dict) and isinstance(item.get("fingerprint"), str)}
    new = {item.get("fingerprint"): item for item in current.get("findings", []) if isinstance(item, dict) and isinstance(item.get("fingerprint"), str)}

    items = []
    counts = {"still_present": 0, "new": 0, "not_reproduced": 0, "not_retested": 0}
    for fingerprint, finding in sorted(old.items()):
        tool = _tool_for_rule(str(finding.get("rule", "")))
        coverage = _tool_observation(current, tool)
        if fingerprint in new:
            state = "still_present"
            reason = "Matching fingerprint remains present in the current run."
        elif comparable_scope and tool and tool in current_tools:
            state = "not_reproduced"
            reason = "Comparable check completed, but the prior fingerprint was not observed. This is not an automatic fixed verdict."
        else:
            state = "not_retested"
            if not comparable_scope:
                reason = "Target or environment changed; comparable successful coverage was not established."
            elif coverage["status"] not in ("completed",):
                reason = "Comparable successful coverage for this rule was not established; the mapped check was not completed."
            else:
                reason = "Comparable successful coverage for this rule was not established."
        counts[state] += 1
        items.append({
            "fingerprint": fingerprint,
            "title": finding.get("title"),
            "rule": finding.get("rule"),
            "state": state,
            "reason": reason,
            "recheck": _recheck_binding(previous["id"], current["id"], finding, coverage, comparable_scope),
        })

    for fingerprint, finding in sorted(new.items()):
        if fingerprint not in old:
            counts["new"] += 1
            items.append({
                "fingerprint": fingerprint,
                "title": finding.get("title"),
                "rule": finding.get("rule"),
                "state": "new",
                "reason": "Fingerprint was not present in the previous report.",
                "recheck": {
                    "previous_run": previous["id"],
                    "current_run": current["id"],
                    "previous_finding_id": None,
                    "previous_evidence_sha256": None,
                    "remediation_sha256": None,
                    "remediation_guidance_present": False,
                    "remediation_applied": "not_applicable",
                    "comparable_scope": comparable_scope,
                    "coverage": _tool_observation(current, _tool_for_rule(str(finding.get("rule", "")))),
                },
            })

    return {
        "schema": "hackgpt.retest-diff/v1",
        "previous_run": previous["id"],
        "current_run": current["id"],
        "comparable_scope": comparable_scope,
        "scope_comparison": {"same_target": same_target, "same_environment": same_environment},
        "counts": counts,
        "items": items,
        "conclusion": "comparison_only",
        "note": "Absent findings are never labeled fixed solely by absence. Remediation guidance is hash-linked for review, but whether it was applied remains unknown unless separate evidence establishes that fact.",
    }
