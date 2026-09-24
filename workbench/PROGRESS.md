# Evidence Workbench current development ledger

## Active milestone: reviewer evidence and product-readiness hardening

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical detail remains preserved in Git history and in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). This file records current shipping state and current-source evidence; it does not replace those historical records.

The fork itself is the product target. Upstream acceptance is not a release gate. Preserve the retained application and Evidence Workbench, keep deterministic no-AI operation, require finite independently approved tool execution, maintain local-first/provider-neutral model contracts, and report limitations rather than universal coverage. No owner-side installation or testing is required.

## Merged foundations

The earlier reviewed slices remain in fork `main`:

- PR #2 preserved the original Workbench while adding the reviewed startup/install, model, execution-lifecycle, report, package, CI and reliability foundations.
- PR #3 repaired trusted portable-release verification without weakening signed provenance/SBOM verification.
- PR #4 made retest comparison fail closed on ambiguous finding identity, missing scope identity, self-comparison and incompatible method/coverage drift; `not_reproduced` is never presented as `fixed`.
- PR #5 added structured finding-evidence drill-down while preserving raw evidence as authoritative.
- PR #6 fixed explicit SQLite/HTTP resource ownership rather than suppressing `ResourceWarning` diagnostics.
- PR #7 added coverage-aware reviewer summaries that keep skipped/inconclusive/error/unknown states visible and do not treat `completed` as a safety verdict.
- PR #8 added reviewable AI-processing provenance and usage while keeping AI non-evidentiary and preserving exact raw AI records.

Detailed source SHAs, prior workflow IDs and bounded evidence for those merged slices remain in this file's Git history and the preserved continuation ledgers above.

## PR #8 merged; post-merge shipping evidence

PR #8 (`feat/ai-review-summary`) was fully validated on exact source `09b162046d48bae34e01ff5af09ed1dafc008ed9`: Evidence Workbench `35988439120`, Workbench Startup `35988439068`, PR-context Release Package `35988439093`, Basic CI `35988439064`, and Enterprise CI `35988439146` all completed successfully before merge. Its final three-file diff was reviewed and merged with expected-head protection and no force update into fork `main` at **`756a87676f4439adc3d603c4074b08921e4cd702`**.

On that merged main revision, Workbench Startup `35992966219`, Basic CI `35992966173`, and trusted Release Package `35992966433` completed successfully. The trusted package path built the deterministic portable source archive, smoke-tested the exact package on Ubuntu/macOS/Windows, generated signed build provenance and CycloneDX SBOM attestations, verified the exact bundles, and uploaded final attested release evidence. This is portable-source release evidence, not native installer signing and not assessment-report signing.

Main Evidence Workbench `35992966240` did **not** complete successfully. Its browser job `107611166517` failed before page interaction because Chrome's DevTools endpoint did not become reachable inside the existing 15-second startup wait. Chrome had launched; no Workbench/browser application assertion was reached. This is the second observed occurrence of the same pre-page DevTools startup timing condition: PR #8 had previously recorded one 15-second startup timeout followed by success on the exact unchanged checkout. The repeated main failure is therefore treated as a real CI reliability defect, not erased as a one-off green retry. Post-merge Enterprise state is not reused as a repository-wide green claim in this ledger because it was not independently re-established during the current round.

## PR #9: reviewable adapter lifecycle authority

Branch `feat/adapter-lifecycle-review` starts from exact merged main `756a87676f4439adc3d603c4074b08921e4cd702`. PR #9 is open at https://github.com/HostX0/HackGpt/pull/9 . Current implementation source before this ledger successor is **`e386a85b05e01462abc45e88ca9c30d29bad0343`**; GitHub generated PR checkout **`7bb0d59f55f2d92b34fe4111ae92806fcf377b05`** for its exact Workbench run.

The existing reviewed-adapter execution boundary is unchanged, but its lifecycle is now directly reviewable before the recorded minimized preview:

