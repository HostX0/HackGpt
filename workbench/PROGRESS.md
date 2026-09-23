# Evidence Workbench current development ledger

## Active milestone: review-readiness hardening (in progress)

This is the live, revision-bound status. The earlier continuation ledger has been preserved byte-for-byte as [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), Git blob `7be6bb4838e99083a55fc1542f0dcd8b12e466c7`. The first-milestone ledger remains preserved separately in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), Git blob `1e3f288fa2666feac06a87558f6e01e74e8d8d9d`; its matching historical roadmap is [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md), Git blob `113fdd48b9d4ea10c901c6a60fd0874831014edd`. No historical record was rewritten.

PR #1 was merged only into **HostX0/HackGpt** at `2048e59143b568fa80c1736a3d02921491252eef`. PR #2 remains the active fork-only follow-up. The owner extended the same bounded development window on 2026-09-23 without resetting or duplicating it. No upstream submission, public deployment, paid inference or owner-side installation/testing is required by this work.

## Current delivered repair

The current CI slice fixes a reproduced Enterprise code-quality incompatibility without weakening any gate or changing the application runtime matrix:

- Enterprise keeps Python 3.8, 3.9, 3.10 and 3.11 in the real unit/integration matrix.
- Only the code-quality lane uses Python 3.11, allowing the already pinned Black `26.5.1` package to install on a supported interpreter.
- `.ci/black/` is created before quality-tool installation. The selected Python version and installed Black version are retained in diagnostics, so a future setup failure does not cascade into a misleading missing-artifact failure.
- Black remains fail-closed: `black --check --diff --no-color .` records its real exit code, diagnostics are uploaded, an exact ephemeral repair candidate is generated only on failure, then the original result is enforced. No `continue-on-error`, assertion deletion or formatter bypass was introduced.
- The Workbench workflow regression now identifies the actual Black `--check` invocation instead of incorrectly treating utility commands such as `black --version` as formatter checks.
- Root CI contract tests bind the quality lane to the compatible runtime, diagnostic files and fail-closed ordering.

Published implementation commits:

- `9625cdb592da5181bcb875c474811b4684fb179d` — compatible quality runtime, diagnostics and regression repair.
- `8e6e871ad360d93f5d207c17f5c7281213ad2c2d` — exact Black 26.5.1 formatting of the one remaining file reported by hosted CI.

Both updates advanced `fix/review-readiness` by non-force fast-forward and preserve the original Workbench, subsequent contributions, LICENSE and legacy entry points.

## Reproduced baseline failures

At source `0c0c4f9b8995cd1fe7404e453b47634c6ace55f7` / generated PR checkout `1b227780010852a380497aa52a6aaf4f4ff23e5c`:

- Basic CI `35819753021`, Startup `35819753008` and Release Package `35819753016` passed.
- Evidence Workbench `35819753044` ran 361 native Python tests on its Python 3.11 lane: **358 passed, 2 skipped, 1 failed**. The single failure was the workflow regression misclassifying `black --version`; browser E2E, the real local-model compatibility probe, pinned Semgrep-container validation and fresh-install smoke on Ubuntu/macOS/Windows all passed.
- Enterprise `35819753009` selected Python 3.9.25 for code quality and failed before formatting because Black 26.5.1 requires Python >=3.10. Its always-upload diagnostics step also failed because `.ci/black/` had not yet been created. The Python 3.9/3.10/3.11 application test jobs had passed at that checkpoint; no completion claim was made for 3.8 there.

These logs establish the repair target; they are not current-head validation.

## Focused pre-publication validation

Using the exact published package artifact from Release Package `35819753016` plus the exact hosted root workflow texts in a temporary validation tree:

- Workbench documentation/workflow regression module: **8 passed, 0 failed/skipped**.
- Root Enterprise CI contract tests: **4 passed, 0 failed/skipped**.
- `python -m compileall -q workbench tests/unit/test_enterprise_ci_contract.py`: passed.
- Both root workflow files parsed successfully as YAML.
- One complete local Workbench suite exceeded the execution tool limit before a final summary, so it is **not** counted as a completed local full-suite pass.

