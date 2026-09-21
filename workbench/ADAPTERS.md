# Scanner adapter boundary

This document describes the **implemented parse/review boundary**, not scanner execution. The workbench can now normalize selected scanner result formats offline, but it does not yet launch Semgrep, Trivy, Nuclei, ZAP, Nmap or any other third-party scanner.

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

## Execution adapters are still a separate milestone

Gate C is **not** complete. Before a scanner may be launched by the workbench, its runner must additionally have:

- a pinned/reviewed binary or image and license notice;
- typed configuration rather than model-generated shell strings;
- independently enforced file/network/target/path/effect/request boundaries;
- cancellation and hard deadline behavior;
- vulnerable and corrected owned fixtures;
- exact coverage/error accounting;
- secret-safe logs and exports;
- cross-version regression tests for its parser/runner pair.

The model may later select from approved adapter actions, but model output never becomes execution authority.

## Format references and compatibility notes

Checked 2026-09-21:

- Semgrep has documented JSON output as an integration surface, while later releases also removed some internal/private JSON fields. The parser therefore consumes only a small common subset and tests its own contract rather than depending on private fields: https://semgrep.dev/blog/2022/semgrep-release-v1-announcement/ and https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss/
- Trivy currently documents JSON as a supported report format for its scanners and supports writing JSON reports to a file: https://trivy.dev/docs/dev/guide/configuration/reporting/
- Nuclei's current public documentation evolves independently of this parser. The JSONL parser is fixture-driven and deliberately does not claim complete scan coverage from a finding stream. Its assumptions must be revalidated against the pinned Nuclei version before an execution runner is added: https://docs.projectdiscovery.io/tools/nuclei/input-formats

Exact observed validation for each contribution is recorded in [PROGRESS.md](PROGRESS.md).