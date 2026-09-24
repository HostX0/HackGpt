# Evidence Workbench current development ledger

## Active milestone: review-readiness hardening (in progress)

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical ledgers remain preserved in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md) and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). The current file is intentionally concise and does not replace those records.

PR #2 was merged into fork `main` at `2cf544d46f9d6c1b4383230ff7d0aa004a8cb56d` on 2026-09-24. The fork itself is now the product target; upstream acceptance is not a release gate. The product direction remains bounded: preserve the legacy application and Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require independent finite tool approval, and report limitations rather than universal coverage. No owner-side installation/testing is required.

## Retest comparability and reviewer UX candidate

Open PR #4 (`fix/retest-comparability`) tightens Gate D and improves the reviewer-facing comparison without changing execution authority, scanners, targets or network behavior.

### Reproduced hosted regression at source `88a0e00abd2741273522d4e71558d92f14048225`

Exact PR-head Workbench run `35954369147` compiled successfully but failed its native Python lanes on all three versions. Python 3.13 job `107489436477` ran **375 tests: 371 passed, 2 failed, 2 explicitly skipped**. The two failures were both real integration regressions caused by the stricter method comparability rule:

- `test_review_api.ReviewApiTests.test_compare_endpoint_does_not_claim_fixed`: expected two comparable `not_reproduced` results but received zero.
- `test_runtime_registry_integration.RuntimeAndRegistryIntegrationTests.test_registry_web_rule_maps_to_comparable_retest_coverage`: expected one comparable `not_reproduced` result but received zero.

The cause is specific. Findings produced by `native-web-headers/1` correctly retain `evidence.method = HEAD`, while the report-level adapter check retains the exact adapter identity/version but intentionally does not duplicate per-finding evidence. The first comparability implementation therefore saw the expected `HEAD` method but no current check method and downgraded exact version-matched executions to `method_unknown`.

Other hosted paths at the same source were independently green: Workbench Startup `35954369224`, Release Package `35954369190`, Basic CI `35954369234` and Enterprise CI `35954369221`. Browser E2E, pinned Semgrep, real local-model compatibility and all three fresh-install jobs inside the failed Workbench workflow also passed. Those successes do not override the two failed native integration assertions.

### Method-comparability repair and reviewer UX

The repair makes method comparability revision-bound rather than guessed:

1. `native-web-headers/1` is the only currently declared adapter contract allowed to supply an omitted check method, and it supplies only its code-owned fixed `HEAD` method.
2. Explicit check evidence still wins when present.
3. Unknown/future adapter versions do **not** inherit that assumption; without their own recorded/declared method they remain `method_unknown` and therefore `not_retested`.
4. Adapter-version drift, missing identity, method drift and missing coverage remain conservative `not_retested` states. A stable fingerprint may still show `still_present`; it never proves comparable absence by itself.

The reviewer UI converts the retest API object into a compact human-readable review instead of dumping raw JSON. It shows whether target/environment are comparable, mode/engine drift, counts for `still_present`, `new`, `not_reproduced` and `not_retested`, per-finding reasons, and expected/observed adapter versions and methods. Output is assigned through `textContent`; no finding text becomes markup. Unsupported retest schemas fail closed. The existing `role=status` / `aria-live=polite` notice announces completion and state counts without forcing focus. Reviewer DOM/fetch regressions cover the human summary, adapter-version detail, scope drift, announcement text and unsupported-schema failure. Delayed-response/selection epoch guards remain unchanged.

### Ambiguous finding identity now fails closed at import and comparison

A further review found that `compare_reports()` built dictionaries directly from `fingerprint`. That silently dropped malformed findings without a fingerprint and silently collapsed multiple findings carrying the same fingerprint. Either behavior can corrupt reviewer counts and can turn an ambiguous instance-level comparison into an apparently precise result.

Source commits `33abf5899e42a111347588d0a9e18579fe4f7cf7` and `d27a98d605b6daeca4201e32dbc87348f5b321cd` replace that silent normalization with explicit comparison indexing validation. Both reports must contain object findings with nonempty comparison fingerprints; duplicate fingerprints in either report raise a comparison error instead of choosing one record. The existing API converts that `ValueError` into HTTP 409, so the operator gets no fabricated `still_present` / `new` / `not_reproduced` counts from ambiguous data.

Commits `c2d8de359d84bd77899ad3610a6222f06c481d1d` and `9e568e9051713195dd4845b91a5ce772fc3c5739` move the same invariant earlier to the versioned adapter-result boundary. `normalize_adapter_result()` now rejects two findings that resolve to the same asset/adapter/rule/external-id fingerprint instead of emitting an ambiguous candidate report. An adapter that legitimately reports multiple occurrences of the same rule must provide distinct stable `external_id` values; dedicated tests prove equal implicit IDs and equal explicit IDs fail closed, while distinct external IDs generate distinct fingerprints.