No external assessment target, real customer data/credentials, live external scanner target or blocked unpublished draft was used.

## Hosted validation after publication

### Source `9625cdb592da5181bcb875c474811b4684fb179d`

- Evidence Workbench `35822890367`: **success**. Python 3.11 native lane ran **361 tests: 359 passed, 2 skipped, 0 failures** in 35.935s. JavaScript DOM/fetch contracts: **29 passed, 0 failed/skipped**. Browser E2E, real local-model compatibility, pinned Semgrep-container validation, and fresh-install smoke on Ubuntu/macOS/Windows all passed in the aggregate.
- Startup `35822890363`: **success**.
- Release Package `35822890373`: **success**.
- Enterprise `35822890391`: Python 3.11.16 and Black 26.5.1 installed successfully and diagnostics were uploaded. Fail-closed enforcement then reported exactly **1 file would be reformatted and 99 left unchanged**. Formatter repair artifact `10733709416` was generated. This run correctly remained non-green until the exact formatting was committed.

### Source `8e6e871ad360d93f5d207c17f5c7281213ad2c2d`

- Startup `35823047203`: **success**.
- Evidence Workbench `35823047248`: **success**.
- Release Package `35823047290`: **success**.
- Enterprise `35823047201`, Code Quality job `107058805447`: **success**. Quality-tool installation, Black check, fail-closed enforcement, Flake8, MyPy, Pylint and report upload all completed successfully; the repair-candidate steps correctly skipped because the checkout was already formatted. The security advisory job also passed at the latest checkpoint.
- Basic CI `35823047202` and the Python 3.8-3.11 Enterprise runtime matrix/downstream Docker path were still running at the latest checkpoint. They are **not** counted as successful or complete here.

The formatter/runtime blocker is therefore closed by hosted evidence, but **whole-repository green status is not yet established**. PR #2 remains open and unmerged while the exact current Basic/Enterprise runtime and Docker paths finish or expose the next concrete blocker.


## Current reliability candidate: exact-once execution and terminal-storage truthfulness

This candidate is based on source `1f18fef08f6cd1290ba3f8a6b15eb6f13846115e`. Its exact current Workbench bytes were taken from Release Package run `35823563700`, generated PR checkout `cf3ff5e903c1c37ef5b001cc3c1c2379d8a4ee31`, artifact `10734560859`; the package itself had already passed its Ubuntu/macOS/Windows smoke jobs before this candidate was edited locally.

The reliability change closes a concrete ambiguity in the reviewed adapter lifecycle rather than widening execution authority:

- Two concurrent callers against one approved lifecycle cannot both reach the execution registry; the second caller is rejected after the first transition to `executing`.
- Adapter execution/receipt validation errors still persist their real bounded outcome when storage is healthy.
- If that terminal write fails, a recoverable second write records `interrupted` with `terminal_persistence_failed` instead of pretending the adapter itself failed. A known pre-persistence outcome may be retained only as a code such as `policy_denied`; no raw exception or request path is stored.
- If an adapter returns successfully but the durable completed receipt cannot be committed, no receipt is exposed and no durable success is claimed. The lifecycle becomes `interrupted` when the fallback write succeeds; if storage remains unavailable, the existing restart recovery converts the still-`executing` row to interrupted evidence.
- The HTTP layer returns a bounded 503 persistence error telling the operator to **Check run status** and not automatically re-execute. The existing frontend already performs a read-only status recovery rather than retrying the tool.

Focused local validation on Linux/Python 3.13 against that exact packaged Workbench plus this candidate:

