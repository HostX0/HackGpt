"""Bounded, read-only native project metadata adapter.

This adapter deliberately does not execute subprocesses, read file contents, follow
symlinks, or access the network. It inventories eligible project paths and reports
candidate exposure observations from filenames only. Secret values are never read.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from .contracts import ADAPTER_SCHEMA, normalize_adapter_result
from .execution_contracts import EXECUTION_SCHEMA, normalize_execution_declaration

ADAPTER_ID = "native-project-metadata"
ADAPTER_VERSION = "1"
MAX_FILES_LIMIT = 5000
MAX_DEPTH = 16
MAX_RELATIVE_PATH = 512
DEFAULT_EXCLUDED_DIRS = frozenset(
    {".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "__pycache__"}
)

_SECRET_FILENAMES = {
    ".env": (
        "project/exposed-env-file",
        "Environment file present in project tree",
        "medium",
    ),
    ".env.local": (
        "project/exposed-env-file",
        "Local environment file present in project tree",
        "medium",
    ),
    ".env.production": (
        "project/exposed-env-file",
        "Production environment file present in project tree",
        "high",
    ),
    "id_rsa": (
        "project/private-key-file",
        "Private-key filename present in project tree",
        "high",
    ),
    "id_ed25519": (
        "project/private-key-file",
        "Private-key filename present in project tree",
        "high",
    ),
    "credentials.json": (
        "project/credential-file",
        "Credential filename present in project tree",
        "high",
    ),
    "service-account.json": (
        "project/credential-file",
        "Service-account filename present in project tree",
        "high",
    ),
}
_SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks"}


@dataclass(frozen=True)
class ProjectScanPolicy:
    """Operator-owned execution limits for the native project adapter."""

    max_files: int = 1000
    max_depth: int = 12
    excluded_dirs: frozenset[str] = DEFAULT_EXCLUDED_DIRS
    timeout_seconds: int = 30

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_files, bool)
            or not isinstance(self.max_files, int)
            or not 1 <= self.max_files <= MAX_FILES_LIMIT
        ):
            raise ValueError(
                f"max_files must be an integer from 1 to {MAX_FILES_LIMIT}"
            )
        if (
            isinstance(self.max_depth, bool)
            or not isinstance(self.max_depth, int)
            or not 0 <= self.max_depth <= MAX_DEPTH
        ):
            raise ValueError(f"max_depth must be an integer from 0 to {MAX_DEPTH}")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, int)
            or not 1 <= self.timeout_seconds <= 120
        ):
            raise ValueError("timeout_seconds must be an integer from 1 to 120")
        if (
            not isinstance(self.excluded_dirs, frozenset)
            or len(self.excluded_dirs) > 64
        ):
            raise ValueError("excluded_dirs must be a bounded frozenset")
        for name in self.excluded_dirs:
            if (
                not isinstance(name, str)
                or not name
                or len(name) > 120
                or "/" in name
                or "\\" in name
                or name in {".", ".."}
                or any(ord(ch) < 32 or ord(ch) == 127 for ch in name)
            ):
                raise ValueError("invalid excluded directory name")


class ProjectMetadataAdapter:
    """Read-only filename metadata scanner with a closed execution declaration."""

    identity = {"id": ADAPTER_ID, "version": ADAPTER_VERSION}
    execution_template = {
        "schema": EXECUTION_SCHEMA,
        "adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION},
        "launcher": "native_python",
        "effect_level": "read_only",
        "filesystem": "read_only_metadata",
        "network": "none",
        "subprocess": False,
        "writes": False,
        "follows_symlinks": False,
        "limits": {"max_objects": 1000, "max_requests": 0, "timeout_seconds": 30},
        "coverage_unit": "eligible_project_files",
    }

    def __init__(self, policy: ProjectScanPolicy | None = None):
        self.policy = policy or ProjectScanPolicy()

    @staticmethod
    def _check_cancel(cancel) -> None:
        if cancel is not None and cancel.is_set():
            raise InterruptedError("project metadata scan cancelled")

    def run(self, root: str | os.PathLike[str], *, asset_key: str, cancel=None) -> dict:
        self._check_cancel(cancel)
        root_path = Path(root)
        if root_path.is_symlink():
            raise ValueError("project root must not be a symlink")
        try:
            resolved_root = root_path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise ValueError("project root is unavailable") from exc
        if not resolved_root.is_dir():
            raise ValueError("project root must be a directory")
        self._check_cancel(cancel)

        findings: list[dict] = []
        notes: list[str] = [
            "Native metadata-only scan: file contents were not read.",
            "Symlinks are not followed.",
        ]
        tested = 0
        expires_at = time.monotonic() + self.policy.timeout_seconds
        partial = False
        excluded_seen: set[str] = set()
        symlinks_skipped = 0
        errors = 0

        stack: list[tuple[Path, int]] = [(resolved_root, 0)]
        while stack:
            self._check_cancel(cancel)
            if time.monotonic() >= expires_at:
                partial = True
                notes.append(
                    "Cooperative project scan deadline reached before all eligible paths were visited."
                )
                break
            directory, depth = stack.pop()
            if depth > self.policy.max_depth:
                partial = True
                continue
            try:
                with os.scandir(directory) as iterator:
                    entries = sorted(iterator, key=lambda item: item.name.casefold())
            except OSError:
                errors += 1
                partial = True
                continue
            self._check_cancel(cancel)
            for entry in entries:
                self._check_cancel(cancel)
                if time.monotonic() >= expires_at:
                    partial = True
                    stack.clear()
                    break
                if entry.is_symlink():
                    symlinks_skipped += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if entry.name in self.policy.excluded_dirs:
                        excluded_seen.add(entry.name)
                        continue
                    if depth >= self.policy.max_depth:
                        partial = True
                        continue
                    stack.append((Path(entry.path), depth + 1))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
                if tested >= self.policy.max_files:
                    partial = True
                    stack.clear()
                    break
                tested += 1
                try:
                    relative = Path(entry.path).relative_to(resolved_root).as_posix()
                except ValueError:
                    errors += 1
                    partial = True
                    continue
                if len(relative) > MAX_RELATIVE_PATH or any(
                    ord(ch) < 32 or ord(ch) == 127 for ch in relative
                ):
                    errors += 1
                    partial = True
                    continue
                finding = self._finding_for(relative)
                if finding is not None:
                    findings.append(finding)

        if excluded_seen:
            notes.append(
                "Excluded directory names observed: "
                + ", ".join(sorted(excluded_seen))
                + "."
            )
        if symlinks_skipped:
            notes.append(f"Skipped {symlinks_skipped} symlink path(s).")
        if errors:
            notes.append(f"Could not safely classify {errors} filesystem object(s).")
        if partial:
            notes.append(
                "Coverage is partial because a configured bound or filesystem error was reached."
            )

        payload = {
            "schema": ADAPTER_SCHEMA,
            "adapter": dict(self.identity),
            "status": "partial" if partial else "completed",
            "coverage": {
                "objects_tested": tested,
                "objects_total": None if partial else tested,
                "notes": notes,
            },
            "findings": findings,
            "error": None,
        }
        return normalize_adapter_result(payload, asset_key=asset_key)

    def execution_declaration(self) -> dict:
        declaration = dict(self.execution_template)
        declaration["adapter"] = dict(self.execution_template["adapter"])
        declaration["limits"] = dict(self.execution_template["limits"])
        declaration["limits"]["max_objects"] = self.policy.max_files
        declaration["limits"]["timeout_seconds"] = self.policy.timeout_seconds
        return normalize_execution_declaration(declaration)

    @staticmethod
    def _finding_for(relative_path: str) -> dict | None:
        basename = Path(relative_path).name.lower()
        rule_info = _SECRET_FILENAMES.get(basename)
        if rule_info is None and Path(basename).suffix.lower() in _SECRET_SUFFIXES:
            rule_info = (
                "project/key-material-file",
                "Key-material filename present in project tree",
                "high",
            )
        if rule_info is None:
            return None
        rule, title, severity = rule_info
        return {
            "rule": rule,
            "title": title,
            "severity": severity,
            "confidence": 0.9,
            "external_id": relative_path,
            "evidence": {
                "relative_path": relative_path,
                "filename_only": True,
                "content_read": False,
                "impact_proven": False,
            },
            "remediation": (
                "Confirm whether this file is intentionally tracked. Remove sensitive material from version control, "
                "rotate any exposed credentials or keys, and add an appropriate ignore rule. Filename presence alone "
                "does not prove that a usable secret exists."
            ),
        }
