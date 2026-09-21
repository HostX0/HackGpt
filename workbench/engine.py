"""Bounded native checks, explicit scope, independently verifiable evidence.

No legacy modules, subprocesses, arbitrary commands, payloads or third-party scanners
are loaded by this package. Missing coverage is represented, not silently passed.
"""
import copy
import hashlib
import html
import http.client
import ipaddress
import json
import queue
import re
import socket
import ssl
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlsplit

from . import __version__
from .lab import CanaryLab

LIMITATION = "No finding is not a security guarantee. A failed or skipped verification does not prove that exploitation is impossible."
DEFAULT_ASSESSMENT_DEADLINE_SECONDS = 45


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def seal(report):
    report.pop("integrity", None)
    report["integrity"] = {"algorithm": "sha256", "report_sha256": digest(report), "signed": False}
    return report


def verify_integrity(report):
    if not isinstance(report, dict):
        return False
    value = copy.deepcopy(report)
    integrity = value.pop("integrity", {})
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256" or integrity.get("signed") is not False:
        return False
    if integrity.get("report_sha256") != digest(value):
        return False
    previous = "0" * 64
    for index, event in enumerate(value.get("events", []), 1):
        if not isinstance(event, dict):
            return False
        item = dict(event)
        event_hash = item.pop("sha256", None)
        if item.get("sequence") != index or item.get("previous_sha256") != previous or event_hash != digest(item):
            return False
        previous = event_hash
    for finding in value.get("findings", []):
        if not isinstance(finding, dict) or finding.get("evidence_sha256") != digest(finding.get("evidence")):
            return False
    return True


class DeadlineExceeded(TimeoutError):
    pass


class Deadline:
    """Monotonic wall-clock budget shared by bounded native/model operations."""

    def __init__(self, seconds):
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not 0 < seconds <= 300:
            raise ValueError("deadline must be from 0 to 300 seconds")
        self.seconds = float(seconds)
        self.expires_at = time.monotonic() + self.seconds

    def remaining(self, cap=None):
        value = self.expires_at - time.monotonic()
        if value <= 0:
            raise DeadlineExceeded("Assessment wall-clock deadline exceeded")
        if cap is not None:
            value = min(value, float(cap))
        return max(value, 0.001)


@dataclass(frozen=True)
class Scope:
    target: str
    mode: str
    approved: bool
    authorization: str
    model: str
    use_ai: bool
    lab: bool
    allow_cloud: bool = False

    @classmethod
    def parse(cls, data):
        if not isinstance(data, dict):
            raise ValueError("An assessment must be a JSON object")
        if data.get("authorized") is not True:
            raise ValueError("Explicit authorization is required")
        authorization = data.get("authorization", "")
        if not isinstance(authorization, str) or not 3 <= len(authorization.strip()) <= 160:
            raise ValueError("Provide a non-secret authorization reference, 3 to 160 characters")
        mode = data.get("mode", "analyst")
        if mode not in ("analyst", "verify"):
            raise ValueError("Unknown assessment mode")
        approved = data.get("approve_verification") is True
        if mode == "verify" and not approved:
            raise ValueError("Controlled verification needs separate approval")
        target = data.get("target", "lab")
        if not isinstance(target, str) or not target or len(target) > 2048:
            raise ValueError("Invalid target")
        lab = target == "lab"
        if not lab:
            validate_url(target)
        model = data.get("model", "")
        if not isinstance(model, str) or len(model) > 120:
            raise ValueError("Invalid model name")
        use_ai = data.get("use_ai", False)
        if type(use_ai) is not bool:
            raise ValueError("use_ai must be boolean")
        if use_ai and (not model or not re.fullmatch(r"[A-Za-z0-9_./:-]+", model)):
            raise ValueError("Choose a model available through Ollama")
        allow_cloud = data.get("allow_cloud", False)
        if type(allow_cloud) is not bool:
            raise ValueError("allow_cloud must be boolean")
        if allow_cloud and not use_ai:
            raise ValueError("Cloud processing approval requires AI to be enabled")
        if use_ai and "cloud" in model.lower() and not allow_cloud:
            raise ValueError("A cloud-tagged model requires explicit cloud-processing approval")
        return cls(target, mode, approved, authorization.strip(), model, use_ai, lab, allow_cloud)