- `test_adapter_lifecycle`, `test_adapter_api`, and `test_adapter_lifecycle_registry`: **21 passed, 0 failed/skipped** in 3.607s.
- `test_adapter_ui.cjs`: **6 passed, 0 failed/skipped**; DOM/fetch contracts only, not browser E2E.
- `compileall` for the changed lifecycle/server/test modules passed.
- A complete local Workbench discovery was attempted but did not finish inside the execution-tool limit, so it is **not** counted as a full-suite pass. No external target, live scanner target, model call, customer row or credential was used.

Fresh hosted state of the unmodified base `1f18fef...` at the latest pre-publication read:

- Evidence Workbench `35823563686`: **success**.
- Release Package `35823563700`: **success**; on this pull request the package/smoke path runs but trusted Sigstore attestation is intentionally not treated as an external-PR signing success.
- Workbench Startup `35823563640`: **success**.
- Basic CI `35823563775`: **success**.
- Enterprise `35823563635`: still **in progress**. Code Quality plus Python 3.9, 3.10 and 3.11 test jobs were successful; Python 3.8 was still in dependency installation at the latest read. Downstream Enterprise completion is therefore not claimed, and none of these base results validate the unpublished candidate.

## Current gate impact

- **A — evidence/document consistency:** advanced. Current claims distinguish baseline failures, source commits, hosted jobs and incomplete lanes. Historical records remain preserved.
- **B — reliability:** materially advanced by the candidate's exact-once concurrent lifecycle fixture and explicit terminal-persistence-failure path. A successful adapter return without a durable receipt is now treated as interrupted/unknown review evidence, never durable success; hosted current-head validation is still pending.
- **C — adapter/scope:** unchanged and preserved; no authority or scanner surface was expanded.
- **D — reviewer evidence:** advanced by revision-bound CI/formatter diagnostics without relabeling repair artifacts as successful validation.
- **E — usable release/build compatibility:** materially advanced. Black runtime installation, exact formatting and the full Enterprise code-quality job now pass, while current Basic/Enterprise runtime and Docker completion remain required before a whole-project pass.

See [ROADMAP.md](ROADMAP.md) for the cumulative acceptance criteria. Portable-source packaging is not a native signed installer, advisory security reports are not certification, and no findings is not a security guarantee.


## Current startup-diagnostics candidate: actionable fail-closed preflight

This candidate is based on published source `6af6d78063b8e61381d833740a4fe24d6080ec95` and changes only the dependency-free launcher diagnostics, its startup regressions and matching documentation. It does not open report storage, contact inference, start a scanner, widen adapter authority or perform automatic repair.

The existing `--check-install` preflight already tests application files, in-memory SQLite, a temporary workspace write and loopback-port availability. The candidate makes failures useful to operators and automation without exposing raw local exception details:

- machine-readable failures now include a stable `check` field plus a bounded code: `application_files` / `incomplete_application_files`, `sqlite_memory` / `sqlite_unavailable`, `workspace_write` / `workspace_not_writable`, or `loopback_port` / `loopback_port_unavailable`;
- workspace-lock contention remains separately reported as `workspace_lock` / `workspace_busy`;
- unexpected failures remain the generic `startup` / `startup_failed`;
- human-readable failure text gives one local recovery action for the stable category but never embeds the caught exception, path or socket detail;
- successful preflight semantics remain unchanged and still do not inspect/recover assessment history.

Focused local validation on Linux/Python 3.13 against the exact current release-package bytes plus this candidate:

- `workbench.tests.test_startup`: **17 passed, 0 failed/skipped** in 8.301s, including new occupied-port, workspace-write and incomplete-files failure fixtures.
- `workbench.tests.test_startup_trace`: **0 passed, 1 explicit macOS-only skip, 0 failures** on Linux.
- `python -m workbench.tests.fresh_install_smoke`: passed, completing an owned synthetic assessment and durable export with no external target or live model.
- `compileall` for the changed launcher/test modules passed.

Fresh hosted state of the unmodified base `6af6d780...` at the latest read:

