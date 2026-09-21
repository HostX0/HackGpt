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

**Current state:** Gate A is partially implemented; Gate D now has standalone conservative retest/bundle foundations but still needs UI/API integration and full-suite CI evidence. Gates B, C and E remain incomplete. Therefore the project is not eligible for an early “only polish remains” stop.

## 1. Complete the reliability boundary

- Enforce a genuine end-to-end deadline, including resolver and slow-read behavior; add adversarial loopback tests.
- Normalize rejection of special/multicast/tunnel IP ranges across supported Python versions; retain DNS pinning and no redirects.
- Make terminal status publication atomic with sealing/persistence; add restart/interruption recovery for active jobs.
- Test cancellation during every phase, storage failures, model timeouts and concurrent API activity.
- Add structured validation errors and coverage accounting that distinguish failed, unsupported, excluded and executed tests.

Acceptance: Gate B.

## 2. Stable adapter and finding contracts

- Version request/result schemas, adapter/tool/version identifiers and deterministic fingerprints.
- Typed adapter protocol declares network/filesystem permissions, effect level, scope capability and coverage units.
- Parse scanner fixtures offline before implementing execution.
- Normalize severity separately from confidence, proof state, exploitability assumptions and business impact.
- Imported adapters can create candidates/observations only; independent verification remains a separate authority.

Acceptance: malformed/truncated fixtures cannot invent verified findings; contract tests pass across supported Python versions.

## 3. Project-code checks first

Integrate narrowly configured local code/dependency/secret checks after reviewing tool/rule licenses. Mount source read-only, redact secrets by default and disclose exact files/languages/rules covered. Do not send source, credentials or raw secrets to inference by default. Any external processing needs adapter-specific minimization and disclosure rather than a generic cloud checkbox.

Acceptance: vulnerable and corrected fixtures, pinned versions, offline behavior and explicit errors.

## 4. Controlled web assessment adapters

Add reviewed ZAP/Nuclei-style integrations with target/path allowlists, request budgets and safe profiles. Do not equate a hostname with permission for a CDN/shared IP. Disable uncontrolled callbacks/out-of-band behavior by default. Process runners consume typed configs, never model-generated shell strings.

Acceptance: isolated tests prove no unintended external target and enforce effect/network boundaries outside the model.

## 5. Authenticated test contexts

Support operator-provided designated test accounts/roles with secure local storage, redaction, expiry and an access-control matrix. Use customer-designated synthetic/test records and inert canaries for proof. Never use unrelated live customer rows as report samples.

Acceptance: role/isolation vulnerable/fixed fixtures pass and secrets are absent from logs, prompts and exports.

## 6. Bounded model-independent orchestration

Expand the finite action registry only after each adapter has deterministic validation and independent scope enforcement. Renew approval when target/effect/scope changes. Record public decision/action traces and budgets. Treat model/tool/retrieved text as untrusted data, never authority.

Acceptance: adversarial responses cannot change target, permissions, shell commands, budgets or evidence state. Local/cloud/provider routing never changes tool authority.

## 7. Retesting and change-aware reports

Use stable fingerprints plus comparable coverage to distinguish still-present, new, not-reproduced, not-retested and regression. Add evidence-linked remediation/recheck. Do not produce an unsupported overall safety score.

Acceptance: Gate D; failed scanner or changed scope cannot falsely close a finding.

## 8. Interface and accessibility

Refine typography/touch targets, keyboard navigation, accessible live statuses, localization-ready strings, filters, per-tool progress, scope/effect preview, retest diff and evidence drill-down. Add real browser-to-server E2E where environment permits; keep DOM/mock transport tests labeled separately.

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
