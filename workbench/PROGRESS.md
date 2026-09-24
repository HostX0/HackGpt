# Evidence Workbench current development ledger

## Active milestone: reviewer evidence and product-readiness hardening

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical records remain preserved in Git history and in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). This file records the current shipping state and the evidence that applies to it; it does not rewrite those historical ledgers.

The fork itself is the product target. Upstream acceptance is not a release gate. The product remains bounded: preserve the retained application and Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require finite independently approved tool execution, maintain local-first/provider-neutral model contracts, and report limitations rather than universal coverage. No owner-side installation or testing is required.

## Merged foundations

PR #2 was merged to fork `main` at `2cf544d46f9d6c1b4383230ff7d0aa004a8cb56d` on 2026-09-24. It preserves the original Evidence Workbench and subsequent contributions while adding the reviewed startup/install, model, execution-lifecycle, report, package, CI, and reliability work recorded in the historical ledgers.

PR #4 (`fix/retest-comparability`) was reviewed on exact source `a7e061f9a6bc2905d20e361d1a724ac4399fe524` and then merged with expected-head protection to fork `main` at `2032bce9228cdb404e2b2b6b3c8d8053ea515eec`. Its exact-head Evidence Workbench, Workbench Startup, Release Package, Basic CI, and Enterprise CI workflows all completed successfully before merge. The merged retest contract remains conservative: duplicate/missing finding identity fails closed; missing target/environment identity cannot become comparable absence; a run cannot be compared with itself; adapter version/method/coverage drift remains `not_retested`; and `not_reproduced` is never presented as `fixed`.

PR #5 (`feat/reviewer-evidence-drilldown`) was reviewed on exact source `e04c72453644b38440c6de4f1ff6f5f5db8aa1b3` after its Workbench, Startup, PR package, Basic CI, and Enterprise CI workflows all completed successfully. It was merged with expected-head protection to fork `main` at **`a72b6c80309c3e8039dfca0e0adbbd18dec8085e`**. The finding-review UI now exposes a structured summary of recorded source/rule/verification/context/hash facts while keeping raw evidence authoritative and unchanged. No model, target, scanner, route, or execution authority was added.

Post-merge Evidence Workbench run `35974672394` on `a72b6c80309c3e8039dfca0e0adbbd18dec8085e` completed successfully, as did Workbench Startup run `35974672386`. Trusted Release Package run `35974672487` also completed successfully: deterministic build, exact-package smoke on Ubuntu/macOS/Windows, downloaded-package identity validation, signed build provenance, signed CycloneDX SBOM, preservation and verification of both attestation bundles, and final attested portable-release evidence upload all succeeded. This remains portable-source release evidence, not native installer signing or assessment-report signing. Basic and Enterprise post-merge runs were still executing when the next reliability slice began, so their aggregate state is not reused as a repository-wide green claim here.

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

## Merged PR #5: structured reviewer evidence drill-down

The reviewer evidence slice returned the sprint to Gate D/E product usability after the trusted release blocker was repaired. Its existing report data model, raw evidence, evidence digests, exports, adapters, execution authority, targets, model policy, and network behavior are unchanged. Each rendered finding now receives a structured reviewer panel **before** its existing raw evidence JSON. The panel shows only fields already recorded by the report:

- finding source and rule;
- verification state;
- confidence when a valid numeric confidence was recorded;
- optional external ID and observation time;
- allowlisted evidence context such as method, HTTP status, scope/environment, absent header, demonstrated synthetic impact, denied-control/record status;
- explicit `credentials_sent` and `customer_data_sampled` booleans when present;
- the existing evidence SHA-256.

Missing source/rule/hash data is shown as `not recorded`; the UI does not infer absent values or promote candidate evidence. The panel states that it is only a structured summary and that raw evidence remains authoritative. Raw JSON stays visible below it and is not mutated by the reviewer layer.

The feature is isolated in `workbench/static/reviewer.js` and `reviewer.css`, loaded after the existing core `app.js`. Recorded strings are assigned through `textContent`; no new `innerHTML`, model call, network request, scanner, target, filesystem access, or execution permission is introduced. The existing native `<details>/<summary>` finding disclosure remains the interaction surface rather than adding a custom disclosure widget.

### Source-bound validation before merge

