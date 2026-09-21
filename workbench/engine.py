"""Bounded native checks, explicit scope, independently verifiable evidence.

No legacy modules, subprocesses, arbitrary commands, payloads or third-party scanners
are loaded by this package. Missing coverage is represented, not silently passed.
"""
import copy
import hashlib
import http.client
import ipaddress
import json
import re
import socket
import ssl
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlsplit

from . import __version__
from .lab import CanaryLab

LIMITATION = "No finding is not a security guarantee. A failed or skipped verification does not prove that exploitation is impossible."


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
    value = copy.deepcopy(report)
    integrity = value.pop("integrity", {})
    if integrity.get("report_sha256") != digest(value):
        return False
    previous = "0" * 64
    for event in value.get("events", []):
        item = dict(event)
        event_hash = item.pop("sha256", None)
        if item.get("previous_sha256") != previous or event_hash != digest(item):
            return False
        previous = event_hash
    return True


@dataclass(frozen=True)
class Scope:
    target: str
    mode: str
    approved: bool
    authorization: str
    model: str
    use_ai: bool
    lab: bool

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
            raise ValueError("Choose an installed local Ollama model")
        if use_ai and "cloud" in model.lower():
            raise ValueError("Cloud-tagged models are not allowed in this local workbench")
        return cls(target, mode, approved, authorization.strip(), model, use_ai, lab)


