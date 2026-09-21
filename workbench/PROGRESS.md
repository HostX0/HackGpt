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
