# Contribution and validation ledger

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

Keep developing, testing and uploading without requiring the owner to install or run anything now. Ollama is the workbench's **only AI provider**. Do not add hosted providers or fallback services. Deterministic checks with AI explicitly disabled remain supported. Existing legacy code and attribution are preserved, not silently rewritten.

### Implemented

- Extracted a typed, standard-library-only local runtime with an explicit operation allowlist, strict port/model validation, bounded requests/responses and stable user-safe errors.
- Added model discovery diagnostics and authenticated metadata checking. Exact installed selection is required; `/api/show` gates completion/tool capabilities and rejects remote aliases before each inference.
- Added a fixed-provider GUI panel, model capability details, explicit Check model action, safe error guidance and preflight checks for AI-enabled submissions. Stale model-check results are invalidated; duplicate submissions and silent substitution are prevented.
- Kept local metadata checks separate from inference validation and daemon egress attestation. No prompt is sent during Check model, no model is pulled, no API key is requested, and no fallback provider is used.
- Added completed-response/truncation validation, controlled sampling/context/output settings and filtering of model thinking traces. Existing independent finding/evidence verdicts remain authoritative.
- Added [OLLAMA.md](OLLAMA.md) with the provider contract, supported operations, limits, diagnostics, threat boundary, references and validation caveats; updated the roadmap and isolated workflow.

### Validation actually performed before upload

- **38 new Python tests passed locally on Python 3.13.5**, including real loopback HTTP against a synthetic Ollama protocol server. Tests cover installed-model and alias gates, capability compatibility, budgets, strict configuration, malformed/failed/redirected responses and bounded planning contracts.
- **10 new JavaScript behavior tests passed** with Node 22.16.0 using DOM/fetch doubles. Tests cover model discovery, no substitution, stale metadata, tool support, preflight failure, native-only submissions and duplicate-submit prevention.
- Compilation of the locally reconstructed workbench files and JavaScript syntax validation passed.
- The 72 existing Python tests were not rerun in this local working copy because the full repository was not materialized. The workflow is configured to run the complete repository test suite plus the new JavaScript tests on Python 3.11, 3.12 and 3.13. Check the actual commit's hosted CI results separately; configuration is not a passing result.

### Not validated / still pending

No live Ollama inference, GPU/model performance, cloud-egress attestation, new browser layout/E2E run, external target or third-party scanner execution was performed. Protocol fixtures and DOM doubles are not replacements for those tests. The new model metadata endpoint has safe validation and uses the already-authenticated local handler, but broader real-browser integration remains pending. Hard total deadlines, cancellation/restart behavior and atomic durable finalization remain the next reliability priorities. Upstream submission and maintainer acceptance have not occurred.

## 2026-09-21 — Contribution 03: Assessment-data-free Ollama inference self-test

### Implemented

- Added a bounded compatibility probe that uses only fixed synthetic prompts. It never receives an assessment target, authorization reference, finding, evidence, credential, scanner output or arbitrary user content.
- The first probe requires one exact structured JSON response. Optional tool compatibility uses a second fixed prompt and a single `workbench_self_test` function with empty arguments. The returned tool call is validated but **never executed**; the self-test has no execution callback.
- Added `Ollama.self_test()` and an authenticated loopback `POST /api/models/self-test` endpoint. Its body is closed to `model` and optional boolean `require_tools`; extra fields such as a target are rejected before model access.
- Passing output is explicitly labeled `inference_compatible`, records `assessment_data_sent: false`, and does not become assessment evidence or a security verdict. Mismatches fail closed with `self_test_failed`.
- Updated [OLLAMA.md](OLLAMA.md) to distinguish model metadata readiness, synthetic inference compatibility, real assessment inference, and daemon/network-egress attestation.

### Validation performed in this development run

- **9 focused Python unit tests passed locally on Python 3.13** for the new self-test module/wrapper. They cover fixed structured output, no assessment fields in the prompt, strict boolean options, inert tool declaration, malformed/missing/wrong tool calls, model-metadata failure before any prompt, and the public `Ollama.self_test()` wrapper.
- `python -m compileall -q workbench` passed in the reconstructed local slice containing the new module/wrapper and test dependencies.
- Four additional loopback API tests were added to the repository for authentication, closed request fields, strict `require_tools`, safe Ollama error propagation and ensuring the probe does not start an assessment. They were **not separately executed in the partial local slice** because the full repository was not materialized there; hosted Evidence Workbench CI is expected to discover them along with the complete existing suite. An actual hosted result must be checked before claiming they passed.

### Deliberate limits

This contribution still does **not** claim successful inference against a real installed Ollama model or measure GPU capacity, speed, model quality or future reliability. A self-test pass is not evidence that the daemon is offline: operators must configure the running Ollama service with `OLLAMA_NO_CLOUD=1`, restart it, and use separate egress controls when a stronger offline guarantee is required. The new backend endpoint is intentionally not wired to an automatic GUI inference action yet; model metadata preflight remains non-inference. No external targets were contacted and no exploit action was added.