This is deliberately conservative rather than inventing an occurrence ID. SARIF permits a result management system to retain multiple results with the same fingerprint when distinct stable result GUIDs distinguish the instances. HackGPT's current retest report schema does not carry a separate comparison-grade instance/correlation identity, so accepting duplicates would be guesswork. DefectDojo likewise models duplicate Findings explicitly and preserves a canonical original instead of erasing duplicate records from the review model. No external code or dependency was copied.

Targeted Linux/Python 3.13 validation for the comparison identity slice before the adapter-boundary extension:

- Existing retest module plus the new integrity cases: **22 passed / 0 failed**.
- Exact standalone `workbench/tests/test_retest_identity_integrity.py`: **5 passed / 0 failed**.

Hosted Workbench run `35957883142` for exact source `d27a98d605b6daeca4201e32dbc87348f5b321cd` subsequently completed successfully. Its Python 3.13 generated-merge checkout ran **382 tests: 380 passed, 2 explicitly skipped, 0 failed**, including all five new retest identity-integrity regressions and the previously failing review/runtime integration assertions. Frontend behavior contracts ran **31 passed / 0 failed**. Real Chromium E2E, pinned Semgrep fixture, real assessment-data-free local-model compatibility, Python 3.11/3.12/3.13 and Ubuntu/macOS/Windows fresh-install jobs all passed, and the workflow's fail-closed validation summary passed. Workbench Startup `35957882956` and Release Package `35957882872` also passed for that same source. Basic `35957882912` and Enterprise `35957882883` were still in progress at the last predecessor-head read.

The adapter-boundary extension at source `9e568e9051713195dd4845b91a5ce772fc3c5739` queued fresh hosted workflows when this entry was updated; no current-head success claim is made before those runs finish. The container available to this development session could not resolve `github.com`, so an attempted independent checkout was recorded as unavailable rather than represented as local validation of that newer source.

## Research applied in this slice

Current primary/comparable references were reviewed for the specific retest/reviewer problem; no external code or dependency was copied.

- **DefectDojo Reimport** — https://docs.defectdojo.com/import_data/import_intro/reimport/ . It compares a new scan within a bounded Test/service context and preserves import history/version context; automatic close-on-absence is optional there. Applied lesson: HackGPT requires explicit comparable context and remains stricter by never auto-closing a finding from absence.
- **DefectDojo Deduplication** — https://docs.defectdojo.com/triage_findings/finding_deduplication/about_deduplication/ . Duplicate Findings remain explicit records associated with a canonical original rather than disappearing through a dictionary-key collision. Applied lesson: if HackGPT lacks an instance-level correlation identity, ambiguous duplicate fingerprints should stop comparison instead of silently dropping an occurrence.
- **OASIS SARIF 2.1.0** — https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html . Fingerprints represent logical identity, while a result management system may store multiple results with identical fingerprints when their stable result GUIDs are distinct. Applied lesson: a fingerprint cannot safely be treated as a unique occurrence identifier unless the local schema guarantees uniqueness.
- **OWASP ZAP Automation Framework / exitStatus** — https://www.zaproxy.org/docs/desktop/addons/automation-framework/ and https://www.zaproxy.org/docs/desktop/addons/automation-framework/job-exitstatus/ . ZAP keeps completion/error/warning state explicit instead of flattening output creation into success. Applied lesson: expose version/method/coverage drift as review state rather than silently accepting it.
- **W3C WAI failure F103 for WCAG 2.1 status messages** — https://www.w3.org/WAI/WCAG21/Techniques/failures/F103 . Dynamic status updates need programmatic notification without unnecessary focus movement. Applied lesson: reuse the existing polite status region to announce comparison completion/counts while keeping keyboard focus stable.

## Preserved reliability, AI and execution boundaries

The original Workbench and later contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, pinned Semgrep runner, delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution and terminal-persistence-failure handling.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the only implemented adapter and the reference local path, not a mandatory gateway. Localhost transport does not prove local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority or turns candidate evidence into verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external target, real credential/customer row, payload deployment, persistence, lateral movement, paid inference, public deployment or upstream outreach is part of this work. Raw internal exports remain sensitive and are not universally sanitized client handovers.

## Remaining validation and product work

1. **Finish exact-head validation for PR #4.** The repaired comparison, new adapter-boundary identity checks, frontend syntax/DOM tests, real Chromium E2E, fresh-install, package, Basic and Enterprise workflows must all be evaluated on the newest source before merge.
2. **Keep PR #3 independent.** Release-attestation verification remains a separate open shipping-path fix and must not be overwritten by this retest branch.
3. **Do not convert informational jobs into claims.** Advisory security reports and non-validating compliance/performance placeholders remain evidence gaps, not clean scans, benchmarks or certifications.
4. **Continue reviewer/product work after comparability is proven.** Gate D still needs wider reviewer validation and practical evidence drill-down; Gates A-E remain cumulative. Missing adapters, broader model-quality evidence and native signed installers remain outstanding where documented in [ROADMAP.md](ROADMAP.md).

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local/DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, and portable-source smoke from native signing. A green historical run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.