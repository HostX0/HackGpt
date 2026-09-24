"""Execution-neutral access-control matrix evaluation.

This module never authenticates, sends requests, or stores credentials. It evaluates
explicit operator-defined expectations against normalized observations from a separate,
scoped test harness. Unauthorized-access mismatches become candidate observations only;
independent verification remains a separate workbench authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from .contracts import ADAPTER_SCHEMA, normalize_adapter_result

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,95}")
MAX_CASES = 256
_ALLOWED_OBSERVED = {"allowed", "denied", "error", "skipped"}


def _id(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"invalid {name}")
    return value


@dataclass(frozen=True)
class AccessExpectation:
    role: str
    resource: str
    should_allow: bool

    @classmethod
    def parse(cls, value: Any) -> "AccessExpectation":
        if not isinstance(value, dict) or set(value) != {
            "role",
            "resource",
            "should_allow",
        }:
            raise ValueError(
                "expectation must contain exactly role, resource and should_allow"
            )
        if type(value["should_allow"]) is not bool:
            raise ValueError("should_allow must be boolean")
        return cls(
            _id(value["role"], "role"),
            _id(value["resource"], "resource"),
            value["should_allow"],
        )


@dataclass(frozen=True)
class AccessObservation:
    role: str
    resource: str
    observed: str
    control_confirmed: bool

    @classmethod
    def parse(cls, value: Any) -> "AccessObservation":
        if not isinstance(value, dict) or set(value) != {
            "role",
            "resource",
            "observed",
            "control_confirmed",
        }:
            raise ValueError(
                "observation must contain exactly role, resource, observed and control_confirmed"
            )
        observed = value["observed"]
        if observed not in _ALLOWED_OBSERVED:
            raise ValueError("invalid observed access state")
        if type(value["control_confirmed"]) is not bool:
            raise ValueError("control_confirmed must be boolean")
        return cls(
            _id(value["role"], "role"),
            _id(value["resource"], "resource"),
            observed,
            value["control_confirmed"],
        )


def evaluate_access_matrix(
    expectations: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    *,
    asset_key: str,
    version: str = "1",
) -> dict[str, Any]:
    """Compare an explicit role/resource policy with normalized test outcomes.

    No credentials, response bodies, cookies, tokens, or customer records are accepted by
    this contract. A denied-control flag is required before an unexpected allow can become
    a high-confidence candidate. Missing/error/skipped cases remain incomplete coverage.
    """
    if not isinstance(expectations, list) or not isinstance(observations, list):
        raise ValueError("expectations and observations must be lists")
    if (
        not expectations
        or len(expectations) > MAX_CASES
        or len(observations) > MAX_CASES
    ):
        raise ValueError("access matrix must contain from 1 to 256 bounded cases")
    if not isinstance(version, str) or not version.strip() or len(version) > 64:
        raise ValueError("matrix version must be a short non-empty string")

    expected = [AccessExpectation.parse(item) for item in expectations]
    keys = [(item.role, item.resource) for item in expected]
    key_set = set(keys)
    if len(keys) != len(key_set):
        raise ValueError("duplicate role/resource expectation")

    observed_items = [AccessObservation.parse(item) for item in observations]
    observed_map: dict[tuple[str, str], AccessObservation] = {}
    for item in observed_items:
        key = (item.role, item.resource)
        if key in observed_map:
            raise ValueError("duplicate role/resource observation")
        if key not in key_set:
            raise ValueError("observation is outside the declared matrix")
        observed_map[key] = item

    findings = []
    cases = []
    completed = 0
    incomplete = 0
    for item in expected:
        key = (item.role, item.resource)
        observation = observed_map.get(key)
        if observation is None:
            cases.append(
                {
                    "role": item.role,
                    "resource": item.resource,
                    "expected": "allowed" if item.should_allow else "denied",
                    "observed": "not_tested",
                    "result": "inconclusive",
                }
            )
            incomplete += 1
            continue

        expected_state = "allowed" if item.should_allow else "denied"
        if observation.observed in {"error", "skipped"}:
            cases.append(
                {
                    "role": item.role,
                    "resource": item.resource,
                    "expected": expected_state,
                    "observed": observation.observed,
                    "result": "inconclusive",
                }
            )
            incomplete += 1
            continue

        completed += 1
        matches = (item.should_allow and observation.observed == "allowed") or (
            (not item.should_allow) and observation.observed == "denied"
        )
        result = "matched" if matches else "mismatch"
        cases.append(
            {
                "role": item.role,
                "resource": item.resource,
                "expected": expected_state,
                "observed": observation.observed,
                "result": result,
            }
        )

        # Only an unexpected allow represents a confidentiality/authorization candidate.
        # An unexpected denial remains a policy mismatch in the case matrix but is not
        # converted into an exploitability claim.
        if (not item.should_allow) and observation.observed == "allowed":
            confidence = 0.9 if observation.control_confirmed else 0.45
            findings.append(
                {
                    "rule": "access-control/unexpected-allow",
                    "title": f"Role {item.role} reached restricted resource {item.resource}",
                    "severity": "high",
                    "confidence": confidence,
                    "evidence": {
                        "role": item.role,
                        "resource": item.resource,
                        "expected": "denied",
                        "observed": "allowed",
                        "denied_control_confirmed": observation.control_confirmed,
                        "credentials_included": False,
                        "response_body_included": False,
                        "customer_records_included": False,
                    },
                    "remediation": "Enforce authorization for this role/resource boundary and re-run the same declared matrix with a denied control.",
                    "external_id": f"{item.role}:{item.resource}",
                }
            )

    status = "completed" if incomplete == 0 else "partial"
    notes = [
        "Access-matrix input is execution-neutral and accepts no credentials, response bodies or customer records.",
        "Unexpected allows remain candidate observations until a separate workbench verification step proves impact.",
    ]
    normalized = normalize_adapter_result(
        {
            "schema": ADAPTER_SCHEMA,
            "adapter": {"id": "access-matrix", "version": version.strip()},
            "status": status,
            "coverage": {
                "objects_tested": completed,
                "objects_total": len(expected),
                "notes": notes,
            },
            "findings": findings,
            **(
                {"error": f"{incomplete} declared matrix case(s) were not completed"}
                if incomplete
                else {}
            ),
        },
        asset_key=asset_key,
    )
    normalized["cases"] = cases
    normalized["matrix_summary"] = {
        "declared_cases": len(expected),
        "completed_cases": completed,
        "incomplete_cases": incomplete,
        "mismatches": sum(1 for case in cases if case["result"] == "mismatch"),
        "unexpected_allows": len(findings),
    }
    return normalized
