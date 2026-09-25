"""Bounded native web-response metadata adapter.

The adapter performs exactly one scoped HEAD request, never follows redirects and never
reads a response body. It is intentionally small: candidate header observations are
not exploit proof and do not broaden authorization beyond the supplied target URL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from .contracts import ADAPTER_SCHEMA, normalize_adapter_result
from .engine import Deadline, validate_url
from .execution_contracts import EXECUTION_SCHEMA, normalize_execution_declaration
from .network_transport import inspect_remote

ADAPTER_ID = "native-web-headers"
ADAPTER_VERSION = "1"


@dataclass(frozen=True)
class WebHeaderPolicy:
    """Operator-owned limits for the passive native web adapter."""

    timeout_seconds: int = 15
    max_requests: int = 1

    def __post_init__(self) -> None:
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, int)
            or not 1 <= self.timeout_seconds <= 60
        ):
            raise ValueError("timeout_seconds must be an integer from 1 to 60")
        if self.max_requests != 1:
            raise ValueError(
                "native web header adapter is fixed to exactly one request"
            )


class WebHeaderAdapter:
    """One-request, body-free security-header observation adapter."""

    identity = {"id": ADAPTER_ID, "version": ADAPTER_VERSION}

    def __init__(self, policy: WebHeaderPolicy | None = None):
        self.policy = policy or WebHeaderPolicy()

    def execution_declaration(self) -> dict[str, Any]:
        return normalize_execution_declaration(
            {
                "schema": EXECUTION_SCHEMA,
                "adapter": dict(self.identity),
                "launcher": "native_python",
                "effect_level": "passive",
                "filesystem": "none",
                "network": "scoped_target",
                "subprocess": False,
                "writes": False,
                "follows_symlinks": False,
                "limits": {
                    "max_objects": 1,
                    "max_requests": 1,
                    "timeout_seconds": self.policy.timeout_seconds,
                },
                "coverage_unit": "declared_http_response",
            }
        )

    def run(
        self,
        target: str,
        *,
        asset_key: str,
        cancel=None,
        reader: Callable[[str], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Inspect one explicitly declared URL and normalize candidate observations.

        `reader` exists only as an injection seam for owned synthetic fixtures/tests. The
        production path uses the workbench's DNS-pinned, no-redirect, HEAD-only reader.
        """
        validate_url(target)
        if reader is None:
            result = inspect_remote(
                target, deadline=Deadline(self.policy.timeout_seconds), cancel=cancel
            )
        else:
            result = reader(target)
        result = self._validate_result(result)

        status = result["status"]
        headers = result["headers"]
        findings: list[dict[str, Any]] = []
        notes = [
            "Exactly one HEAD response was inspected; redirects and response bodies are not followed or collected.",
            "Header observations are candidates only and do not demonstrate exploitability.",
        ]
        adapter_status = "completed"
        if not 200 <= status < 300:
            adapter_status = "partial"
            notes.append(
                "The scoped response was not 2xx, so HTML hardening coverage is inconclusive for the intended representation."
            )
        elif "text/html" not in headers.get("content-type", "").lower():
            notes.append(
                "The scoped response was not identified as HTML; HTML-specific header rules were not applied."
            )
        else:
            rules = (
                (
                    "content-security-policy",
                    "web/missing-content-security-policy",
                    "Content Security Policy header not observed",
                    "medium",
                    "Define a Content Security Policy appropriate to the application and validate it against required browser behavior.",
                ),
                (
                    "x-content-type-options",
                    "web/missing-content-type-options",
                    "X-Content-Type-Options header not observed",
                    "low",
                    "Return X-Content-Type-Options: nosniff with accurate response content types where appropriate.",
                ),
            )
            for header, rule, title, severity, remediation in rules:
                if header not in headers:
                    findings.append(
                        {
                            "rule": rule,
                            "title": title,
                            "severity": severity,
                            "confidence": 0.95,
                            "external_id": header,
                            "evidence": {
                                "method": "HEAD",
                                "http_status": status,
                                "absent_header": header,
                                "scope": "declared response only",
                                "body_read": False,
                                "redirect_followed": False,
                                "impact_proven": False,
                            },
                            "remediation": remediation,
                        }
                    )

        payload = {
            "schema": ADAPTER_SCHEMA,
            "adapter": dict(self.identity),
            "status": adapter_status,
            "coverage": {"objects_tested": 1, "objects_total": 1, "notes": notes},
            "findings": findings,
            "error": None,
        }
        return normalize_adapter_result(payload, asset_key=asset_key)

    @staticmethod
    def _validate_result(result: Any) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ValueError("web adapter reader returned an invalid result")
        allowed = {"status", "headers", "resolved_ip", "method", "redirect_followed"}
        if set(result) - allowed:
            raise ValueError("web adapter reader returned unsupported fields")
        status = result.get("status")
        if (
            isinstance(status, bool)
            or not isinstance(status, int)
            or not 100 <= status <= 599
        ):
            raise ValueError("web adapter reader returned an invalid status")
        headers = result.get("headers")
        if not isinstance(headers, dict) or len(headers) > 64:
            raise ValueError("web adapter reader returned invalid headers")
        clean_headers: dict[str, str] = {}
        for name, value in headers.items():
            if not isinstance(name, str) or not isinstance(value, str):
                raise ValueError("web adapter headers must be text")
            lower = name.lower().strip()
            if lower not in {
                "content-type",
                "content-security-policy",
                "x-frame-options",
                "strict-transport-security",
                "x-content-type-options",
                "referrer-policy",
            }:
                raise ValueError("web adapter reader returned an unapproved header")
            if (
                len(value) > 2048
                or any(ord(ch) < 32 and ch not in "\t" for ch in value)
                or any(ord(ch) == 127 for ch in value)
            ):
                raise ValueError("web adapter reader returned an unsafe header value")
            clean_headers[lower] = value
        if (
            result.get("method") != "HEAD"
            or result.get("redirect_followed") is not False
        ):
            raise ValueError(
                "web adapter reader violated the HEAD/no-redirect contract"
            )
        return {"status": status, "headers": clean_headers}
