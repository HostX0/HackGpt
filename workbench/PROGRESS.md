# Evidence Workbench current development ledger

## Active milestone: review-readiness hardening (in progress)

This is the live continuation ledger for the fork-only follow-up PR. PR #1 was merged into **HostX0/HackGpt** at `2048e59143b568fa80c1736a3d02921491252eef`; it was not submitted or accepted upstream. Historical ledgers remain preserved in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md) and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). The current file is intentionally concise and does not replace those records.

The product direction remains practical and bounded: preserve the legacy application and Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require independent finite tool approval, and report limitations rather than universal coverage. No owner-side installation/testing is required for this continuation.

## Exact hosted state at source `89b9c8334f5215faf498a2cff87adcf98f667f99`

Fork main was rechecked at `2048e59143b568fa80c1736a3d02921491252eef`; PR #2 remained open and unmerged. The exact source-head workflows completed as follows:

- **Evidence Workbench `35854576182`: success.** The repaired UTF-8 ledger passed the native Workbench lanes together with the existing browser/model/Semgrep/fresh-install validation. This is revision-bound evidence, not a universal compatibility or security claim.
- **Workbench Startup `35854576064`: success.** This validates the managed launcher path for this source only; unchanged legacy/embedding entry points still do not participate in its cooperating-process lock.
- **Release Package `35854576110`: success.** The portable source package passed its configured validation. It remains a portable source archive, not a signed native Windows/macOS installer or signed assessment handover.
- **Basic CI `35854576194`: success.** The retained basic installation/import/lint/Docker path is green at this exact source. Advisory security output remains advisory rather than certification.
- **Enterprise CI `35854576104`: failure.** Code Quality passed fail-closed Black 26.5.1, Flake8, MyPy and Pylint. The Python 3.11 full dependency lane passed installation, unit tests and integration tests. The Python 3.8 `legacy-core` lane passed setup, native prerequisites, its bounded dependency installation and unit tests, then failed at the integration step. Downstream Enterprise Docker/performance therefore cannot be counted as current-head passes.

The current source-level cause of the Python 3.8 integration mismatch is narrow and reproducible: `requirements-ci-py38.txt` deliberately omits `cvsslib`, because that distribution has no Python 3.8 release, and `test_installation.py::CORE_IMPORTS` already excludes it, but retained `hackgpt.py` still directly imports `cvsslib`. Repository inspection confirms that direct import is unused by `hackgpt.py`. Full `requirements.txt` still contains `cvsslib>=1.0.0` for supported full-stack runtimes, and the Python 3.9-3.11 Enterprise lanes continue to install the full requirements.

These results supersede older failure descriptions for this exact source only. Old LDAP/PortAudio setup, missing test paths, artifact-v3, psutil/aiohttp, Black-format and invalid-UTF-8 defects must not be described as current blockers unless they regress on a newer source.

## Current repair candidate

This candidate removes only the unused direct `import cvsslib` from retained `hackgpt.py`. It does **not** remove the dependency from `requirements.txt`, change any public entry point, weaken the Python 3.8 integration test, fake a package, or reduce the full Python 3.9-3.11 dependency matrix.

A regression in `tests/unit/test_requirements_compat.py` now parses `hackgpt.py` with Python's AST and binds four facts together:

1. `cvsslib` is not declared as a Python 3.8 core import.
2. `cvsslib` is not installed by the bounded Python 3.8 CI profile.
3. `hackgpt.py` does not directly import `cvsslib` again.
4. `cvsslib` remains present in the full product requirements.

The change is intentionally narrow because no use of `cvsslib` exists in the retained entry point. Fresh hosted validation at the publication commit is still required before claiming that the Python 3.8 integration lane, Enterprise Docker or aggregate Enterprise workflow is repaired.

## Preserved reliability and execution boundaries

The original Workbench and subsequent contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, conservative retest states, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, and the reviewed pinned Semgrep runner. Later continuation work also preserves delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution and terminal-persistence-failure handling.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the only implemented adapter and the reference local path, not a mandatory gateway. Localhost transport does not prove local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority or turns candidate evidence into verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external target, real credential/customer row, payload deployment, persistence, lateral movement, paid inference, public deployment or upstream outreach is part of this work.

## Remaining validation and product work

1. **Retest the exact publication head.** Workbench, Startup, Release Package and Basic CI must remain green after this source repair; historical success does not certify a newer commit.
2. **Re-run Enterprise Python 3.8.** Its real unit and integration steps must pass with the bounded profile before Docker/performance and the Enterprise aggregate can be treated as repaired.
3. **Do not convert informational jobs into claims.** Advisory security reports and non-validating compliance/performance placeholders remain evidence gaps, not clean scans, benchmarks or certifications.
4. **Gates A-E remain cumulative.** Missing adapters, broader model-quality evidence, native signed installers and wider accessibility/reviewer validation remain outstanding as documented in [ROADMAP.md](ROADMAP.md); one CI repair does not make the product universally complete.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local/DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, and portable-source smoke from native signing. A green historical run never certifies a later commit. Raw internal exports remain sensitive and are not universally sanitized client handovers. No findings is not a security guarantee; failed reproduction is not proof of impossibility.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
