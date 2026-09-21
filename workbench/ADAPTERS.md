# Scanner and execution adapter boundary

The workbench now has three separate implemented boundaries:

- an offline parse/review boundary for selected third-party scanner result formats;
- a typed native execution boundary with a metadata-only project adapter and a one-request web-header adapter; and
- a versioned planning/receipt boundary that records sanitized scope previews, declared authority and bounded observed usage without granting verification authority.

The workbench still does **not** launch Semgrep, Trivy, Nuclei, ZAP, Nmap or another third-party scanner. The native adapters below are deliberately narrow and cannot turn their own observations into independently verified findings.

## Why parsing comes before execution

Third-party output is untrusted input. The workbench therefore separates four authorities:

1. A scanner may produce a raw observation.
2. A format parser may extract a bounded, privacy-minimized subset.
3. `hackgpt.adapter-result/v1` normalizes that subset and forces every imported finding to `candidate`.
4. Only a separate workbench-controlled verification step may later prove a finding in an approved test context.

A parser cannot widen target scope, execute a command, reuse a credential, mark itself independently verified, or turn missing coverage into a pass.

## Implemented offline parsers

| Parser | Input | Retained evidence | Deliberately omitted | Coverage interpretation |
|---|---|---|---|---|
| `semgrep-json` | Semgrep JSON result object | Rule, file path, start/end line, message, severity, stable external identifier when supplied | Source snippets, metavariable contents, arbitrary internal fields | Uses the explicit scanned-path list when present. Scanner errors make the result `partial`. |
| `trivy-json` | Trivy JSON report | Target, package/version/fix metadata, misconfiguration location metadata, secret rule and line range | Secret matches, embedded source/configuration code, advisory prose not required for evidence | Counts top-level result objects. Findings remain candidates. |
| `nuclei-jsonl` | One JSON finding per line | Template id/name, severity, matcher, protocol and URL path | Raw request/response, curl command, extracted values, URL query/host | Finding streams do not establish complete target/template coverage, so non-empty imports are deliberately `partial`; an empty stream keeps coverage unknown. |

All parser input is bounded to 2 MiB, must be UTF-8 text without NUL bytes, and is capped at the adapter contract's 500 normalized findings. Malformed/truncated content fails closed.

## Privacy properties

The parse layer intentionally does **not** act as an archive of raw scanner output. It keeps enough metadata for review and stable fingerprints while reducing the chance that a finding export becomes a second copy of customer secrets, response bodies or exploit material.

This is not a universal redaction guarantee. Future adapters may expose new sensitive fields and must receive adapter-specific review and regression tests before execution is enabled. Raw source files and raw scanner reports remain outside this normalized evidence contract unless a separately reviewed workflow explicitly handles them.

## Access-control matrix foundation

`access_matrix.py` adds an execution-neutral role/resource policy evaluator. It accepts only role/resource labels, an expected allow/deny state, a normalized observed state and whether an independent denied control was confirmed. It accepts no password, token, cookie, response body or customer record fields.

Unexpected allows become **candidate** access-control observations. A confirmed denied control raises confidence, but it still does not become independently verified until a separate workbench proof step validates impact. Missing, errored and skipped matrix cases remain incomplete coverage. Unexpected denials are reported as policy mismatches rather than being mislabeled as exploit findings.

This is groundwork for designated test-account matrices in owned synthetic fixtures. It is not an authenticated external scanner and does not store credentials.

## Implemented native execution declarations and adapters

`execution_contracts.py` adds `hackgpt.execution-declaration/v1`. It is a closed declaration of required authority, not a permission grant. A declaration records the adapter/version, launcher class, effect level, filesystem/network authority, whether subprocesses/writes/symlinks are involved, hard object/request/time limits and a coverage unit. Unknown fields such as an arbitrary `command` are rejected. Native Python adapters cannot declare subprocess execution; read-only adapters cannot declare writes; network-none adapters must have a zero request budget.

Two native adapters currently implement this declaration:

