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

## Current gate impact

- **A — evidence/document consistency:** advanced. Current claims distinguish baseline failures, source commits, hosted jobs and incomplete lanes. Historical records remain preserved.
- **B — reliability:** previously published cancellation/recovery/storage protections remain; this CI slice does not claim new runtime reliability coverage.
- **C — adapter/scope:** unchanged and preserved; no authority or scanner surface was expanded.
- **D — reviewer evidence:** advanced by revision-bound CI/formatter diagnostics without relabeling repair artifacts as successful validation.
- **E — usable release/build compatibility:** materially advanced. Black runtime installation, exact formatting and the full Enterprise code-quality job now pass, while current Basic/Enterprise runtime and Docker completion remain required before a whole-project pass.

See [ROADMAP.md](ROADMAP.md) for the cumulative acceptance criteria. Portable-source packaging is not a native signed installer, advisory security reports are not certification, and no findings is not a security guarantee.
