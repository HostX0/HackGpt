# Contribution and validation ledger

Historical entries describe the policy at their time. Contribution 04 supersedes the local-inference-only restriction: Ollama remains the implemented reference integration; cloud-backed selection is allowed with explicit assessment-level consent. Contribution 05 records the newer local-first, provider-agnostic product direction: evidence, action and report contracts must not require Ollama to remain the permanent gateway.

## 2026-09-21 — Contribution 01: Evidence-first local workbench

### Implemented

An isolated `workbench/` package with a responsive HTML/CSS/JavaScript interface, native HTTP metadata inspection, an ephemeral authorization-canary lab, two execution modes, optional bounded Ollama tool selection and interpretation, deterministic evidence states, finding fingerprints, per-evidence SHA-256, an ordered hash-linked audit log, finalized report checksums, local SQLite history and JSON/Markdown exports.

Security boundaries include loopback-only service binding, session-token API access, strict Host/Origin validation, no cross-origin allowance, no arbitrary shell execution, typed scope validation, private-address rejection, DNS-pinned native requests, no redirects/body capture on public targets, a three-request native budget, a single active assessment and cancellation checkpoints. The legacy entry points and license were not replaced.

### Validation actually performed

- **72 unit/integration tests passed** on Python 3.13.5 in the development environment. This includes real HTTP requests to owned ephemeral loopback fixtures and the local workbench API; no external target was scanned.
- A deliberately vulnerable synthetic record returned a fresh marker without authorization while the control denied access. The verifier recorded one `verified_in_lab` finding. A corrected fixture did not produce that proof.
- API tests exercised authentication, Host/Origin rejection, content/body limits, protected paths, assessment lifecycle, report persistence, export integrity and history.
- Evidence/report tampering, failed scanners, skipped external verification, absent AI, rejected model actions, duplicate actions and budget enforcement were tested.
- Frontend JavaScript syntax checked with Node 22.16.0.
- Offline Chromium UI contract/layout checks passed at **1440, 768 and 390 pixels**: session unlock, approved form submission, rendering actual synthetic-lab result data, findings/history, no horizontal overflow and no JavaScript exceptions.

### Limits of the validation

- Browser-to-server E2E was **not run successfully**: browser administrator policy blocked localhost navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). Offline UI tests use a mocked fetch transport; native API tests separately use real loopback HTTP. These must not be presented as the same test.
- Live Ollama inference, GPU performance and compatibility with an actual installed model were **not tested**. Model-response contracts were tested with controlled fixtures.
- External websites and third-party scanner binaries were **not tested**. Those adapters are not integrated in this milestone.
- GitHub Actions workflow configuration is supplied; inspect actual hosted run status before claiming hosted CI success.
- Windows/macOS runtime behavior and Python versions other than 3.13 were not locally validated in this first session.

### Problems found and corrected during development

Four initial regression tests failed and were corrected before publishing the test-backed revision: explicit port `0` being treated as a default port, acceptance of an ASCII DEL control character, failure to independently check each finding's evidence digest after an outer reseal, and raw HTML in a target displayed in Markdown export. The interface also disables history switching while its active run is being observed.

### Next highest-priority work

Read ROADMAP.md item 1: hard total deadlines, special-range coverage across Python versions, atomic finalization/persistence and cancellation/restart recovery. Then define a stable adapter contract with offline scanner-output fixtures before increasing execution capability.

### Product claims deliberately not made

This is a working experimental foundation, not a complete production pentest suite. A local-lab proof is not a compromise of a customer's application. No findings does not establish security; inability to demonstrate exploitation does not establish impossibility. SHA-256 records are not signatures. No stars or community adoption are guaranteed.

## 2026-09-21 — Contribution 02: Ollama-only readiness and diagnostics

### Owner direction

At this point in the history, Ollama was the workbench's only intended AI provider. Later contributions supersede that product-level restriction while preserving the implemented Ollama path and its tests.

### Implemented

- Extracted a typed, standard-library-only local runtime with an explicit operation allowlist, strict port/model validation, bounded requests/responses and stable user-safe errors.
- Added model discovery diagnostics and authenticated metadata checking. Exact installed selection is required; `/api/show` gates completion/tool capabilities and rejects remote aliases before each inference under the policy active at that time.
- Added a fixed-provider GUI panel, model capability details, explicit Check model action, safe error guidance and preflight checks for AI-enabled submissions. Stale model-check results are invalidated; duplicate submissions and silent substitution are prevented.
- Kept local metadata checks separate from inference validation and daemon egress attestation. No prompt is sent during Check model, no model is pulled, no API key is requested, and no fallback provider is used.
- Added completed-response/truncation validation, controlled sampling/context/output settings and filtering of model thinking traces. Existing independent finding/evidence verdicts remain authoritative.
- Added [OLLAMA.md](OLLAMA.md) with the provider contract, supported operations, limits, diagnostics, threat boundary, references and validation caveats; updated the roadmap and isolated workflow.

### Validation actually performed before upload