| Adapter | Authority | What it does | What it deliberately does not do |
|---|---|---|---|
| `native-project-metadata/1` | read-only filesystem metadata, no network, no subprocess, no writes, no symlink following | Traverses bounded project filenames and reports candidate observations for filenames commonly associated with environment/credential/key material | Reads no file content or secret value, executes no scanner, follows no symlink |
| `native-web-headers/1` | passive scoped-target network, exactly one request, no filesystem/subprocess/write authority | Issues one scoped HEAD request through the existing DNS-pinned/no-redirect/body-free reader and reports candidate HTML hardening-header observations | Sends no payload/body, follows no redirect, reads no response body, stores no cookie/header outside the small allowlist |

Both adapters feed `hackgpt.adapter-result/v1`, so their observations remain `candidate`. Filename presence or a missing header is not exploit proof. Tests use vulnerable/corrected synthetic fixtures and also exercise fail-closed input/authority boundaries.

## Planning and execution receipts

`ExecutionRegistry.plan()` validates one reviewed typed request against the operator-owned authority ceiling **without executing adapter I/O**. The preview is intentionally minimized:

- project scans retain an asset key and a short project label but not the full local root path;
- web scans retain the exact approved URL plus the fixed `HEAD` / no-redirect / no-body behavior;
- arbitrary commands, argv, environment fields and dynamic adapter identifiers are not part of the planning surface.

`execution_receipts.py` adds `hackgpt.execution-receipt/v1`. `ExecutionRegistry.execute_with_receipt()` combines the reviewed declaration, minimized request summary, normalized candidate-only result and bounded observed usage. The current native adapters account:

- eligible filesystem objects tested;
- scoped network requests (zero for the project adapter, exactly one for a completed/partial native web-header run); and
- elapsed adapter execution time in milliseconds.

Receipt validation rejects object/request usage above the declaration's hard limits, adapter identity mismatches, self-verified findings and sensitive/execution fields such as passwords, tokens, cookies, authorization values, commands or argv in the request summary.

A receipt is review metadata, not a security verdict. It does not prove that every possible object was covered, it does not attest OS-level egress, and it does not upgrade candidate findings. The next lifecycle step is to persist these receipts inside durable assessment runs and expose the same preview/accounting through authenticated API/GUI controls.

## Remaining Gate C work

Gate C is **materially advanced but is not declared complete by this contribution**. The native adapters establish the typed execution shape and bounded project/web examples; planning and receipts add a reviewable budget/accounting contract. The product still needs durable assessment-lifecycle/API/GUI execution using these receipts before broad execution claims. Third-party scanners additionally require:

- a pinned/reviewed binary or image and license notice;
- typed fixed arguments rather than model-generated shell strings;
- independently enforced file/network/target/path/effect/request boundaries;
- cancellation and hard deadline behavior;
- vulnerable and corrected owned integration fixtures;
- exact coverage/error accounting;
- secret-safe logs and exports;
- cross-version regression tests for each parser/runner pair.

The model may later select from approved adapter actions, but model output never becomes execution authority.

## Format references and compatibility notes

Checked 2026-09-21:

- Semgrep has documented JSON output as an integration surface, while later releases also removed some internal/private JSON fields. The parser therefore consumes only a small common subset and tests its own contract rather than depending on private fields: https://semgrep.dev/blog/2022/semgrep-release-v1-announcement/ and https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss/
- Trivy currently documents JSON as a supported report format for its scanners and supports writing JSON reports to a file: https://trivy.dev/docs/dev/guide/configuration/reporting/
- Nuclei's current public documentation evolves independently of this parser. The JSONL parser is fixture-driven and deliberately does not claim complete scan coverage from a finding stream. Its assumptions must be revalidated against the pinned Nuclei version before an execution runner is added: https://docs.projectdiscovery.io/tools/nuclei/input-formats

Exact observed validation for each contribution is recorded in [PROGRESS.md](PROGRESS.md).