def validate_url(url):
    if any(ord(c) < 33 for c in url) or "\\" in url:
        raise ValueError("Whitespace, control characters and backslashes are not allowed")
    try:
        parsed = urlsplit(url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
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


def public_addresses(host, port, resolver=None):
    """Resolve once and reject *all* mixed/private results before opening a socket."""
    resolver = resolver or socket.getaddrinfo
    results = resolver(host, port, type=socket.SOCK_STREAM)
    addresses = []
    for result in results:
        raw = result[4][0]
        address = ipaddress.ip_address(raw)
        # IPv6 translation/tunnel addresses complicate private-range enforcement.
        if not address.is_global or (address.version == 6 and (address.ipv4_mapped or address.sixtofour or address.teredo or address in ipaddress.ip_network("64:ff9b::/96"))):
            raise ValueError("Target resolves outside the permitted public address space")
        if raw not in addresses:
            addresses.append(raw)
    if not addresses:
        raise ValueError("Target did not resolve")
    return addresses


def inspect_remote(url):
    """One HEAD request, no redirects/proxies/body capture; socket pinned after DNS."""
    parsed = validate_url(url)
    host = parsed.hostname.encode("idna").decode("ascii")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    address = public_addresses(host, port)[0]
    sock = socket.create_connection((address, port), timeout=8)
    connection = http.client.HTTPConnection(host, port, timeout=8)
    try:
        if parsed.scheme == "https":
            sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
        connection.sock = sock
        connection.request("HEAD", parsed.path or "/", headers={"User-Agent": "HackGPT-Workbench/" + __version__, "Connection": "close"})
        response = connection.getresponse()
        headers = {}
        allowed = {"content-type", "content-security-policy", "x-frame-options", "strict-transport-security", "x-content-type-options", "referrer-policy"}
        for name, value in response.getheaders():
            if name.lower() in allowed:
                headers[name.lower()] = value[:2048]
        return {"status": response.status, "headers": headers, "resolved_ip": address, "method": "HEAD", "redirect_followed": False}
    finally:
        connection.close()
        sock.close()


def new_report(scope):
    return {
        "schema_version": "1.0", "engine_version": __version__, "id": uuid.uuid4().hex,
        "started_at": now(), "finished_at": None, "status": "running", "mode": scope.mode,
        "target": "lab://ephemeral-authorization-fixture" if scope.lab else scope.target,
        "environment": "synthetic_lab" if scope.lab else "authorized_public_web",
        "authorization": scope.authorization, "verification_approved": scope.approved,
        "findings": [], "checks": [], "events": [], "verdict": "pending",
        "ai": {"status": "not_requested", "interpretation": None},
        "limitations": [LIMITATION, "Native HTTP baseline only; ZAP, Nuclei, Semgrep, Trivy and Nmap adapters are not integrated in this milestone.", "Authentication, business logic and broad application coverage require additional tests.", "Checksums detect changes relative to a trusted digest; they are not signatures or proof of origin."],
    }


class Cancelled(Exception):
    pass


class Assessment:
    def __init__(self, scope, cancel=None, notify=None, remote_reader=None, ai_client=None):
        self.scope = scope
        self.cancel = cancel or threading.Event()
        self.notify = notify or (lambda report: None)
        self.remote_reader = remote_reader or inspect_remote
        self.ai_client = ai_client
        self.report = new_report(scope)
        self.requests_used = 0
        self.executed = set()

    def emit(self, kind, message, details=None):
        previous = self.report["events"][-1]["sha256"] if self.report["events"] else "0" * 64
        event = {"sequence": len(self.report["events"]) + 1, "at": now(), "kind": kind, "message": message, "details": details or {}, "previous_sha256": previous}
        event["sha256"] = digest(event)
        self.report["events"].append(event)
        self.notify(copy.deepcopy(self.report))

    def checkpoint(self):
        if self.cancel.is_set():
            raise Cancelled()

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

    def baseline(self, lab):
        self.budget(1)
        self.emit("tool_started", "Inspecting HTTP response metadata; no redirects or body collection")
        if lab:
            status, headers, _ = lab.request("/", "HEAD")
            result = {"status": status, "headers": headers, "method": "HEAD", "redirect_followed": False, "resolved_ip": "127.0.0.1 (owned ephemeral fixture)"}
        else:
            result = self.remote_reader(self.scope.target)
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
        self.emit("tool_completed", "Synthetic proof completed", {"demonstrated": demonstrated, "external_target_tested": False})
        return {"demonstrated": demonstrated, "environment": "synthetic_lab"}

    def run(self, fixed_lab=False):
        lab = None
        try:
            self.emit("scope_approved", "Scope and authorization recorded", {"mode": self.scope.mode, "max_http_requests": 3})
            self.checkpoint()
            if self.scope.lab:
                lab = CanaryLab(fixed=fixed_lab).__enter__()
            self.baseline(lab)
            if self.scope.mode == "verify":
                if not self.scope.lab:
                    self.report["checks"].append({"tool": "controlled_verification", "status": "skipped", "reason": "No approved external verification adapter is implemented in this milestone"})
                    self.emit("tool_skipped", "External exploit verification is not implemented; no exploitation attempted")
                elif not self.scope.use_ai:
                    self.execute_action("verify_lab_canary", {}, lab)
            if self.scope.use_ai:
                self.checkpoint()
                self.report["ai"]["status"] = "running"
                self.emit("ai_started", "Requesting local model interpretation; evidence remains immutable")
                try:
                    if self.ai_client is None:
                        from .ollama import Ollama
                        self.ai_client = Ollama(self.scope.model)
                    if self.scope.mode == "verify" and self.scope.lab:
                        decisions = self.ai_client.plan(lambda name, arguments: self.execute_action(name, arguments, lab), self.report, self.checkpoint)
                        self.report["ai"]["decisions"] = decisions
                        if "verify_lab_canary" not in self.executed:
                            self.report["checks"].append({"tool": "verify_lab_canary", "status": "skipped", "reason": "Model did not request the approved verification action"})
                    self.checkpoint()
                    self.report["ai"]["interpretation"] = self.ai_client.summarize(copy.deepcopy(self.report))
                    self.checkpoint()
                    self.report["ai"]["status"] = "completed"
                    self.emit("ai_completed", "AI commentary stored separately from deterministic findings")
                except Cancelled:
                    raise
                except Exception as exc:
                    self.report["ai"]["status"] = "unavailable"
                    self.report["ai"]["error_type"] = type(exc).__name__
                    if self.scope.mode == "verify" and self.scope.lab and "verify_lab_canary" not in self.executed:
                        self.report["checks"].append({"tool": "verify_lab_canary", "status": "error", "reason": "AI orchestration unavailable; verification not executed"})
                    self.emit("ai_unavailable", "Local AI unavailable or response invalid; no simulated AI result", {"error_type": type(exc).__name__})
            self.checkpoint()
            incomplete = any(c["status"] in ("skipped", "error", "inconclusive") for c in self.report["checks"]) or self.report["ai"]["status"] == "unavailable"
            self.report["status"] = "partial" if incomplete else "completed"
            if any(f["verification"] == "verified_in_lab" for f in self.report["findings"]):
                self.report["verdict"] = "verified_in_synthetic_lab_only"
            elif incomplete:
                self.report["verdict"] = "inconclusive"
            elif self.report["findings"]:
                self.report["verdict"] = "observations_need_context"
            else:
                self.report["verdict"] = "no_findings_in_executed_checks"
        except Cancelled:
            self.report["status"], self.report["verdict"] = "cancelled", "inconclusive"
            if self.report["ai"]["status"] == "running":
                self.report["ai"]["status"] = "cancelled"
            self.emit("cancelled", "Cancellation honored; in-flight bounded I/O may finish before this checkpoint")
        except Exception as exc:
            self.report["status"], self.report["verdict"] = "error", "inconclusive"
            self.report["checks"].append({"tool": "assessment", "status": "error", "reason": type(exc).__name__})
            self.emit("error", "Assessment incomplete; no security conclusion", {"error_type": type(exc).__name__})
        finally:
            if lab:
                lab.__exit__(None, None, None)
            self.report["finished_at"] = now()
            self.report["http_requests_budgeted"] = self.requests_used
            self.emit("finished", "Assessment finished", {"status": self.report["status"], "verdict": self.report["verdict"]})
            seal(self.report)
        return copy.deepcopy(self.report)


def markdown(report):
    lines = ["# HackGPT Evidence Workbench report", "", "- Run: " + report["id"], "- Target: " + report["target"], "- Status: " + report["status"], "- Verdict: " + report["verdict"], "- Environment: " + report["environment"], "", "> " + LIMITATION, "", "## Findings"]
    for finding in report["findings"]:
        lines += ["", "### " + finding["title"], "Severity: " + finding["severity"], "Verification: " + finding["verification"], "Remediation: " + finding["remediation"], "", "Evidence SHA-256: " + finding["evidence_sha256"], "```json", json.dumps(finding["evidence"], indent=2), "```"]
    lines += ["", "## Coverage and execution", "```json", json.dumps(report["checks"], indent=2), "```", "", "## AI interpretation (not evidence)", "```json", json.dumps(report["ai"], indent=2), "```", "", "## Limitations"]
    lines += ["- " + item for item in report["limitations"]]
    lines += ["", "Report SHA-256 (unsigned): " + report.get("integrity", {}).get("report_sha256", "not finalized")]
    return "\n".join(lines)