- **38 new Python tests passed locally on Python 3.13.5**, including real loopback HTTP against a synthetic Ollama protocol server. Tests cover installed-model and alias gates, capability compatibility, budgets, strict configuration, malformed/failed/redirected responses and bounded planning contracts.
- **10 new JavaScript behavior tests passed** with Node 22.16.0 using DOM/fetch doubles. Tests cover model discovery, no substitution, stale metadata, tool support, preflight failure, native-only submissions and duplicate-submit prevention.
- Compilation of the locally reconstructed workbench files and JavaScript syntax validation passed.
- The 72 existing Python tests were not rerun in this local working copy because the full repository was not materialized. The workflow was configured to run the complete repository test suite plus the new JavaScript tests on Python 3.11, 3.12 and 3.13; hosted results were checked in later contributions.

### Not validated / still pending

No live Ollama inference, GPU/model performance, cloud-egress attestation, new browser layout/E2E run, external target or third-party scanner execution was performed. Protocol fixtures and DOM doubles are not replacements for those tests. Hard total deadlines, cancellation/restart behavior and atomic durable finalization remained priorities.

## 2026-09-21 — Contribution 03: Assessment-data-free Ollama inference self-test

### Implemented

- Added a bounded compatibility probe that uses only fixed synthetic prompts. It never receives an assessment target, authorization reference, finding, evidence, credential, scanner output or arbitrary user content.
- The first probe requires one exact structured JSON response. Optional tool compatibility uses a second fixed prompt and a single `workbench_self_test` function with empty arguments. The returned tool call is validated but **never executed**; the self-test has no execution callback.
- Added `Ollama.self_test()` and an authenticated loopback `POST /api/models/self-test` endpoint. Its body is closed to `model` and optional policy booleans; extra fields such as a target are rejected before model access.
- Passing output is explicitly labeled `inference_compatible`, records `assessment_data_sent: false`, and does not become assessment evidence or a security verdict. Mismatches fail closed with `self_test_failed`.
- Updated [OLLAMA.md](OLLAMA.md) to distinguish model metadata readiness, synthetic inference compatibility, real assessment inference, and daemon/network-egress attestation.

### Validation performed in this development run

- **9 focused Python unit tests passed locally on Python 3.13** for the self-test module/wrapper. They cover fixed structured output, no assessment fields in the prompt, strict boolean options, inert tool declaration, malformed/missing/wrong tool calls, model-metadata failure before any prompt, and the public `Ollama.self_test()` wrapper.
- `python -m compileall -q workbench` passed in the reconstructed local slice containing the new module/wrapper and test dependencies.
- Four additional loopback API tests were added for authentication, closed request fields, strict options, safe Ollama error propagation and ensuring the probe does not start an assessment. They were not separately executed in that partial local slice; later hosted CI covered the full workbench.

### Deliberate limits

This contribution did **not** claim successful inference against a real installed Ollama model or measure GPU capacity, speed, model quality or future reliability. A self-test pass is not evidence that a daemon is offline. No external targets were contacted and no exploit action was added.

## 2026-09-21 — Contribution 04: Choice of inference location, explicit consent and reviewability

### Implemented

- Preserved Ollama as the implemented gateway while adding strictly typed per-assessment `allow_cloud` support across runtime, scope, authenticated model endpoints and GUI. Local-only remains the default policy; cloud-backed catalog/show aliases become selectable when approved. Local/cloud selection does not change tool authority.
- Added explicit cloud disclosure, no automatic first-model selection, model/location metadata and consent invalidation on model/scope changes, after submission and during stale preflight races. Added an explicit GUI Test response action for fixed synthetic compatibility probes.
- Adapted cloud JSON responses to a prompted contract because current Ollama Cloud documentation does not support server-constrained structured outputs. Both paths retain strict application validation and cannot invent proof states.
- Recorded daemon-reported token counts, attempts and processing metadata in assessment reports, including failed-response coverage and unknown counters. No billing values or hardware performance were fabricated.
- Added a combined loopback integration test covering the real workbench HTTP API, fake cloud-backed Ollama protocol, assessment completion, sealed export and SQLite persistence. No real cloud inference was used.
- Added a revision-bound CI source review artifact with the tracked workbench, workflow, original LICENSE, checksum and real test logs. Excludes root .env, untracked runtime data and reports; it is not a binary release, signed attestation or security certification.
- Updated the current Ollama guide, roadmap and product direction: professional engagement workflow, coverage-aware retest, permission preview, evidence review, customer isolation and provenance-aware retrieval are explicit development targets, not false implemented features.

### Validation actually performed before the main feature commit

- **155 Python unit/integration tests passed locally** on Python 3.13, including **32 new cloud-policy/usage/API tests**; full suite completed in 19.238 seconds in that environment.
- **20 JavaScript behavior tests passed locally**, including **10 new cloud-consent/self-test/stale-response tests**. These use DOM/fetch doubles, not browser E2E.
- `python -m compileall -q workbench` and `node --check workbench/static/app.js` passed.
- Hosted Evidence Workbench CI for feature head `5ad825c10ff3ddcd4377e5e5a2c8a0bda1dbd667` succeeded on Python 3.11, 3.12 and 3.13 in run `35552510665`. The independent legacy Enterprise CI/CD was separate and failed; workbench success was never presented as repository-wide success.