def validate_url(url):
    if any(ord(c) < 33 or ord(c) == 127 for c in url) or "\\" in url:
        raise ValueError("Whitespace, control characters and backslashes are not allowed")
    try:
        parsed = urlsplit(url)
        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise ValueError("Malformed target URL") from exc
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use an explicit http or https URL")
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError("Credentials, queries and fragments are not accepted in scope URLs")
    if port not in (80, 443):
        raise ValueError("This milestone supports public web ports 80 and 443 only")
    if "%" in parsed.netloc or not parsed.path.isascii():
        raise ValueError("Use an unambiguous host and percent-encoded ASCII path")
    return parsed


def _resolve_bounded(resolver, host, port, deadline, cancel=None):
    if deadline is None:
        return resolver(host, port, type=socket.SOCK_STREAM)
    result_queue = queue.Queue(maxsize=1)

    def worker():
        try:
            result_queue.put((True, resolver(host, port, type=socket.SOCK_STREAM)), block=False)
        except BaseException as exc:
            try:
                result_queue.put((False, exc), block=False)
            except queue.Full:
                pass

    threading.Thread(target=worker, name="hackgpt-bounded-resolver", daemon=True).start()
    while True:
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        try:
            ok, value = result_queue.get(timeout=min(0.05, deadline.remaining()))
            break
        except queue.Empty:
            continue
    if not ok:
        raise value
    return value


def public_addresses(host, port, resolver=None, deadline=None, cancel=None):
    resolver = resolver or socket.getaddrinfo
    results = _resolve_bounded(resolver, host, port, deadline, cancel)
    addresses = []
    for result in results:
        raw = result[4][0]
        address = ipaddress.ip_address(raw)
        if not address.is_global or (address.version == 6 and (address.ipv4_mapped or address.sixtofour or address.teredo or address in ipaddress.ip_network("64:ff9b::/96"))):
            raise ValueError("Target resolves outside the permitted public address space")
        if raw not in addresses:
            addresses.append(raw)
    if not addresses:
        raise ValueError("Target did not resolve")
    return addresses


def inspect_remote(url, deadline=None, cancel=None):
    parsed = validate_url(url)
    host = parsed.hostname.encode("idna").decode("ascii")
    port = parsed.port if parsed.port is not None else (443 if parsed.scheme == "https" else 80)
    address = public_addresses(host, port, deadline=deadline, cancel=cancel)[0]
    timeout = deadline.remaining(8) if deadline is not None else 8
    if cancel is not None and cancel.is_set():
        raise Cancelled()
    sock = socket.create_connection((address, port), timeout=timeout)
    holder = {"socket": sock}
    watcher_stop = threading.Event()

    def cancel_watcher():
        while not watcher_stop.wait(0.025):
            if cancel is not None and cancel.is_set():
                current = holder.get("socket")
                if current is not None:
                    try:
                        current.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    try:
                        current.close()
                    except OSError:
                        pass
                return

    watcher = None
    if cancel is not None:
        watcher = threading.Thread(target=cancel_watcher, name="hackgpt-http-cancel", daemon=True)
        watcher.start()
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        if parsed.scheme == "https":
            if deadline is not None:
                sock.settimeout(deadline.remaining(8))
            sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
            holder["socket"] = sock
        if deadline is not None:
            sock.settimeout(deadline.remaining(8))
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        connection.sock = sock
        connection.request("HEAD", parsed.path or "/", headers={"User-Agent": "HackGPT-Workbench/" + __version__, "Connection": "close"})
        if deadline is not None:
            sock.settimeout(deadline.remaining(8))
        response = connection.getresponse()
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        headers = {}
        allowed = {"content-type", "content-security-policy", "x-frame-options", "strict-transport-security", "x-content-type-options", "referrer-policy"}
        for name, value in response.getheaders():
            if name.lower() in allowed:
                headers[name.lower()] = value[:2048]
        return {"status": response.status, "headers": headers, "resolved_ip": address, "method": "HEAD", "redirect_followed": False}
    except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
        if cancel is not None and cancel.is_set():
            raise Cancelled() from exc
        raise
    finally:
        watcher_stop.set()
        connection.close()
        try:
            sock.close()
        except OSError:
            pass
        if watcher is not None:
            watcher.join(timeout=0.2)