- Evidence Workbench `35827760430`: **success**.
- Workbench Startup `35827760479`: **success**.
- Release Package `35827760428`: **success**.
- Basic CI `35827760528`: **success**, including legacy readiness/import plus Docker build and Docker smoke.
- Enterprise `35827760460`: still **in progress**. Code Quality, Security Advisory Reports and Python 3.9/3.10/3.11 unit/integration jobs are successful; Python 3.8 was still installing dependencies at the latest read. A transient job-log download returned `BlobNotFound` while that job was still running, so no root cause is inferred from it.

These base results do not validate this unpublished candidate. Fresh hosted startup/Workbench/package/whole-repository results are required after publication.


## Current candidate: close exact formatter drift and classify workspace preparation failures

Fresh hosted evidence for source `2671b0723de9202f17ad65ff1fedc03301bd0cb0` / generated PR checkout `33c843c82851cbdfa8920a2864630790238f31e2` established the next concrete blocker instead of relying on the previous checkpoint:

- Evidence Workbench `35835984309`: **success**.
- Workbench Startup `35835984380`: **success**.
- Release Package `35835984346`: **success**; candidate artifact `10739685879` supplies the exact tested Workbench bytes used for this round.
- Basic CI `35835984429`: **success**.
- Enterprise `35835984314`: still **in progress** at this read, but Code Quality job `107099439532` failed closed on Black 26.5.1 after reporting exactly two files needing formatting: `workbench/start.py` and `workbench/tests/test_startup.py`. Its exact hosted repair artifact is `10738997572`. Security Advisory Reports and Python 3.11 were already successful at the same checkpoint; no whole-Enterprise success is claimed.

This candidate applies the exact hosted Black repair for those two files and closes one remaining actionable startup gap without widening assessment authority:

- workspace directory resolution/creation and lock-file open failures now return `workspace_lock` / `workspace_unavailable` instead of the generic `startup_failed`;
- a symbolic-link or otherwise unsafe lock object returns `workspace_lock` / `workspace_lock_unsafe`;
- ordinary lock contention remains the existing `workspace_busy`, preserving the distinction between a live cooperating process and an unusable workspace;
- JSON and human diagnostics never expose the caught filesystem detail or local path, and no automatic repair/deletion of the lock is attempted.

Focused local validation on Linux/Python 3.13 against the exact packaged current Workbench plus this candidate:

- `workbench.tests.test_startup`: **18 passed, 0 failed/skipped** in 13.422s, including workspace-creation privacy and unsafe-symlink lock regressions.
- `workbench.tests.test_startup_trace`: **0 passed, 1 explicit macOS-only skip, 0 failures** on Linux.
- `python -m workbench.tests.fresh_install_smoke`: passed, including owned synthetic assessment and durable export with no external target or live model.
- `compileall` / Python compilation of the changed launcher and startup tests passed.
- Black 26.5.1 could not be installed in the local execution container because package-index DNS was unavailable. The exact current-head hosted formatter artifact was therefore used for the two baseline files, while the newly added lines await fail-closed hosted Black verification after publication; no local formatter pass is claimed.

No external assessment target, real credential/customer row, live scanner target, model call, blocked unpublished draft, public deployment or paid service was used.

## Current CI compatibility candidate: bounded Python 3.8 dependency profile

Source `3ab2920f0d86ef409ed2482e20bc9e26456b6971` addresses a repeatable Enterprise shipping bottleneck without deleting Python 3.8 or weakening the unit/integration matrix. On source `881575b311c3e854b06ad9abda99faa4ca7eb263`, Workbench Startup `35840399491`, Evidence Workbench `35840399451`, Release Package `35840399309` and Basic CI `35840399456` completed successfully. Enterprise `35840399529` had successful Code Quality, Security Advisory Reports and Python 3.9/3.10/3.11 test jobs while Python 3.8 remained in `Install dependencies` for hours; the preceding Enterprise run showed the same oldest-runtime stall. The completed Python 3.9 job log showed the full `requirements.txt` resolving large TensorFlow and Torch/CUDA stacks before running the retained 21 unit and 2 integration tests.