### Limits and next work

No live local/cloud model inference, account sign-in, paid API, GPU test, external target, real third-party scanner or new browser E2E/layout check was performed. Prompted JSON is not constrained decoding; model metadata is not egress attestation; reported counters are not a bill. Checkpoint cancellation and per-operation timeouts were still not hard end-to-end deadlines.

## 2026-09-21 — Contribution 05: Adapter trust boundary, coverage-aware retest and privacy-preserving proof

### Implemented

This contribution spans feature commits `fa95c429a1d9dd6c47eafde7e0d2bb8381b869bd`, `d5ac514b7b829750f4913c0fc34ce8a9a1068d53` and `e2268b88ddaf027db819ab04437d2bd91fb7039e`.

- Added `contracts.py` with versioned `hackgpt.adapter-result/v1` validation, bounded evidence/coverage, deterministic fingerprints and a verification firewall: imported scanner findings are always `candidate`; an adapter cannot label its own output independently verified.
- Added `retest.py` with conservative cross-run states `still_present`, `new`, `not_reproduced` and `not_retested`. Missing findings are never labeled fixed solely by absence; comparable target/environment and successful relevant coverage are required even for `not_reproduced`.
- Added `bundle.py` and authenticated `export.bundle.zip`: finalized intact reports can be packaged with JSON/Markdown and an unsigned manifest containing SHA-256/size metadata. This improves reviewer portability without pretending checksums are signatures.
- Added authenticated `/api/runs/<previous>/compare/<current>` to expose retest comparison through the real loopback API. Unknown or non-intact runs fail explicitly.
- Added `evidence_safety.py` for data-layer proof metadata. Ordinary record values are omitted; row count, column/type metadata and a content digest are retained, while only explicit `HACKGPT-SYNTHETIC-*` canaries may be shown as sample proof.
- Upgraded the owned synthetic authorization fixture so successful verification demonstrates unauthenticated read of designated synthetic records, records a denied control and fresh canary, and explicitly states `customer_data_sampled: false`. The corrected fixture does not export a data summary.
- Rewrote `ROADMAP.md` with measurable cumulative Gates A–E covering evidence, reliability, adapter/scope boundaries, retest/reviewer evidence and usable review release. Current gates explicitly remain incomplete; this sprint must not stop early merely because optional polish remains.
- Reconciled `PRODUCT_DIRECTION.md` to local-first, provider-agnostic architecture: Ollama is the only AI adapter implemented today, not a permanent architectural requirement. Future reviewed provider/self-hosted adapters must reuse the same independent evidence/action authority.

### Validation actually observed

- **21 focused new pure-module unit tests passed locally** before the first commit. They cover adapter candidate-state enforcement, malformed coverage/evidence, stable fingerprints, retest states, unsigned bundle manifests and record-value minimization.
- The review API integration changes were syntax-compiled locally; the container used for this automation could not clone GitHub because external DNS was unavailable, so a second local full-suite run was not fabricated.
- Hosted **Evidence Workbench** run `35554625980` completed successfully for current head `e2268b88ddaf027db819ab04437d2bd91fb7039e` on Python **3.11, 3.12 and 3.13**. Each job passed isolated compilation, full Python unit/real-loopback integration discovery, JavaScript syntax and frontend DOM/fetch contract tests. The Python 3.13 job also produced the revision-bound review artifact.
- Real-loopback API tests added in this contribution exercise evidence-bundle export, conservative comparison and missing-run handling. Synthetic data-proof tests verify the evidence contains the canary/schema/hash but not ordinary fixture account values.
- No external assessment target, real database, live customer row, credential, third-party scanner, paid model or public service was touched.

### Remaining blockers to the measurable release gates

- Gate B remains incomplete: no true end-to-end deadline spanning DNS/network/model operations, no interruption-safe atomic terminal persistence and no complete restart recovery.
- Gate C remains incomplete: the adapter contract exists, but Semgrep/Trivy-style read-only execution and bounded ZAP/Nuclei-style web adapters are not implemented/tested.
- Gate D has substantial foundations, but retest/bundle controls are not yet surfaced in the GUI and evidence replay is not a signed attestation.
- Gate E remains incomplete: no live model benchmark, browser-to-server E2E/accessibility pass, cross-platform fresh-install smoke test, signed release or full packaging/SBOM evidence.
- The legacy Enterprise workflows remain separate from Evidence Workbench CI and must not be implied successful by this run.

### Safety/product interpretation

The stronger synthetic data proof is intentionally **not** a database dump. It demonstrates the product pattern the owner requested—concrete evidence that a data boundary can be crossed—using designated synthetic records and a denied control, while avoiding reusable credentials or customer data in the report. Real external exploitation, persistence, credential theft, customer-row sampling and lateral movement remain outside this workbench contribution.
