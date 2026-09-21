"""Coverage-aware comparison of two finalized assessment reports.

The comparator deliberately avoids claiming a finding is fixed merely because it is absent.
It distinguishes persistent/new findings from not-reproduced and not-retested outcomes.
"""
from __future__ import annotations

from typing import Any


def _tool_for_rule(rule: str) -> str | None:
    if rule.startswith("header/"):
        return "http_baseline"
    if rule == "lab/missing-authorization":
        return "verify_lab_canary"
    return None


def _completed_tools(report: dict[str, Any]) -> set[str]:
    result = set()
    for check in report.get("checks", []):
        if isinstance(check, dict) and check.get("status") == "completed" and isinstance(check.get("tool"), str):
            result.add(check["tool"])
    return result


def compare_reports(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("reports must be objects")
    for report in (previous, current):
        if not isinstance(report.get("id"), str) or not isinstance(report.get("findings", []), list) or not isinstance(report.get("checks", []), list):
            raise ValueError("invalid report shape")
        if report.get("status") == "running":
            raise ValueError("running reports cannot be compared")

    comparable_scope = previous.get("target") == current.get("target") and previous.get("environment") == current.get("environment")
    current_tools = _completed_tools(current)
    old = {item.get("fingerprint"): item for item in previous.get("findings", []) if isinstance(item, dict) and isinstance(item.get("fingerprint"), str)}
    new = {item.get("fingerprint"): item for item in current.get("findings", []) if isinstance(item, dict) and isinstance(item.get("fingerprint"), str)}

    items = []
    counts = {"still_present": 0, "new": 0, "not_reproduced": 0, "not_retested": 0}
    for fingerprint, finding in sorted(old.items()):
        if fingerprint in new:
            state = "still_present"
            reason = "Matching fingerprint remains present in the current run."
        else:
            tool = _tool_for_rule(str(finding.get("rule", "")))
            if comparable_scope and tool and tool in current_tools:
                state = "not_reproduced"
                reason = "Comparable check completed, but the prior fingerprint was not observed. This is not an automatic fixed verdict."
            else:
                state = "not_retested"
                reason = "Comparable successful coverage for this rule was not established."
        counts[state] += 1
        items.append({"fingerprint": fingerprint, "title": finding.get("title"), "rule": finding.get("rule"), "state": state, "reason": reason})

    for fingerprint, finding in sorted(new.items()):
        if fingerprint not in old:
            counts["new"] += 1
            items.append({"fingerprint": fingerprint, "title": finding.get("title"), "rule": finding.get("rule"), "state": "new", "reason": "Fingerprint was not present in the previous report."})

    return {
        "schema": "hackgpt.retest-diff/v1",
        "previous_run": previous["id"],
        "current_run": current["id"],
        "comparable_scope": comparable_scope,
        "counts": counts,
        "items": items,
        "conclusion": "comparison_only",
        "note": "Absent findings are never labeled fixed solely by absence. Review coverage, remediation and evidence before closure.",
    }