The published repair therefore keeps two distinct claims honest:

- Python 3.8 still runs the same real unit/integration tests and legacy readiness/import checks, but uses `requirements-ci-py38.txt`, a bounded profile tied by regression to `test_installation.CORE_IMPORTS` plus the import-time Jinja2 reporting dependency.
- Python 3.9, 3.10 and 3.11 still install the complete `requirements.txt`, preserving full-stack dependency validation on three runtimes. TensorFlow, Torch and Transformers are not removed from the product requirements; they are excluded only from the oldest compatibility lane where they are not required for the retained legacy import contract.
- Downstream Docker still depends on the entire matrix. No runtime was removed, no test/assertion was deleted, and no `continue-on-error` or skip was added.

Focused pre-publication validation on Linux/Python 3.13 in a temporary exact workflow/profile tree: **9 Enterprise/profile contract tests passed, 0 failed**, and the updated Enterprise workflow parsed successfully as YAML with all four runtime entries present. No external target, model call, scanner target, report/customer data, credential or blocked unpublished draft was used.

Fresh hosted runs for `3ab2920f...` were queued/in progress at publication: Evidence Workbench `35843554118`, Workbench Startup `35843554090`, Release Package `35843554235`, Basic CI `35843554297`, Enterprise `35843554070`. These are not claimed successful until their exact current-head conclusions are read.

## Current candidate: repair exact current-head CI contract drift

Fresh hosted evidence for source `3aafe689ca443e3d7468b6ff08af2c36ac4060a8` / generated PR checkout `b899c9f3cb09b3b4945fbcaaa7a93bf48723919e` identifies two bounded CI blockers while confirming the underlying compatibility work:

- Workbench Startup `35843846771`: **success**.
- Release Package `35843846701`: **success**.
- Basic CI `35843846716`: **success**.
- Evidence Workbench `35843846696`: **failure** only in native Python 3.11/3.12/3.13 lanes. The Python 3.11 lane ran **369 tests: 366 passed, 2 skipped, 1 failed**; the one failure is `test_legacy_setup_fixes_keep_real_test_and_lint_commands`, whose stale assertion still expects literal `pip install -r requirements.txt` although the reviewed Enterprise workflow now installs the matrix-selected requirements file. Browser E2E, the real local-model probe, pinned Semgrep validation and fresh-install smoke on Ubuntu/macOS/Windows all succeeded in the same aggregate run.
- Enterprise `35843846730`: **failure** at fail-closed Code Quality only. Security Advisory Reports and all four test matrix jobs passed: Python 3.8 `legacy-core` plus Python 3.9/3.10/3.11 `full`. Black 26.5.1 reported exactly one file requiring formatting, `tests/unit/test_requirements_compat.py`; because quality failed, the downstream Docker job correctly did not run. Compliance remains an explicitly non-validating coverage-gap job, not certification.

The current candidate makes two narrow repairs without weakening coverage:

- applies the exact hosted Black 26.5.1 formatting to the two long set-comprehension lines in `tests/unit/test_requirements_compat.py`, with no logic change;
- updates the Workbench workflow regression to validate the four-lane dependency contract itself: one Python 3.8 `legacy-core` profile, three `full` lanes using `requirements.txt`, and the matrix-selected install command. It no longer requires the obsolete literal command that the new matrix intentionally replaced;
- refreshes ROADMAP Gate E to the exact current evidence instead of retaining the older formatter checkpoint.

The candidate does not remove a runtime, dependency from the product requirements, test, assertion category or fail-closed check. It adds no execution authority and uses no external assessment target, model call, scanner target, credential/customer data, blocked draft, public deployment or paid service. Fresh hosted validation is still required after publication; current-head success is not claimed yet.
