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

**Current state after Contribution 14: Gates A, B and D pass their declared bounded criteria in the dedicated workbench test boundary.** Gate B retains shared deadline/cancellation coverage across DNS, pending TCP connect, TLS, slow HTTP response and model transport plus durable terminal publication/recovery. Gate C now additionally has a durable `hackgpt.adapter-lifecycle/v1` state machine, exact request-digest approval binding, authenticated plan/approve/execute/cancel/read API routes, serialized adapter-vs-assessment execution, a GUI authority preview, restart recovery for interrupted adapter executions and nested sensitive-field rejection in execution receipts. Hosted Evidence Workbench run `35578990398` validated the implementation head `45b9c9d4651d272d021e0c4c3958f3697bf7e446` on Python 3.11/3.12/3.13; Python 3.13 ran 312 Python tests and 27 JavaScript DOM/fetch contract tests successfully. Gate C still requires reviewed pinned/licensed third-party runner packaging/integration before it is declared complete. Gate E still lacks live real-model compatibility, real browser-to-server E2E/accessibility, cross-platform fresh-install validation and a signed/release-grade package. The project is therefore **not** eligible for an early “only polish remains” stop.

## 1. Complete the reliability boundary

Implemented foundations include a shared monotonic deadline for native resolver/connect/TLS/response and Ollama runtime calls, cancellable bounded DNS waiting, no terminal unsealed publication from `Assessment`, active SQLite checkpoints, restart recovery to explicit `interrupted`, and atomic durable terminal publication with explicit `not_durable` memory-only fallback.

The production passive-web path uses a cancellation-aware nonblocking TCP connector. Owned adversarial fixtures exercise pending-connect cancellation/deadline, TLS-handshake cancellation/deadline, slow-response cancellation/deadline and slow model cancellation/deadline; bounded DNS cancellation/deadline and durable publication/recovery are also covered. The first timing-sensitive CI assertion was corrected because a successful cancellation may legitimately occur before the owned HTTP fixture parses a HEAD request; the corrected test asserts bounded cancellation and no unintended GET/body path instead.

Next work beyond the bounded Gate B criteria:
- Normalize rejection of special/multicast/tunnel IP ranges across supported Python versions; retain DNS pinning and no redirects.
- Test concurrent API activity and additional SQLite/storage failure modes, including checkpoint gaps followed by restart.
- Decide and document how test-only injected readers participate in deadline enforcement without weakening production boundaries.
- Add structured validation errors and richer coverage accounting that distinguish failed, unsupported, excluded and executed tests.
- Keep project-filesystem cancellation explicitly cooperative at metadata boundaries; do not describe blocking filesystem syscalls as instantly interruptible.

Acceptance: **Gate B passes** at feature head `4e71682a0a44c6cbd650c8aa1cf921d50e0766fa` in Evidence Workbench run `35568876285` on Python 3.11, 3.12 and 3.13. Later feature heads preserve that boundary in the same dedicated test matrix.

## 2. Stable adapter and finding contracts

Implemented foundations: `hackgpt.adapter-result/v1`, deterministic fingerprints, candidate-only import authority, privacy-minimizing offline parsers for Semgrep JSON, Trivy JSON and Nuclei JSONL, malformed/truncated/oversized input tests, explicit coverage caveats, the closed `hackgpt.execution-declaration/v1` authority contract, a finite `ExecutionRegistry` with operator-owned filesystem/network/effect ceilings, `hackgpt.execution-receipt/v1`, and the durable `hackgpt.adapter-lifecycle/v1` plan/approval/execution state machine.

The registry validates a typed adapter request without I/O, exposes a minimized review preview and binds a normalized candidate-only result to declared authority plus observed object/request/elapsed-time accounting. Lifecycle storage persists the minimized declaration/summary and an exact request digest rather than the raw request, makes approved plan fields immutable, revalidates the resubmitted request before I/O, records stable failure states without raw exception text and recovers stale `executing` records as `interrupted`. Receipt validation rejects nested sensitive/execution fields, identity mismatches and usage above declared object/request budgets. See [ADAPTERS.md](ADAPTERS.md).

