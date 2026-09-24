# Evidence Workbench current development ledger

## Active milestone: reviewer evidence and product-readiness hardening

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical records remain preserved in Git history and in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). This file records the current shipping state and the evidence that applies to it; it does not rewrite those historical ledgers.

The fork itself is the product target. Upstream acceptance is not a release gate. The product remains bounded: preserve the retained application and Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require finite independently approved tool execution, maintain local-first/provider-neutral model contracts, and report limitations rather than universal coverage. No owner-side installation or testing is required.

## Merged foundations

PR #2 was merged to fork `main` at `2cf544d46f9d6c1b4383230ff7d0aa004a8cb56d` on 2026-09-24. It preserves the original Evidence Workbench and subsequent contributions while adding the reviewed startup/install, model, execution-lifecycle, report, package, CI, and reliability work recorded in the historical ledgers.

PR #4 (`fix/retest-comparability`) was reviewed on exact source `a7e061f9a6bc2905d20e361d1a724ac4399fe524` and then merged with expected-head protection to fork `main` at `2032bce9228cdb404e2b2b6b3c8d8053ea515eec`. Its exact-head Evidence Workbench, Workbench Startup, Release Package, Basic CI, and Enterprise CI workflows all completed successfully before merge. The merged retest contract remains conservative: duplicate/missing finding identity fails closed; missing target/environment identity cannot become comparable absence; a run cannot be compared with itself; adapter version/method/coverage drift remains `not_retested`; and `not_reproduced` is never presented as `fixed`.

## Trusted portable-release verification repaired on main

The post-PR4 main release exposed a real shipping defect: trusted Release Package run `35964232068` failed while verifying signed release evidence. PR #3 (`fix/release-attestation-verification`) repaired the exact workflow rather than weakening attestation or skipping verification. The branch was reconciled non-force with current main, reviewed on source `69a843d3ef998fc980d91d08bbfe116c0815a077`, and merged with expected-head protection to fork `main` at **`5b6482bfa08d075078fd0dba0e28ba361ad66628`**.

The retained release behavior is now explicit and fail-closed:

1. normalize and validate the exact revision-bound package basename;
2. require the downloaded archive and `SHA256SUMS`, and verify the archive bytes before requesting signatures;
3. generate separate build-provenance and CycloneDX SBOM attestations only in trusted non-PR context;
4. require bundle/attestation identifiers and URLs rather than accepting missing outputs;
5. verify the exact local provenance bundle with the SLSA predicate, repository, source digest, and exact signer workflow;
6. verify the exact local SBOM bundle with the CycloneDX predicate and the same repository/source/workflow bindings;
7. preserve separate verification transcripts and keep verifier failures nonzero through `tee` with `pipefail`;
8. upload final release evidence only after both verifications succeed.

### Trusted main evidence

Trusted main Release Package run **`35969183890`** on `5b6482bfa08d075078fd0dba0e28ba361ad66628` completed **successfully**. Observed jobs/steps:

- deterministic `build-package`: success;
- exact-package smoke on `ubuntu-latest`: success;
- exact-package smoke on `macos-latest`: success;
- exact-package smoke on `windows-latest`: success;
- `attest-package`: success;
- `Generate signed build provenance attestation`: success;
- `Generate signed SBOM attestation`: success;
- `Preserve and verify attestation evidence`: success;
- `Upload attested portable release evidence`: success.

Main Evidence Workbench run `35969183904` also completed successfully for that merge revision. This verifies the trusted portable-source release path; it does **not** turn the archive into a native Windows/macOS/Linux signed installer, and it does not sign individual assessment reports.

## PR #5: structured reviewer evidence drill-down

Open PR #5 (`feat/reviewer-evidence-drilldown`) returns the sprint to Gate D/E product usability after the trusted release blocker was repaired. Base main is `5b6482bfa08d075078fd0dba0e28ba361ad66628`. The substantive feature commit is `dcbe43fef827e888335b16ab9b97721c470de892`; hosted-contract follow-up `d0658a1bc32da7c08fa8fa649f45ab48d373ae3a` adds the feature assertions to the JavaScript test file that the Workbench workflow actually executes.

The existing report data model, raw evidence, evidence digests, exports, adapters, execution authority, targets, model policy, and network behavior are unchanged. Each rendered finding now receives a structured reviewer panel **before** its existing raw evidence JSON. The panel shows only fields already recorded by the report:

- finding source and rule;
- verification state;
- confidence when a valid numeric confidence was recorded;
- optional external ID and observation time;
- allowlisted evidence context such as method, HTTP status, scope/environment, absent header, demonstrated synthetic impact, denied-control/record status;
- explicit `credentials_sent` and `customer_data_sampled` booleans when present;
- the existing evidence SHA-256.

Missing source/rule/hash data is shown as `not recorded`; the UI does not infer absent values or promote candidate evidence. The panel states that it is only a structured summary and that raw evidence remains authoritative. Raw JSON stays visible below it and is not mutated by the reviewer layer.

The feature is isolated in `workbench/static/reviewer.js` and `reviewer.css`, loaded after the existing core `app.js`. Recorded strings are assigned through `textContent`; no new `innerHTML`, model call, network request, scanner, target, filesystem access, or execution permission is introduced.

### Local feature validation

Environment: Linux, Node built-in test runner, exact authored reviewer assets at source `dcbe43fef827e888335b16ab9b97721c470de892`.

- `node --test workbench/tests/test_evidence_drilldown_ui.cjs`: **4 passed / 0 failed / 0 skipped**.
- `node --check workbench/static/reviewer.js`: **success**.