- lifecycle state is normalized to `planned`, `approved`, `executing`, `completed`, `failed`, `cancelled`, `interrupted`, or fail-closed `unknown`;
- adapter identity and exact plan SHA-256 remain visible;
- declared maximum objects, requests and timeout remain visible;
- recorded outcome and receipt usage remain visible when present;
- candidate-finding count and coverage-record presence remain visible when recorded;
- `planned` explicitly means approval has not been granted;
- `approved` explicitly means the exact plan digest is approved but execution has not yet been confirmed;
- `executing` keeps Stop as a cancellation **request** until a terminal state is confirmed;
- `completed` with a durable receipt describes adapter execution only; candidate observations are not upgraded to independent verification;
- `completed` without a usable receipt is not reportable success;
- `cancelled`, `failed` and `interrupted` do not imply a successful receipt or verification;
- `interrupted` explicitly warns against automatic retry because execution may have started without durable terminal completion;
- unrecognized lifecycle state fails closed and does not infer execution, cancellation or durable completion.

Recorded strings are assigned through `textContent`; no `innerHTML`, model call, new target, scanner, filesystem authority, network authority, approval path, schema change or storage mutation is added.

### Browser contract and startup-reliability follow-through

An initial PR #9 Workbench run on source `9dfc83f1f76209ae3a4669c9f95d636788dc3507` correctly caught a browser-contract regression: the real browser E2E still attempted to JSON-parse `adapter-preview` after the UI changed it to a structured human-readable lifecycle summary. That run was not called green. The browser contract was updated to assert the visible `Lifecycle state: COMPLETED` and durable-receipt boundary while preserving the linked-report and candidate-only assertions.

During that correction, compare review detected an accidental broad rewrite of `browser_e2e.mjs`. The broad change was restored before proceeding. Relative to main, the intended browser changes are narrow: structured lifecycle assertions plus bounded DevTools startup tolerance.

Because merged main had now reproduced the 15-second DevTools startup timeout, current source `e386a85b05e01462abc45e88ca9c30d29bad0343` extends only the existing DevTools-listener wait to a bounded **30 seconds with 100 ms polling**. It does not add a blanket workflow retry, `continue-on-error`, or weaker browser/application assertions. A Chrome process exit still fails immediately and preserves captured stderr.

### Exact current implementation-head evidence

Evidence Workbench run **`35993886322`** on source `e386a85b05e01462abc45e88ca9c30d29bad0343` completed **successfully**. The exact Python 3.13 job `107614387939` checked out generated PR merge `7bb0d59f55f2d92b34fe4111ae92806fcf377b05` on Ubuntu 24.04 with CPython **3.13.15** and ran **411 tests: 409 passed, 2 explicitly skipped, 0 failed**. The hosted frontend command ran **44 JavaScript tests: 44 passed, 0 failed, 0 skipped**. New lifecycle tests are inside the already-hosted adapter suite and cover planned/unapproved authority, approved/completed receipt boundaries, cancelled/interrupted/unknown fail-closed semantics, and text-only rendering of recorded strings.

The same Workbench run passed Python 3.11/3.12/3.13, pinned Semgrep validation on owned fixtures, assessment-data-free live local Ollama compatibility, fresh-install smoke on Ubuntu/macOS/Windows, and the fail-closed validation summary. Real browser job **`107614387739`** succeeded on Ubuntu 24.04.5 / Python 3.13.15 / Node 22.23.2 / Chrome 152.0.7977.82. It exercised the owned loopback assessment, 1440/768/390 viewport checks, keyboard/accessibility checks, exact adapter planning and approval, execution, the structured completed/durable-receipt lifecycle review, linked-report review, zero external assessment targets, and no live model use; it recorded zero runtime exceptions.

Workbench Startup **`35993886298`** completed successfully. PR-context Release Package **`35993886294`** completed successfully for deterministic package build and exact Ubuntu/macOS/Windows package smoke; trusted signing is intentionally unavailable in pull-request context and is not called successful signing.