def new_report(scope, deadline_seconds=DEFAULT_ASSESSMENT_DEADLINE_SECONDS):
    return {
        "schema_version": "1.0", "engine_version": __version__, "id": uuid.uuid4().hex,
        "started_at": now(), "finished_at": None, "status": "running", "mode": scope.mode,
        "target": "lab://ephemeral-authorization-fixture" if scope.lab else scope.target,
        "environment": "synthetic_lab" if scope.lab else "authorized_public_web",
        "authorization": scope.authorization, "verification_approved": scope.approved,
        "findings": [], "checks": [], "events": [], "verdict": "pending",
        "execution_budget": {"wall_clock_seconds": float(deadline_seconds), "native_http_requests": 3,
                             "enforcement": "native network/model socket operations plus assessment checkpoints"},
        "ai": {"status": "not_requested", "interpretation": None,
               "provider": "ollama" if scope.use_ai else None,
               "model": scope.model if scope.use_ai else None,
               "processing_policy": "cloud_allowed" if scope.allow_cloud else "local_only",
               "cloud_processing_approved": scope.allow_cloud,
               "data_disclosure": "Normalized rule IDs, severities, verification states, remediation, check status and limitations only; target URLs, authorization notes, headers, bodies and credentials are omitted."},
        "limitations": [LIMITATION, "Native HTTP baseline only; ZAP, Nuclei, Semgrep, Trivy and Nmap adapters are not integrated in this milestone.", "Authentication, business logic and broad application coverage require additional tests.", "Checksums detect changes relative to a trusted digest; they are not signatures or proof of origin."],
    }


class Cancelled(Exception):
    pass