The standalone regressions cover asset ordering, normalized provenance/method/scope/hash presentation, synthetic-proof safety context with raw evidence unchanged, and untrusted recorded strings remaining text rather than markup. A full local checkout was unavailable in the development container because `github.com` resolution failed; that environment limitation is not reported as a GitHub permission denial and is not substituted for hosted evidence.

### Hosted exact-source validation

Initial published feature source `dcbe43fef827e888335b16ab9b97721c470de892` passed Evidence Workbench run `35970012530`, Workbench Startup `35970012587`, and PR-context Release Package `35970012523`. The first hosted review identified a coverage gap rather than treating those green workflows as sufficient: the standalone reviewer file was not among the JavaScript files invoked by the Workbench DOM/fetch-double command.

Commit `d0658a1bc32da7c08fa8fa649f45ab48d373ae3a` closes that gap by adding three evidence-drill-down regressions directly to the existing hosted `test_reviewer_ui.cjs` contract. On GitHub's generated PR checkout **`5b885aea83d18e1588c6d8ccd0b37fe60c52ac88`**, Evidence Workbench run **`35970372143`** completed **successfully**:

- Python 3.11 / 3.12 / 3.13 native lanes: success;
- Python 3.13: **405 tests run, 403 passed, 2 explicitly skipped, 0 failed**;
- hosted frontend DOM/fetch-double contracts: **34 passed / 0 failed / 0 skipped**, including all three new evidence-drill-down tests;
- real Chromium browser-to-loopback E2E and accessibility: success, with zero runtime exceptions reported by the existing browser harness;
- pinned Semgrep CE owned-fixture validation: success;
- real assessment-data-free local Ollama compatibility probe: success;
- fresh-checkout smoke on Ubuntu, macOS, and Windows: success;
- fail-closed Workbench validation summary: success.

For the same exact source, Workbench Startup run **`35970372302`** and PR-context Release Package run **`35970372197`** completed successfully. The release workflow in PR context continues to build and smoke the package while trusted signing remains gated off; a skipped PR signing job is not called successful signing.

At this ledger update, Basic run `35970372379` and Enterprise run `35970372303` were still in progress. Basic had completed dependency installation and Flake8 and was executing deterministic installation readiness. Enterprise had already completed Python 3.8 legacy-core, Python 3.10 full, Python 3.11 full, and Code Quality successfully; the Python 3.9 full lane was still installing dependencies. The security/compliance jobs are advisory/non-validating and their successful workflow steps are not security certification. MyPy/Pylint still retain their existing advisory exit semantics and are not relabeled as fail-closed clean checks. **PR #5 must not merge until fresh current-head aggregate Basic and Enterprise conclusions are reviewed.**

## Research applied to reviewer evidence UX

Current primary/comparable documentation was reviewed for this product slice; no external code or dependency was copied.

- **DefectDojo – Introduction to Findings** — https://docs.defectdojo.com/triage_findings/findings_workflows/intro_to_findings/ . A finding page separates the vulnerability data from additional details such as request/response pairs, reproduction steps, severity justification, and metadata. Applied lesson: make recorded review facts scannable without replacing the underlying evidence record.
- **DefectDojo – Findings data** — https://docs.defectdojo.com/asset_modelling/engagements_tests/os__findings/ . Findings retain required metadata plus optional tool/context fields. Applied lesson: normalize only data the finding actually carries; missing values must remain missing rather than being inferred by the UI.
- **OWASP ZAP alert metadata** — https://www.zaproxy.org/docs/alerts/90022/ and https://www.zaproxy.org/docs/alerts/220000-8/ . ZAP presents alert identity/status/risk/CWE/WASC/solution/reference metadata explicitly. The DOM-XSS guidance also recommends text DOM APIs rather than inserting untrusted strings as HTML. Applied lesson: give reviewers an explicit recorded-facts panel and keep all report-sourced strings on `textContent` paths.

This research is architecture/UX evidence only. It does not make HackGPT's verification states equivalent to ZAP or DefectDojo states, and no third-party parser/runtime dependency was added.

## Preserved reliability, AI, privacy, and execution boundaries

The original Workbench and later contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, pinned Semgrep runner, delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution, terminal-persistence-failure handling, conservative retesting, and trusted package-attestation verification.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the implemented reference adapter, not a mandatory gateway. Deterministic no-AI remains available. Localhost transport does not attest local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority, or upgrades candidate evidence to verification.

Autonomous tests use owned synthetic fixtures, denied controls, and redacted canaries only. No external target exploitation, real credential/customer-row collection, payload deployment, persistence, lateral movement, paid inference, public deployment, or upstream outreach is part of this work. Raw internal exports remain sensitive and are not universally sanitized client handovers.

## Remaining validation and product work

1. **Finish exact-head validation for PR #5.** Read Basic `35970372379` and Enterprise `35970372303` to completion. If either fails, use the exact completed job logs and repair the defect rather than merging around it. If both succeed and the head/base have not moved, review the five-file PR diff and merge with the expected head SHA.
2. **Verify post-merge main separately.** A merged feature needs current main Workbench/browser/startup/package/Basic/Enterprise evidence; historical PR green is not main green.
3. **Keep release claims bounded.** Trusted package provenance/SBOM generation and verification are now proven on main, but the portable source package is not a native signed installer and advisory security/compliance/performance jobs are not certifications or benchmarks.
4. **Continue Gate D/E product work after the reviewer slice.** Prefer concrete reviewer/action/model/startup value demonstrated by live code and tests over cosmetic additions or expanding into an unrelated security platform.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, PR package smoke from trusted-main signing, and portable-source packaging from native installers. A green historical run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries, and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