At this ledger checkpoint, Basic **`35993886364`** and Enterprise **`35993886357`** remain in progress and are therefore neither passed nor failed. Basic's test job has completed successfully while its Docker job is still building. Enterprise Python 3.8 `legacy-core` and Code Quality have completed successfully; the Python 3.9/3.10/3.11 full-runtime lanes are still progressing. Black and Flake8 remain fail-closed; MyPy/Pylint and inherited security/compliance reports retain their existing advisory/non-validating semantics.

This ledger commit is a newer documentation successor. Its own exact source head must receive fresh required validation before PR #9 can merge; the successful `e386a85...` evidence remains source-bound to that implementation head.

## Research applied to lifecycle review and browser reliability

No external code or dependency was copied.

- **OWASP ZAP Automation Framework GUI** — https://www.zaproxy.org/docs/desktop/addons/automation-framework/gui/ . Plan state plus explicit Run/Stop controls informed the decision to make HackGPT's plan/approve/run/stop lifecycle directly visible without treating Stop as confirmed termination.
- **OWASP ZAP Automation Framework** — https://www.zaproxy.org/docs/desktop/addons/automation-framework/ . Some jobs may take time to stop. Applied lesson: keep cancellation request distinct from an observed terminal state.
- **DefectDojo Finding Status Definitions** — https://docs.defectdojo.com/triage_findings/findings_workflows/finding_status_definitions/ . Status has specific workflow meaning. Applied lesson: explain HackGPT's own lifecycle semantics instead of mapping state names to inferred security conclusions.
- **DefectDojo Introduction to Findings** — https://docs.defectdojo.com/triage_findings/findings_workflows/intro_to_findings/ . Scanner discovery and verification are distinct concepts. Applied lesson: completed adapter execution remains candidate evidence until separately verified.
- **Chrome Headless debugging** — https://developer.chrome.com/docs/automation-and-testing/debug-headless and current Chromium headless test source. Chrome exposes remote debugging through the DevTools listener, whose startup is asynchronous in Chromium's own test handling. Applied lesson: use bounded startup tolerance/diagnostics rather than hiding browser failures or weakening application assertions.

These sources inform lifecycle/UX/reliability design only; HackGPT's states are not asserted to be equivalent to ZAP or DefectDojo states.

## Preserved reliability, AI, privacy, and execution boundaries

The retained application still uses exact scoped authorization, finite typed adapter declarations, exact-plan approval, bounded effects/requests/time/output, candidate-only imported observations, cancellation/deadline paths, durable receipts, integrity-checked reports, conservative retesting, structured reviewer evidence, coverage-aware review, explicit AI-processing provenance and trusted package-attestation verification.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the implemented reference adapter, not a mandatory gateway. Deterministic no-AI remains available. Localhost transport does not attest local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority, or upgrades candidate evidence to verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external-target exploitation, real credential/customer-row collection, payload deployment, persistence, lateral movement, paid inference, public deployment, or upstream outreach is part of this work. Raw internal exports remain sensitive and are not universally sanitized client handovers.

## Remaining validation and product work

1. **Finish exact-head PR #9 Basic and Enterprise validation.** Re-read Basic `35993886364` and Enterprise `35993886357`. If either fails, inspect the completed failing job log and repair rather than merging around it.
2. **Validate this documentation successor.** The PROGRESS update creates a newer source head; historical `e386a85...` green cannot be transferred automatically. Require fresh Workbench, Startup, PR Package, Basic and Enterprise results for the exact successor before merge.
3. **Merge only after final review.** Re-read main and PR head immediately before merge, review the final diff, and use expected-head protection with no force update.
4. **Verify merged main separately.** Require Workbench/browser/startup/package/Basic/Enterprise on the actual merge revision. Trusted package signing/attestation must be exercised on main rather than inferred from PR smoke.
5. **Keep browser evidence truthful.** Main's repeated 15-second pre-page timeout remains part of the record. The bounded 30-second startup change does not make future browser failures ignorable.
6. **Continue Gate D/E product work after shipping paths are green.** Prefer explicit tool/approval/cancellation/history state, actionable reviewer flows, and dependable installation/startup over cosmetic additions or platform sprawl.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, PR package smoke from trusted-main signing, and portable-source packaging from native installers. A historical green run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries, and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