class Assessment:
    def __init__(self, scope, cancel=None, notify=None, remote_reader=None, ai_client=None, deadline_seconds=DEFAULT_ASSESSMENT_DEADLINE_SECONDS):
        self.scope = scope
        self.cancel = cancel or threading.Event()
        self.notify = notify or (lambda report: None)
        self.remote_reader = remote_reader
        self.ai_client = ai_client
        self.deadline = Deadline(deadline_seconds)
        self.report = new_report(scope, deadline_seconds)
        self.requests_used = 0
        self.executed = set()

    def emit(self, kind, message, details=None, *, publish=True):
        previous = self.report["events"][-1]["sha256"] if self.report["events"] else "0" * 64
        event = {"sequence": len(self.report["events"]) + 1, "at": now(), "kind": kind, "message": message, "details": details or {}, "previous_sha256": previous}
        event["sha256"] = digest(event)
        self.report["events"].append(event)
        if publish:
            self.notify(copy.deepcopy(self.report))

    def checkpoint(self):
        if self.cancel.is_set():
            raise Cancelled()
        self.deadline.remaining()

    def budget(self, amount):
        self.checkpoint()
        if self.requests_used + amount > 3:
            raise ValueError("Per-assessment native request budget exceeded")
        self.requests_used += amount

    def add_finding(self, rule, title, severity, state, evidence, remediation):
        fingerprint = digest({"rule": rule, "target": self.report["target"]})
        finding = {"id": fingerprint[:16], "fingerprint": fingerprint, "rule": rule, "title": title,
                   "severity": severity, "verification": state, "evidence": evidence,
                   "evidence_sha256": digest(evidence), "remediation": remediation,
                   "source": "native/" + __version__, "observed_at": now()}
        self.report["findings"].append(finding)
        self.emit("finding", title, {"finding_id": finding["id"], "verification": state})

    def _record_adapter_result(self, result, execution_receipt=None):
        """Merge a normalized adapter result without granting it verification authority."""
        if not isinstance(result, dict) or result.get("verification_authority") != "workbench_only":
            raise ValueError("Adapter result did not pass the workbench trust contract")
        adapter = result.get("adapter") or {}
        adapter_id = adapter.get("id")
        if not isinstance(adapter_id, str):
            raise ValueError("Adapter result is missing a stable adapter id")
        status = result.get("status")
        check_status = "inconclusive" if status == "partial" else status
        check = {
            "tool": adapter_id,
            "status": check_status,
            "adapter": copy.deepcopy(adapter),
            "coverage": copy.deepcopy(result.get("coverage", {})),
        }
        if execution_receipt is not None:
            from .execution_receipts import normalize_execution_receipt
            receipt = normalize_execution_receipt(copy.deepcopy(execution_receipt))
            if receipt["result"] != result:
                raise ValueError("Execution receipt result does not match the adapter result")
            check["execution_receipt"] = receipt
        if result.get("error"):
            check["reason"] = result["error"]
        self.report["checks"].append(check)
        for finding in result.get("findings", []):
            if finding.get("verification") != "candidate":
                raise ValueError("Execution adapters cannot self-promote verification state")
            item = copy.deepcopy(finding)
            item["observed_at"] = now()
            self.report["findings"].append(item)
            self.emit("finding", item["title"], {"finding_id": item["id"], "verification": "candidate", "adapter": adapter_id})
        event_kind = "tool_completed" if status == "completed" else ("tool_inconclusive" if status == "partial" else "tool_" + str(status))
        details = {"adapter": adapter_id, "status": status, "findings": len(result.get("findings", []))}
        if execution_receipt is not None:
            details["usage"] = copy.deepcopy(execution_receipt["usage"])
        self.emit(event_kind, "Adapter execution recorded", details)

    def baseline(self, lab):
        self.budget(1)
        self.emit("tool_started", "Inspecting HTTP response metadata; no redirects or body collection")
        if not lab:
            from .registry import ExecutionRegistry, RegistryPolicy
            timeout = max(1, min(15, int(self.deadline.remaining(15))))
            registry = ExecutionRegistry(RegistryPolicy(max_effect="passive", allow_filesystem=False, allow_network=True))
            web_reader = self.remote_reader
            if web_reader is not None:
                original_reader = web_reader
                def web_reader(target):
                    value = original_reader(target)
                    if isinstance(value, dict):
                        value = dict(value)
                        value.setdefault("method", "HEAD")
                        value.setdefault("redirect_followed", False)
                    return value
            receipt = registry.execute_with_receipt(
                "native-web-headers",
                {"target": self.scope.target, "asset_key": digest({"target": self.report["target"], "environment": self.report["environment"]})[:32], "timeout_seconds": timeout},
                cancel=self.cancel,
                web_reader=web_reader,
            )
            self.checkpoint()
            self._record_adapter_result(receipt["result"], execution_receipt=receipt)
            return

        status, headers, _ = lab.request("/", "HEAD")
        result = {"status": status, "headers": headers, "method": "HEAD", "redirect_followed": False, "resolved_ip": "127.0.0.1 (owned ephemeral fixture)"}
        self.checkpoint()
        status = result["status"]
        if not 200 <= status < 300:
            self.report["checks"].append({"tool": "http_baseline", "status": "inconclusive", "reason": "Response is not a successful representation; redirects are intentionally not followed", "evidence": result})
            self.emit("tool_inconclusive", "Baseline could not assess a successful representation", {"http_status": status})
            return
        self.report["checks"].append({"tool": "http_baseline", "status": "completed", "evidence": result})
        headers = result["headers"]
        if "text/html" in headers.get("content-type", "").lower():
            checks = [("content-security-policy", "CSP header not observed", "Define a Content Security Policy appropriate to the application; verify browser behavior and compatibility."), ("x-content-type-options", "Content-type hardening header not observed", "Consider X-Content-Type-Options: nosniff with correct response content types.")]
            for header, title, remediation in checks:
                if header not in headers:
                    self.add_finding("header/" + header, title, "low", "observed_only", {"method": "HEAD", "http_status": status, "absent_header": header, "scope": "this response only", "impact_proven": False}, remediation)
        self.emit("tool_completed", "HTTP baseline recorded; header observations do not establish exploitation")

    def execute_action(self, name, arguments, lab):
        self.checkpoint()
        if name != "verify_lab_canary" or arguments != {}:
            raise ValueError("Action or arguments outside the fixed allowlist")
        if self.scope.mode != "verify" or not self.scope.approved or not self.scope.lab or lab is None:
            raise ValueError("Verification is restricted to an approved, owned synthetic lab")
        if name in self.executed:
            raise ValueError("Duplicate actions are not allowed")
        self.executed.add(name)
        self.budget(2)
        self.emit("tool_started", "Checking synthetic authorization canary against a denied control")
        proof = lab.prove()
        self.checkpoint()
        demonstrated = proof["control_status"] == 401 and proof["synthetic_marker_matched"]
        self.report["checks"].append({"tool": name, "status": "completed", "result": "verified_in_lab" if demonstrated else "not_demonstrated", "evidence": proof})
        if demonstrated:
            self.add_finding("lab/missing-authorization", "Synthetic record accessible without authorization", "high", "verified_in_lab", proof, "Enforce authorization on the record route; test both denied and allowed cases. This evidence applies ONLY to the disposable fixture.")
            self.emit("verification", "Synthetic canary demonstrated impact inside the owned lab", {"scope": "lab_only"})
        else:
            self.emit("verification", "The lab verification did not demonstrate the expected condition", {"scope": "lab_only"})

    def run(self):
        lab = CanaryLab() if self.scope.lab else None
        if lab:
            lab.start()
        try:
            self.emit("started", "Assessment started", {"mode": self.scope.mode, "target_kind": "synthetic_lab" if self.scope.lab else "authorized_web"})
            self.checkpoint()
            self.baseline(lab)
            self.checkpoint()
            if self.scope.mode == "verify":
                if self.scope.lab:
                    if self.ai_client:
                        action = self.ai_client.plan(self.context(), self.scope.model)
                        self.checkpoint()
                        if action:
                            self.execute_action(action["name"], action.get("arguments", {}), lab)
                        else:
                            self.report["checks"].append({"tool": "model_action", "status": "inconclusive", "reason": "The model did not request an allowlisted verification action"})
                    else:
                        self.execute_action("verify_lab_canary", {}, lab)
                else:
                    self.report["checks"].append({"tool": "external_verification", "status": "skipped", "reason": "External exploit verification is not implemented in this milestone"})
                    self.emit("tool_skipped", "External verification is unavailable; no exploitation was attempted")
            if self.scope.use_ai and self.ai_client:
                self.checkpoint()
                self.report["ai"]["status"] = "requested"
                try:
                    self.report["ai"]["interpretation"] = self.ai_client.summarize(self.context(), self.scope.model)
                    self.report["ai"]["status"] = "completed"
                except Exception as exc:
                    self.report["ai"]["status"] = "failed"
                    self.report["ai"]["error"] = str(exc)[:300]
                    self.emit("ai_failed", "AI interpretation failed; deterministic evidence remains authoritative")
            elif self.scope.use_ai:
                self.report["ai"]["status"] = "unavailable"
            failed = [check for check in self.report["checks"] if check.get("status") in ("failed", "error", "inconclusive")]
            skipped = [check for check in self.report["checks"] if check.get("status") == "skipped"]
            if failed or skipped:
                self.report["status"] = "partial"
                self.report["verdict"] = "inconclusive"
            else:
                self.report["status"] = "completed"
                self.report["verdict"] = "findings_recorded" if self.report["findings"] else "no_findings_in_executed_checks"
            self.report["finished_at"] = now()
            self.emit("finished", "Assessment finalized", {"verdict": self.report["verdict"]}, publish=False)
        except Cancelled:
            self.report["status"] = "cancelled"
            self.report["verdict"] = "inconclusive"
            self.report["finished_at"] = now()
            self.emit("cancelled", "Assessment cancelled; partial evidence is not a clean result", publish=False)
        except DeadlineExceeded:
            self.report["status"] = "timed_out"
            self.report["verdict"] = "inconclusive"
            self.report["finished_at"] = now()
            self.emit("timed_out", "Assessment deadline expired; incomplete work is not a clean result", publish=False)
        except Exception as exc:
            self.report["status"] = "failed"
            self.report["verdict"] = "inconclusive"
            self.report["finished_at"] = now()
            self.report["checks"].append({"tool": "engine", "status": "failed", "reason": str(exc)[:500]})
            self.emit("failed", "Assessment failed; no security conclusion is possible", publish=False)
        finally:
            if lab:
                lab.stop()
        return seal(self.report)

    def context(self):
        findings = [{"rule": f["rule"], "severity": f["severity"], "verification": f["verification"], "remediation": f["remediation"]} for f in self.report["findings"]]
        checks = [{"tool": c.get("tool"), "status": c.get("status"), "reason": c.get("reason")} for c in self.report["checks"]]
        return {"mode": self.scope.mode, "environment": self.report["environment"], "findings": findings, "checks": checks, "limitations": self.report["limitations"]}


