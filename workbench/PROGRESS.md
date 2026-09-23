# Evidence Workbench current development ledger

## Active milestone: review-readiness hardening (in progress)

This is the live continuation ledger for the fork-only follow-up PR. PR #1 was merged into **HostX0/HackGpt** at `2048e59143b568fa80c1736a3d02921491252eef`; it was not submitted or accepted upstream. Historical ledgers remain preserved in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md) and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). The current file is intentionally concise and is not a rewrite of those historical records.

The product direction remains practical and bounded: preserve the legacy application and the Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require independent finite tool approval, and report limitations rather than universal coverage. No owner-side installation/testing is required for this continuation.

## Current reproduced state before this repair

The exact source head examined for this round was `bd2d0503122069535fe7af59ba9632b541c7947a`; GitHub generated PR checkout `f8a2a47d97a66a6d7ae033a4dacdb81a53104266` against fork main `2048e59143b568fa80c1736a3d02921491252eef`.

Hosted results at that source head:

- **Basic CI `35853090283`: success.** The deterministic installation readiness check, legacy import smoke, lint, Docker build and Docker `--help` smoke all passed. Its Bandit job remains an advisory report, not a clean-security certification.
- **Workbench Startup `35853089986`: success.** This validates the managed startup checks for that source head only; the cooperating-process lock does not cover unchanged legacy/embedding entry points or distributed storage.
- **Release Package `35853089980`: success.** The exact portable source archive passed Ubuntu/macOS/Windows package smoke. It remains a source archive, not a signed Windows/macOS native installer.
- **Evidence Workbench `35853090121`: failure.** Browser E2E, real local-model compatibility, pinned Semgrep-container validation and fresh-install smoke on Ubuntu/macOS/Windows succeeded, but the native Python 3.11/3.12/3.13 lanes all failed in `test_current_doc_links_resolve_inside_portable_component`. The exact error was a UTF-8 decode failure in `workbench/PROGRESS.md` at byte position 3315 (`0x9d`). This is a documentation-byte defect in the current source, not an application or browser failure, and it still makes the aggregate Workbench workflow red.
- **Enterprise CI `35853090163`: failure.** Code Quality passed fail-closed Black 26.5.1, Flake8, MyPy and Pylint. Python 3.9/3.10/3.11 full dependency unit/integration lanes passed. The Python 3.8 legacy-core lane installed its bounded profile and passed 26 unit tests, then failed both integration tests because `hackgpt.py` still imports `cvsslib` directly while `cvsslib>=1.0.0` has no Python 3.8 distribution. Docker/performance were consequently skipped. Security-report jobs are advisory evidence, not certification.

These observations supersede older failure descriptions for this exact source only. In particular, the old LDAP/PortAudio setup, missing test paths, artifact-v3, psutil/aiohttp and Black-format blockers must not be described as current blockers unless they regress in a newer run.

## Current repair candidate

This round repairs the source-integrity defect that made every native Workbench lane fail before the rest of its review-documentation assertions could complete:

- Replace the corrupted current `PROGRESS.md` byte stream with UTF-8 text while preserving links to the immutable historical ledgers instead of attempting to recover or reinterpret corrupted bytes.
- Keep the existing link-resolution and claim regressions unchanged; no assertion is weakened or skipped.
- Keep the still-unresolved Python 3.8 `cvsslib` import blocker explicit rather than mixing it with the Workbench documentation repair.

Local candidate validation is run against the exact portable Workbench tree extracted from Release Package run `35853089980`, with only the candidate `PROGRESS.md` bytes changed for the published repair. The existing review-documentation link-resolution assertion passed against the clean document and `python -m compileall -q workbench` succeeded. A wider local Workbench discovery run exceeded the available local execution window while still progressing and produced no observed failure before timeout; it is not counted as a full pass. The exact published commit and its hosted runs must be recorded after publication; local success is not a substitute for current-head hosted validation.

## Preserved reliability and execution boundaries

The original Workbench and subsequent contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, conservative retest states, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, and the reviewed pinned Semgrep runner. Later continuation work also preserves delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution and terminal-persistence-failure handling.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the only implemented adapter and the reference local path, not a mandatory gateway. Localhost transport does not prove local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority or turns candidate evidence into verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external target, real credential/customer row, payload deployment, persistence, lateral movement, paid inference, public deployment or upstream outreach is part of this work.

## Active blockers after this candidate

1. **Hosted current-head Workbench proof is still required.** The repaired document bytes must pass native Python 3.11/3.12/3.13 together with the existing browser/model/Semgrep/fresh-install jobs at the exact published head.
2. **Python 3.8 legacy import remains unresolved until code is repaired and retested.** The bounded profile correctly excludes `cvsslib` because no matching Python 3.8 package exists, but `hackgpt.py` still has an unused direct `import cvsslib`. A follow-up must remove or otherwise narrow that import without removing `cvsslib` from full product requirements, faking the dependency in CI or weakening the legacy import test.
3. **Enterprise aggregate/Docker follow-through depends on the Python 3.8 lane.** Current Python 3.9/3.10/3.11 and code-quality evidence is green, but the whole Enterprise workflow is not.
4. Advisory security reports and non-validating compliance/performance placeholders remain exactly that; they are not clean scans, benchmarks or certifications.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local/DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, and portable-source smoke from native signing. A green historical run never certifies a later commit. Raw internal exports remain sensitive and are not universally sanitized client handovers. No findings is not a security guarantee; failed reproduction is not proof of impossibility.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