For exact feature source `254a20c0ef6aa3b826ce8827c8ee12826bdfed16`, Evidence Workbench run `35971160039` completed successfully. Python 3.13.15 on Ubuntu 24.04 ran **408 tests: 406 passed, 2 explicitly skipped, 0 failed**; hosted frontend DOM/fetch-double contracts ran **34 passed / 0 failed / 0 skipped**; real Chromium E2E/accessibility, pinned Semgrep owned fixtures, assessment-data-free local Ollama compatibility, and fresh-checkout smoke on Ubuntu/macOS/Windows all succeeded. Workbench Startup `35971159743`, PR-context Release Package `35971159715`, Basic CI `35971159907`, and Enterprise CI `35971159745` also completed successfully for that source. Later documentation-only successors received fresh source-head validation before the expected-head merge; historical green was not transferred automatically.

## PR #6: explicit runtime/test resource cleanup

Post-PR5 main Workbench run `35974672394` passed its complete matrix, but the Python 3.13 job exposed two non-failing `ResourceWarning` diagnostics worth fixing rather than suppressing: an unclosed direct SQLite connection in the adapter-lifecycle tamper regression, and an unclosed socket surfaced after Ollama HTTP error-path tests. The warnings were concrete cleanup evidence, not assertion failures or a reason to weaken warning visibility.

Branch `fix/runtime-resource-cleanup` was created from exact main `a72b6c80309c3e8039dfca0e0adbbd18dec8085e`. The implementation head before this ledger update is **`ed39cc2775c0102393ad1fb2a9de1ab27c9ad0d9`** and GitHub generated PR checkout **`3c4a4c0bccb44615251df44cc12e924fe9254338`**. Changes are deliberately narrow:

- `test_adapter_lifecycle.py` wraps the test-only direct `sqlite3.connect()` with `contextlib.closing`, so transaction context and resource ownership are both explicit;
- `LocalRuntime.request()` now explicitly closes every obtained `HTTPResponse` in `finally`, including redirect/auth/not-found/busy/service-error paths that can reject before reading a body;
- connection close remains guaranteed even when `response.close()` itself raises `OSError`;
- a focused three-case regression covers a successful catalog response, a rejected HTTP status, and response-close failure while preserving the public error state.

No provider, route, model fallback, target, scanner, tool authority, report schema, consent rule, or network destination was added. Ollama remains fixed to loopback transport from the production client.

### Exact PR #6 hosted evidence before this ledger successor

Evidence Workbench run **`35975926148`** on source `ed39cc2775c0102393ad1fb2a9de1ab27c9ad0d9` completed successfully. Its Python 3.13.15 job `107556264187` checked out generated PR merge revision `3c4a4c0bccb44615251df44cc12e924fe9254338` and ran **411 tests: 409 passed, 2 explicitly skipped, 0 failed**. The three new cleanup regressions all passed. The hosted JavaScript contracts remained **34 passed / 0 failed / 0 skipped**. Python 3.11/3.12/3.13, real Chromium E2E/accessibility, pinned Semgrep owned-fixture validation, real assessment-data-free local Ollama compatibility, and fresh-install smoke on Ubuntu/macOS/Windows all succeeded; the fail-closed Workbench aggregate completed successfully.

Crucially, the exact new Python 3.13 log contains neither of the prior application `ResourceWarning` diagnostics: the cloud-policy discovery regression completes without the prior unclosed-SQLite warning, and the mixed-public-DNS regression completes without the prior unclosed-socket warning. Unrelated GitHub Actions runner deprecation messages for Node/action internals remain visible and are not suppressed or reclassified as application cleanup failures.

Workbench Startup run **`35975926163`** completed successfully. PR-context Release Package run **`35975926125`** completed successfully for deterministic build and exact-package smoke; trusted signing remains intentionally gated off in pull-request context and is not called successful signing. At this checkpoint Basic run `35975926214` and Enterprise run `35975926105` were still in progress: Enterprise Python 3.8 `legacy-core` and fail-closed Black/Flake8 had already succeeded, while the full-runtime dependency/test lanes were still executing; Basic was still installing its full Python dependency set. Their pending state is not treated as failure or success.

This ledger commit is a newer documentation successor, so its own exact source head must receive fresh required validation before PR #6 can merge. The successful `ed39cc...` evidence remains source-bound to that implementation head.

## Research applied to reviewer evidence UX

Current primary/comparable documentation was reviewed for this product slice; no external code or dependency was copied.