Next work:
- Pin/review each external scanner version, license, checksum and packaging boundary before launch support.
- Add parser/runner integration fixtures for each reviewed third-party tool; the existing native web loopback fixture does not substitute for tool-specific runner tests.
- Keep severity separate from confidence, proof state, exploitability assumptions and business impact.
- Preserve adapter-specific minimization and lifecycle-tamper tests as richer outputs are added.
- Do not claim a third-party process is read-only without an independently enforced filesystem/network sandbox boundary.

Acceptance: malformed/truncated fixtures cannot invent verified findings; contract/lifecycle tests pass across supported Python versions; execution authority remains independent of parser/model output.

## 3. Project-code checks first

The first native project execution adapter is implemented as a metadata-only boundary: it inventories bounded filenames without reading content, following symlinks, using subprocesses/network, or writing to the project. Vulnerable/corrected filename fixtures pass. Cancellation is propagated by the finite registry into cooperative checkpoints before and during the metadata walk. Its plan/approval/execution receipt can now be reviewed and persisted through the same authenticated lifecycle API/GUI without storing the full local root path.

Next work: integrate narrowly configured local code/dependency/secret checks only after reviewing tool/rule licenses and establishing a real sandbox/mount boundary. Mount source read-only, redact secrets by default and disclose exact files/languages/rules covered. Do not send source, credentials or raw secrets to inference by default. Any external processing needs adapter-specific minimization and disclosure rather than a generic cloud checkbox.

Acceptance: vulnerable and corrected fixtures, pinned versions, offline behavior and explicit errors.

## 4. Controlled web assessment adapters

A first bounded native web execution adapter exists: one explicit URL, one HEAD request, no redirects, no response body, no filesystem/subprocess/write authority, and candidate-only hardening-header observations. Its vulnerable/corrected logic fixtures pass and its production HTTP-reader path has an owned loopback fixture. The same exact URL/limits now pass through durable plan approval and execution receipt controls. This does not constitute ZAP/Nuclei execution or broad application coverage.

Next work: add reviewed ZAP/Nuclei-style integrations only with target/path allowlists, request budgets, safe profiles, pinned versions/licenses and isolated fixtures. Do not equate a hostname with permission for a CDN/shared IP. Disable uncontrolled callbacks/out-of-band behavior by default. Process runners consume typed configs, never model-generated shell strings.

Acceptance: isolated tests prove no unintended external target and enforce effect/network boundaries outside the model.

## 5. Authenticated test contexts

The execution-neutral `access_matrix.py` foundation compares explicit role/resource expectations against normalized allowed/denied/error/skipped outcomes, rejects credential/body fields, keeps missing cases incomplete and forces unexpected allows through the candidate-only adapter boundary. It does **not** authenticate or send requests.

Next work: support operator-provided designated test accounts/roles with secure local storage, redaction, expiry and a scoped runner that feeds this matrix. Use customer-designated synthetic/test records and inert canaries for proof. Never use unrelated live customer rows as report samples.

Acceptance: role/isolation vulnerable/fixed fixtures pass, denied controls are independently demonstrated and secrets are absent from logs, prompts and exports.

## 6. Bounded model-independent orchestration

The current `ExecutionRegistry` is finite and policy-gated: reviewed adapter IDs map to code-owned constructors, unknown command/dynamic fields fail closed, and operator filesystem/network/effect ceilings are checked before adapter I/O. `plan()` is I/O-free and `execute_with_receipt()` produces versioned candidate-only receipts.

`AdapterLifecycle` now persists `planned -> approved -> executing -> completed|failed|cancelled|interrupted`, binds approval to the exact plan/request digest and revalidates the same request before execution. `workspace_server.py` exposes authenticated plan/approve/execute/cancel/read routes and serializes the adapter lane against ordinary assessment starts. The GUI freezes inputs after planning and keeps execution disabled until the exact digest is approved. No model output participates in these approval decisions.

Next work: expand the registry only after each third-party adapter has deterministic validation, pinned packaging/licensing and independent sandbox/scope enforcement. Add per-tool progress events and integrate resulting candidate observations into the main assessment report only with explicit provenance and without collapsing the independent lifecycle audit trail. Renew approval whenever target/effect/scope changes.