def markdown(report):
    target = html.escape(str(report.get("target", "")))
    lines = ["# HackGPT Evidence Workbench Report", "", f"Run ID: `{report.get('id', '')}`", f"Target: `{target}`", f"Status: **{report.get('status', '')}**", f"Verdict: **{report.get('verdict', '')}**", "", "## Findings"]
    if not report.get("findings"):
        lines.append("No findings were recorded by the checks that actually executed. This is not a security guarantee.")
    for finding in report.get("findings", []):
        lines += ["", f"### {html.escape(str(finding.get('title', 'Finding')))}", f"- Severity: {finding.get('severity')}", f"- Verification: {finding.get('verification')}", f"- Rule: `{html.escape(str(finding.get('rule', '')))}`", f"- Evidence SHA-256: `{finding.get('evidence_sha256')}`", f"- Remediation: {html.escape(str(finding.get('remediation', '')))}"]
    lines += ["", "## Coverage"]
    for check in report.get("checks", []):
        lines.append(f"- `{html.escape(str(check.get('tool', 'unknown')))}`: {html.escape(str(check.get('status', 'unknown')))}" + (f" — {html.escape(str(check.get('reason')))}" if check.get("reason") else ""))
    lines += ["", "## Limitations"] + [f"- {html.escape(str(item))}" for item in report.get("limitations", [])]
    integrity = report.get("integrity", {})
    lines += ["", "## Integrity", f"Report SHA-256: `{integrity.get('report_sha256', '')}`", "Signed: no"]
    return "\n".join(lines) + "\n"