- **DefectDojo – Introduction to Findings** — https://docs.defectdojo.com/triage_findings/findings_workflows/intro_to_findings/ . A finding page separates the vulnerability data from additional details such as request/response pairs, reproduction steps, severity justification, and metadata. Applied lesson: make recorded review facts scannable without replacing the underlying evidence record.
- **DefectDojo – Findings data** — https://docs.defectdojo.com/asset_modelling/engagements_tests/os__findings/ . Findings retain required metadata plus optional tool/context fields. Applied lesson: normalize only data the finding actually carries; missing values must remain missing rather than being inferred by the UI.
- **OWASP ZAP – Scan rule alert fields** — https://www.zaproxy.org/docs/contribute/scan-rules/ . ZAP's guidance keeps evidence tied to what was actually present in the request/response and keeps descriptive/remediation fields clear. Applied lesson: do not synthesize proof in the presentation layer; keep the raw recorded evidence authoritative.
- **W3C WAI-ARIA APG – Disclosure pattern** — https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ and https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-card/ . Disclosure content needs predictable keyboard-operable expansion and a clear control name/focus affordance. Applied lesson: retain the existing native finding `<details>/<summary>` disclosure and put the structured reviewer summary inside it rather than adding a parallel custom JavaScript disclosure.

This research is architecture/UX evidence only. It does not make HackGPT's verification states equivalent to ZAP or DefectDojo states, and no third-party parser/runtime dependency was added.

## Research applied to resource ownership

The PR #6 cleanup follows current Python 3.13 standard-library ownership semantics rather than hiding warnings. No external code or dependency was copied.

- **Python 3.13 `sqlite3` documentation** — https://docs.python.org/3.13/library/sqlite3.html . The `Connection` context manager commits or rolls back transactions but does not close the connection; Python 3.13 emits `ResourceWarning` when a connection is deleted without an explicit `close()`. Applied lesson: the tamper test now expresses transaction/resource ownership separately with `contextlib.closing`.
- **Python 3.13 `http.client` documentation** — https://docs.python.org/3.13/library/http.client.html . `HTTPResponse` is a closeable response stream and `HTTPConnection.close()` closes the connection. Applied lesson: the bounded Ollama transport closes both the response and connection explicitly across successful and early rejected-status paths instead of relying on connection teardown or garbage collection to release the response object.

The cleanup does not claim those docs prove every socket/resource path in the application is leak-free; the exact regression and warning-free hosted path are the bounded evidence for this slice.

## PR #6 merged and post-merge shipping evidence

The documentation successor `686f2df527f784998d9bd2617c70d19b042cda1e` subsequently received fresh exact-source validation before merge: Evidence Workbench `35976280429`, Workbench Startup `35976280402`, PR-context Release Package `35976280359`, Basic CI `35976280293`, and Enterprise CI `35976280292` all completed successfully. The PR package job remained a smoke/build check with trusted signing intentionally gated off in pull-request context.

After reviewing the four-file final diff, PR #6 was merged with expected-head protection and no force update into fork `main` at **`f3668af7539951c4efb59b44d3806ac20c3abfe2`**. Post-merge Evidence Workbench `35980900465`, Workbench Startup `35980900513`, and Basic CI `35980900492` completed successfully. Trusted Release Package `35980900508` also completed successfully: deterministic build, exact-package smoke on Ubuntu/macOS/Windows, downloaded-package identity validation, signed build provenance, signed CycloneDX SBOM, preservation and verification of both attestation bundles, and final attested portable-release evidence upload all succeeded. Post-merge Enterprise run `35980900483` was still in progress at the latest read, so repository-wide aggregate green is not claimed here.

## PR #7: coverage-aware reviewer summary

With the release and resource-ownership blockers bounded, the next Gate D/E slice improves the existing **Coverage and skipped checks** reviewer surface without adding any execution authority. Branch `feat/coverage-review-summary` starts from merged main `f3668af7539951c4efb59b44d3806ac20c3abfe2`. Current implementation source before this ledger successor is **`d7cf400d36f3bb9a5745e2e9a6b7ecbcadebc955`**; GitHub generated PR checkout **`cfa3a381c1fa31badff130ace0c773e8ce5c91e1`** for its exact Workbench run.

The reviewer layer now summarizes only already-recorded report data:

- every check is classified as `completed`, `inconclusive`, `skipped`, `error`, or fail-closed `unknown`;
- missing or unrecognized status is never promoted to `completed`;
- `completed` is explicitly defined as **the check executed**, not that the target is safe;
- recorded result, reason, bounded `objects_tested`/`objects_total`, and coverage notes are shown when present;
- recorded limitations remain visible;
- the exact raw `{checks, limitations}` JSON is appended unchanged and labeled authoritative.

The implementation writes recorded strings through `textContent`, does not use `innerHTML`, and introduces no model request, scanner invocation, target, filesystem access, network request, schema change, storage mutation, or tool authority.

### Test-integration correction and exact current evidence