Acceptance: adversarial responses cannot change target, permissions, shell commands, budgets or evidence state. Local/cloud/provider routing never changes tool authority.

## 7. Retesting and change-aware reports

Implemented Gate D foundations distinguish `still_present`, `new`, `not_reproduced` and `not_retested`; comparison is exposed through the local API/GUI; reviewer bundles carry checksums and safe minimized proof; and each prior finding gets a recheck binding with previous/current run IDs, previous finding/evidence references, a remediation-guidance digest, exact mapped coverage status and explicit scope comparability. Failed/unmapped checks and changed target/environment remain `not_retested`; `not_reproduced` is never renamed fixed; whether remediation was actually applied remains `unknown` absent separate evidence.

Next work beyond the bounded Gate D criteria: add optional operator-authored remediation activity records with provenance and reviewer signatures/attestation only after a threat model and key-management design. Do not weaken the existing conservative state machine to make dashboards look greener.

Acceptance: Gate D passes at `1c85853a`; failed scanner or changed scope cannot falsely close a finding.

## 8. Interface and accessibility

Retest comparison, evidence-bundle download and reviewed adapter plan/approval/receipt controls are now surfaced in the current GUI. The adapter UI performs no automatic discovery or execution, freezes exact typed inputs after planning, and labels receipts as candidate review metadata rather than proof. DOM/fetch contract tests cover plan, approval, execution and web/project request shapes.

Next work: continue typography/touch targets, keyboard navigation, focus management, accessible live statuses, localization-ready strings, filters, per-tool progress and evidence drill-down. Add real browser-to-server E2E where environment permits; keep DOM/mock transport tests labeled separately.

Acceptance: keyboard-only flows, responsive documented layouts, readable errors and actual-render screenshots.

## 9. Reproducible packaging

Separate workbench runtime from legacy dependencies. Package reviewed pinned tools in least-privilege containers with checksums, SBOM and licenses. Avoid privileged containers, host Docker socket mounts and unreviewed shell installers. Define measured offline/update bundles.

Acceptance: fresh-install smoke tests; never claim a tool is bundled until its image/binary is actually present and tested.

## 10. Release-quality evidence

Implemented review-evidence foundations include [THREAT_MODEL.md](THREAT_MODEL.md), [REGRESSION_LABS.md](REGRESSION_LABS.md), [RELEASE_NOTES.md](RELEASE_NOTES.md) and `release_evidence.py`. The Python 3.13 CI job generates a revision-bound machine-readable review manifest, a minimal CycloneDX SBOM scoped to the isolated shipped workbench component, a JSON/Markdown sample report produced by the owned synthetic authorization fixture, checksums and the source/test-log review bundle. The manifest deliberately records that no third-party scanners are bundled and that browser E2E, cross-platform fresh-install validation, signing and public-service support are false rather than inferred.

Next work: validate a real compatible model separately from protocol doubles; add real browser-to-loopback E2E/keyboard-accessibility evidence; run documented fresh-install smoke tests on supported operating systems; define release-grade packaging and signing/key management; add measured performance only after reproducible benchmarks. Future executable third-party runners must add pinned versions/images, licenses, checksums and SBOM components before the release evidence may claim they ship.

Acceptance: Gate E only after every Gate E criterion passes; current review evidence materially advances the gate but does not close it.

## 11. Professional engagement workflow and trusted knowledge

Build customer-isolated workspaces, machine-readable rules of engagement, scope/effect previews, designated role matrices, reviewed proof plans, remediation ownership and executive/technical handover. Legal authorization is necessary but not a substitute for precise technical scope/data handling.

Knowledge refresh begins with a licensed, source-linked, versioned retrieval corpus. Preserve publication/ingestion dates, source revisions, licenses, conflict/staleness state, evaluation and rollback. Never ingest customer secrets into shared knowledge. Runtime/model downloads, RAG refresh and actual fine-tuning are distinct. Fine-tuning requires a separately approved dataset/evaluation/release pipeline; no autonomous self-modification.

Acceptance: one customer cannot cross into another workspace, retrieved text cannot authorize an action and a report cannot claim deeper impact than independent evidence demonstrates.