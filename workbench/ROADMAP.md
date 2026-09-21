# Evidence Workbench development roadmap

This is an ordered engineering backlog, not a claim that all features are implemented or that a fixed sprint can finish every item. Prefer complete, tested slices. Never create cosmetic commits merely to increase contribution counts or promise stars, investment, acceptance or universal capability.

## Development protocol

Read current `main`, the open workbench PR and `PROGRESS.md` before each contribution. Continue the reviewable `feat/evidence-workbench` branch unless a dependent branch is necessary. Preserve upstream attribution, the existing repository license and other contributors' changes. Do not force-push, deploy publicly, contact upstream maintainers or spend money without separate authorization.

Record actual files changed, tests run and explicit validation limits. A configured test is not a passing test. Missing adapters, model checks, E2E coverage or reliability guarantees remain real gaps, not optional polish.

**Current owner direction, 2026-09-21:** local-first and provider-agnostic. The workbench currently implements Ollama as its reference AI integration, including local and explicitly approved cloud-backed models, but product contracts must not depend on Ollama being the permanent gateway. Future reviewed adapters may support third-party APIs or self-hosted inference without changing evidence/tool authority. No silent provider/model fallback, paid development calls, automatic credential provisioning or mandatory cloud dependency. Deterministic no-AI operation remains supported.

## Measurable release-milestone gates

These gates determine whether a review milestone is genuinely complete. They are cumulative. A sprint may stop early only when all gates for the declared milestone pass and remaining work is explicitly outside that milestone.

### Gate A — evidence core
- Final reports are integrity-checked before persistence/export.
- Failed/skipped/inconclusive checks remain visible and cannot become successful coverage.
- Scanner imports cannot self-promote observations to independently verified findings.
- Synthetic proof has a denied control and fresh canary, and is never attributed to an external target.

### Gate B — reliability boundary
- One enforceable end-to-end deadline covers resolution, connect, TLS, response and model operations.
- Cancellation is tested in every phase and cannot publish an unsealed terminal report.
- Crash/restart recovery cannot expose a running job as completed.
- Terminal report publication and durable persistence are atomic or explicitly marked non-durable.

### Gate C — adapter and scope boundary
- Versioned adapter contracts reject malformed/truncated/oversized output and disclose exact coverage.
- Execution adapters use typed configuration, fixed binaries/images and independent scope/effect/request limits; no model-generated shell strings.
- At least one read-only project adapter and one bounded web adapter pass vulnerable/fixed synthetic fixtures before broader claims.

### Gate D — retest and reviewer evidence
- Cross-run comparison distinguishes still-present, new, not-reproduced and not-retested; absence alone never means fixed.
- Reviewer bundles contain checksummed report artifacts and safe proof metadata without reusable credentials or ordinary customer-row samples.
- Remediation evidence links to a comparable recheck and preserves changed-scope/failed-scanner states.

### Gate E — usable review release
- Real-model compatibility is tested separately from protocol doubles; processing location/usage remain honest.
- Browser-to-server E2E and keyboard/accessibility flows pass on documented browsers.
- Fresh-install smoke tests pass on the documented platforms with pinned dependencies/tool licenses and an SBOM.
- Threat model, sample reports, regression lab catalog and release notes clearly separate implemented, experimental and unsupported coverage.

**Current state after Contribution 09: Gates A and D pass their declared bounded criteria in the dedicated workbench test boundary.** Gate A remains evidence-first and Gate D remains conservatively retest-aware. Gate B is **still not complete** because cancellation has not yet been exercised across every connect/TLS/response/model phase and injected readers are not a production hard-deadline guarantee. Gate C now has a closed `hackgpt.execution-declaration/v1` authority contract plus bounded native project-metadata and one-request web-header adapters; vulnerable/corrected synthetic logic fixtures pass, but runner/orchestration integration, production-path web fixture coverage and third-party scanner pinning/licensing remain before Gate C is declared complete. Gate E remains materially incomplete. The project is therefore **not** eligible for an early “only polish remains” stop.

## 1. Complete the reliability boundary

Implemented foundations now include a shared monotonic deadline for native resolver/connect/TLS/response and Ollama runtime calls, cancellable bounded DNS waiting, no terminal unsealed publication from `Assessment`, active SQLite checkpoints, restart recovery to explicit `interrupted`, and atomic durable terminal publication with explicit `not_durable` memory-only fallback.

Next work:
- Exercise cancellation during connect, TLS, slow response and model operations with adversarial owned loopback fixtures; close any phase-specific gaps instead of assuming socket timeout equals cancellation.
- Normalize rejection of special/multicast/tunnel IP ranges across supported Python versions; retain DNS pinning and no redirects.
- Test concurrent API activity and additional SQLite/storage failure modes, including checkpoint gaps followed by restart.
- Decide and document how test-only injected readers participate in deadline enforcement without weakening production boundaries.
- Add structured validation errors and coverage accounting that distinguish failed, unsupported, excluded and executed tests.

Acceptance: Gate B.

## 2. Stable adapter and finding contracts

Implemented foundations: `hackgpt.adapter-result/v1`, deterministic fingerprints, candidate-only import authority, privacy-minimizing offline parsers for Semgrep JSON, Trivy JSON and Nuclei JSONL, malformed/truncated/oversized input tests, explicit coverage caveats, and the closed `hackgpt.execution-declaration/v1` authority contract. The current native project/web adapters declare and enforce no-subprocess/no-write boundaries plus explicit object/request/time budgets. See [ADAPTERS.md](ADAPTERS.md).