The first implementation temporarily placed four new frontend regressions in a standalone CJS file. Predecessor Workbench run `35981327914` was green, but its exact Python 3.13 job log showed the hosted workflow explicitly invoked only `test_ollama_ui.cjs`, `test_reviewer_ui.cjs`, and `test_adapter_ui.cjs`; therefore that green run **did not validate the new standalone coverage test file**. The omission was not treated as a pass. The four cases were moved into the already-hosted `test_reviewer_ui.cjs` suite and the duplicate standalone file was deleted.

Exact current implementation-head Evidence Workbench run **`35981763295`** on generated PR checkout `cfa3a381c1fa31badff130ace0c773e8ce5c91e1` completed successfully. On Ubuntu 24.04 with CPython **3.13.15**, the Python suite ran **411 tests: 409 passed, 2 explicitly skipped, 0 failed**. The hosted frontend command then ran **38 JavaScript tests: 38 passed, 0 failed, 0 skipped**; tests 35–38 are the new coverage-review contracts covering mixed completed/inconclusive/skipped/error visibility, fail-closed unknown status, exact raw-record preservation, and text-only rendering of untrusted recorded strings. The workflow does not separately print the Node CLI version, so no exact Node-version claim is made.

That same current-head Workbench run also passed Python 3.11/3.12/3.13, real Chromium browser-to-loopback E2E/accessibility, pinned Semgrep owned-fixture validation, assessment-data-free live local Ollama compatibility, fresh-install smoke on Ubuntu/macOS/Windows, and its fail-closed validation summary. Workbench Startup **`35981763417`** and PR-context Release Package **`35981763310`** also completed successfully. The package run proves deterministic build and exact cross-platform package smoke in PR context; trusted signing is intentionally gated and is not claimed. Basic `35981763326` and Enterprise `35981763304` remained in progress at this ledger checkpoint. Enterprise fail-closed Black and Flake8 had already passed; MyPy/Pylint retain their existing advisory semantics.

### Research applied to coverage review

No external code or dependency was copied.

- **W3C WCAG 2 at a Glance** — https://www.w3.org/WAI/standards-guidelines/wcag/glance/ . Applied lesson: reviewer information should remain understandable, predictable, and robust rather than requiring interpretation of raw machine data for ordinary status review.
- **DefectDojo – Findings data** — https://docs.defectdojo.com/asset_modelling/engagements_tests/os__findings/ . Applied lesson: expose recorded status/context at the review surface while retaining the underlying test/finding record.
- **DefectDojo – Finding Status Definitions** — https://docs.defectdojo.com/triage_findings/findings_workflows/finding_status_definitions/ . Applied lesson: status terms represent specific lifecycle facts, not a universal safety verdict. HackGPT therefore keeps `completed` as execution state and preserves skipped/inconclusive/error/unknown coverage gaps explicitly.

These sources informed presentation semantics only; HackGPT's status model is not asserted to be equivalent to DefectDojo's.

## Preserved reliability, AI, privacy, and execution boundaries

The original Workbench and later contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, pinned Semgrep runner, delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution, terminal-persistence-failure handling, conservative retesting, structured reviewer evidence, and trusted package-attestation verification.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the implemented reference adapter, not a mandatory gateway. Deterministic no-AI remains available. Localhost transport does not attest local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority, or upgrades candidate evidence to verification.

Autonomous tests use owned synthetic fixtures, denied controls, and redacted canaries only. No external target exploitation, real credential/customer-row collection, payload deployment, persistence, lateral movement, paid inference, public deployment, or upstream outreach is part of this work. Raw internal exports remain sensitive and are not universally sanitized client handovers.

## Remaining validation and product work

1. **Finish PR #7 aggregate validation.** Re-read exact-source Basic `35981763326` and Enterprise `35981763304`. If either fails, inspect the completed failing job log and repair rather than merging around it. If both succeed, add no new code merely to create activity: review the final diff and this ledger successor, then require fresh source-head Workbench/Startup/package/Basic/Enterprise validation before expected-head merge.
2. **Verify post-merge main separately.** If PR #7 merges, re-read current main Workbench/browser/startup/package/Basic/Enterprise evidence. Trusted package signing must be exercised on main rather than inferred from PR package smoke.
3. **Keep release claims bounded.** Trusted package provenance/SBOM generation and verification are proven on main, but the portable source package is not a native signed installer and advisory security/compliance/performance jobs are not certifications or benchmarks.
4. **Continue Gate D/E product work.** Prefer concrete reviewer/action/model/startup value demonstrated by live code and tests over cosmetic additions or expanding into an unrelated security platform. Coverage summaries must remain evidence-preserving rather than becoming inferred pass/fail or safety scores.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, PR package smoke from trusted-main signing, and portable-source packaging from native installers. A green historical run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries, and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