Next work:
- Integrate declarations through a small workbench-controlled execution registry/orchestrator instead of direct ad-hoc construction.
- Pin/review each external scanner version, license and packaging boundary before launch support.
- Add production-path owned fixtures for the network adapter and parser/runner pairs for third-party tools.
- Keep severity separate from confidence, proof state, exploitability assumptions and business impact.
- Preserve adapter-specific minimization tests as richer outputs are added.

Acceptance: malformed/truncated fixtures cannot invent verified findings; contract tests pass across supported Python versions; execution authority remains independent of parser/model output.

## 3. Project-code checks first

The first native project execution adapter is now implemented as a metadata-only boundary: it inventories bounded filenames without reading content, following symlinks, using subprocesses/network, or writing to the project. Vulnerable/corrected filename fixtures pass, but this is not a replacement for Semgrep/Trivy code/dependency/secret analysis.

Next work: integrate narrowly configured local code/dependency/secret checks after reviewing tool/rule licenses. Mount source read-only, redact secrets by default and disclose exact files/languages/rules covered. Do not send source, credentials or raw secrets to inference by default. Any external processing needs adapter-specific minimization and disclosure rather than a generic cloud checkbox.

Acceptance: vulnerable and corrected fixtures, pinned versions, offline behavior and explicit errors.

## 4. Controlled web assessment adapters

A first bounded native web execution adapter now exists: one explicit URL, one HEAD request, no redirects, no response body, no filesystem/subprocess/write authority, and candidate-only hardening-header observations. Its vulnerable/corrected logic fixtures pass. This does not yet constitute ZAP/Nuclei execution or broad application coverage.

Next work: add production-path owned network fixtures, then reviewed ZAP/Nuclei-style integrations with target/path allowlists, request budgets and safe profiles. Do not equate a hostname with permission for a CDN/shared IP. Disable uncontrolled callbacks/out-of-band behavior by default. Process runners consume typed configs, never model-generated shell strings.

Acceptance: isolated tests prove no unintended external target and enforce effect/network boundaries outside the model.

## 5. Authenticated test contexts

The execution-neutral `access_matrix.py` foundation now compares explicit role/resource expectations against normalized allowed/denied/error/skipped outcomes, rejects credential/body fields, keeps missing cases incomplete and forces unexpected allows through the candidate-only adapter boundary. It does **not** authenticate or send requests.

Next work: support operator-provided designated test accounts/roles with secure local storage, redaction, expiry and a scoped runner that feeds this matrix. Use customer-designated synthetic/test records and inert canaries for proof. Never use unrelated live customer rows as report samples.

Acceptance: role/isolation vulnerable/fixed fixtures pass, denied controls are independently demonstrated and secrets are absent from logs, prompts and exports.

## 6. Bounded model-independent orchestration

Expand the finite action registry only after each adapter has deterministic validation and independent scope enforcement. Renew approval when target/effect/scope changes. Record public decision/action traces and budgets. Treat model/tool/retrieved text as untrusted data, never authority.

Acceptance: adversarial responses cannot change target, permissions, shell commands, budgets or evidence state. Local/cloud/provider routing never changes tool authority.

## 7. Retesting and change-aware reports

Implemented Gate D foundations now distinguish `still_present`, `new`, `not_reproduced` and `not_retested`; comparison is exposed through the local API/GUI; reviewer bundles carry checksums and safe minimized proof; and each prior finding now gets a recheck binding with previous/current run IDs, previous finding/evidence references, a remediation-guidance digest, exact mapped coverage status and explicit scope comparability. Failed/unmapped checks and changed target/environment remain `not_retested`; `not_reproduced` is never renamed fixed; whether remediation was actually applied remains `unknown` absent separate evidence.

Next work beyond the bounded Gate D criteria: add optional operator-authored remediation activity records with provenance and reviewer signatures/attestation only after a threat model and key-management design. Do not weaken the existing conservative state machine to make dashboards look greener.

Acceptance: Gate D passes at `1c85853a`; failed scanner or changed scope cannot falsely close a finding.

## 8. Interface and accessibility

Retest comparison and evidence-bundle download are now surfaced in the current GUI. Continue with typography/touch targets, keyboard navigation, accessible live statuses, localization-ready strings, filters, per-tool progress, scope/effect preview and evidence drill-down. Add real browser-to-server E2E where environment permits; keep DOM/mock transport tests labeled separately.

Acceptance: keyboard-only flows, responsive documented layouts, readable errors and actual-render screenshots.

## 9. Reproducible packaging

Separate workbench runtime from legacy dependencies. Package reviewed pinned tools in least-privilege containers with checksums, SBOM and licenses. Avoid privileged containers, host Docker socket mounts and unreviewed shell installers. Define measured offline/update bundles.

Acceptance: fresh-install smoke tests; never claim a tool is bundled until its image/binary is actually present and tested.

## 10. Release-quality evidence

Cross-platform validation, signed releases, threat model, regression lab catalog, performance measurements, realistic sanitized reports and contributor guidance. Prepare an upstream proposal only after owner approval.

Acceptance: Gate E.

## 11. Professional engagement workflow and trusted knowledge

Build customer-isolated workspaces, machine-readable rules of engagement, scope/effect previews, designated role matrices, reviewed proof plans, remediation ownership and executive/technical handover. Legal authorization is necessary but not a substitute for precise technical scope/data handling.

Knowledge refresh begins with a licensed, source-linked, versioned retrieval corpus. Preserve publication/ingestion dates, source revisions, licenses, conflict/staleness state, evaluation and rollback. Never ingest customer secrets into shared knowledge. Runtime/model downloads, RAG refresh and actual fine-tuning are distinct. Fine-tuning requires a separately approved dataset/evaluation/release pipeline; no autonomous self-modification.

Acceptance: one customer cannot cross into another workspace, retrieved text cannot authorize an action and a report cannot claim deeper impact than independent evidence demonstrates.