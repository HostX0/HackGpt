# Evidence Workbench current development ledger

## Active milestone: reviewer evidence and product-readiness hardening

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical detail remains preserved in Git history and in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). This file records current shipping state and current-source evidence; it does not replace those historical records.

The fork itself is the product target. Upstream acceptance is not a release gate. Preserve the retained application and Evidence Workbench, keep deterministic no-AI operation, require finite independently approved tool execution, maintain local-first/provider-neutral model contracts, and report limitations rather than universal coverage. No owner-side installation or testing is required.

## Merged foundations through PR #9

The reviewed slices remain in fork `main`:

- PR #2 preserved the original Workbench while adding reviewed startup/install, model, execution-lifecycle, report, package, CI and reliability foundations.
- PR #3 repaired trusted portable-release verification without weakening provenance/SBOM verification.
- PR #4 made retest comparison fail closed on ambiguous finding identity, missing scope identity, self-comparison and incompatible method/coverage drift; `not_reproduced` is not a fixed verdict.
- PR #5 added structured finding-evidence drill-down while preserving raw evidence as authoritative.
- PR #6 fixed explicit SQLite/HTTP resource ownership rather than suppressing resource diagnostics.
- PR #7 added coverage-aware reviewer summaries without treating `completed` as a safety verdict.
- PR #8 added reviewable AI-processing provenance and usage while keeping AI non-evidentiary.
- PR #9 added reviewable adapter lifecycle authority and a bounded 30-second DevTools startup probe without weakening browser/application assertions.

PR #9 source `d87c7d42f985a301a4a4658c98c54bfb0494c2b6` passed Evidence Workbench `35994619392`, Startup `35994619390`, PR Package `35994619373`, Basic `35994619443`, and Enterprise `35994619370`, then merged with expected-head protection and no force update into main **`ab8529b36696e70897a8c068b0f23126fef9e6ee`**. Detailed test counts, prior workflow IDs and implementation history remain in this file's Git history and the preserved continuation ledgers.

## PR #10: reviewable terminal history, durability, frontend discovery, and Windows startup

Branch `feat/run-history-lifecycle-review` starts from exact main `ab8529b36696e70897a8c068b0f23126fef9e6ee`. PR #10 is open at https://github.com/HostX0/HackGpt/pull/10 .

### Terminal run-history and durability review

The existing report/history authority is unchanged, but terminal state and persistence are now directly reviewable:

- history rows separate recorded assessment `status`, `verdict`, and `mode` instead of collapsing them into one conclusion label;
- retest options retain the recorded terminal status;
- malformed recorded timestamps fail closed to `time invalid`; missing time or target is explicitly `not recorded` rather than browser `Invalid Date` text or invented metadata;
- selected running reports show persistence pending; explicit durable reports show durable final-report state; explicit `not_durable` results show memory-only state; unrecognized durability metadata fails closed;
- explicit memory-only or unknown durability disables JSON/Markdown/bundle export and retest controls in the UI, matching the existing server-side durable-review boundary; UI state never makes a report durable;
- legacy finalized reports remain reviewable under the server's existing compatibility policy and are labeled as legacy durability metadata.

Raw report contents, SQLite atomic finalization, server export/compare checks and lifecycle authority are unchanged. Recorded strings are assigned through `textContent`; no `innerHTML`, new model call, target, scanner, filesystem/network authority, approval, schema or storage mutation is added.

### Frontend contract discovery now fails closed

The established Python-matrix workflow deliberately names selected CJS suites and therefore did not automatically execute a newly added standalone frontend contract. PR #10 adds a separate bounded, read-only `Workbench Frontend Contracts` workflow that:

- syntax-checks the reviewed frontend entry points;
- enumerates every `workbench/tests/*.cjs` contract file;
- fails if no matching contract exists;
- prints the exact files it executes;
- runs the complete Node contract set under a five-minute timeout;
- requests only `contents: read`, with no credential, attestation or write authority.

Predecessor source `956bd3bc355029cdc7535f2c7adfec8f7d56d380` ran Frontend Contracts `36006443204` successfully on Ubuntu 24.04.5 / Node 22.23.2: **6 contract files, 73 passed, 0 failed, 0 skipped, 0 cancelled**. That exact log also emitted GitHub's current warning that `actions/checkout@v4` and `actions/setup-node@v4` target deprecated Node 20 action runtimes and were being forced onto Node 24 by the hosted runner.

The workflow therefore now uses **`actions/checkout@v7`** and **`actions/setup-node@v7`**, matching the current upstream action documentation. `setup-node` also sets `package-manager-cache: false` because this contract job installs no npm dependencies and does not need automatic package-manager caching. Checkout v7 also carries current safer fork-PR handling. This is CI plumbing only; it does not expand repository permissions or execute untrusted code with privileged triggers. The job remains `pull_request`, `contents: read`, and no secrets/signing authority.

Earlier predecessor source `b5129555afd0f535199e00993fa50ab5d2b6fe15` passed Evidence Workbench `36004572114`, Startup `36004572000`, PR-context Package `36004572006`, Frontend Contracts `36004572124`, and Basic `36004572001`. Enterprise `36004571986` had Python 3.8 legacy-core, Python 3.9/3.10/3.11 full unit/integration lanes, Code Quality, advisory security and non-validating compliance jobs successful while its non-publishing Docker build was still in progress at the last exact read. Those results remain source-bound. Advisory jobs are not clean-security/compliance certification claims.

### Windows launcher runtime selection and no-download policy

The Windows helper previously preferred `py -3`, which could ignore the runtime selected by `actions/setup-python`; a hosted Windows startup lane exposed that as a real timeout. PR #10 first changed `start.cmd` to prefer the already configured `python` command on PATH while retaining `py -3` as a compatibility fallback. The Python `start.py` entry point still enforces Python >=3.11 and retains all startup/preflight checks.

Current primary-source review identified a second reliability/privacy boundary in modern Windows Python behavior: the current CPython install-manager documentation states that `python`/`py` may automatically install a runtime when none is installed, controlled by `PYTHON_MANAGER_AUTOMATIC_INSTALL`, and enabled by default. A dependency-free launcher must not silently turn a missing runtime into a download/install operation.

Current implementation commits `b5dc4d874ea1ecb65ef819df903711456bf2d346` and `d48b95ec19f5e66bb255d5748c6e5d5ad584aa17` set the documented boolean **`PYTHON_MANAGER_AUTOMATIC_INSTALL=false` before either launcher probe** and bind that ordering with a static regression. Existing fallback compatibility remains; a missing runtime follows the existing explicit requirement failure instead of authorizing an implicit install. The regression also retains the contract that the helper contains no explicit `pip install`, `py install`, `pymanager install`, PowerShell download command, curl, or wget path.

This setting is local to the launcher process. It does not modify the user's global Python-manager configuration, install/uninstall runtimes, or download packages.

### Current-source validation boundary

The current implementation source before this ledger update is **`d48b95ec19f5e66bb255d5748c6e5d5ad584aa17`**. This ledger update creates a newer documentation successor, so all required validation must run again on that exact successor before merge. Historical or predecessor greens do not certify it.

Merge gate for PR #10 remains cumulative:

1. exact latest source: Evidence Workbench including real Chromium browser E2E/accessibility = success;
2. Workbench Frontend Contracts = success and every CJS contract discovered/executed using the current action versions;
3. Workbench Startup = success on Ubuntu/macOS/Windows;
4. PR Release Package = deterministic build + exact-package Ubuntu/macOS/Windows smoke success; pull-request signing remains intentionally unavailable and is not called successful signing;
5. Basic CI = success including Docker build/test;
6. Enterprise CI = success including Python 3.8 legacy-core, 3.9/3.10/3.11 full unit/integration, fail-closed Black/Flake8, and non-publishing Docker build;
7. final main/head and diff review immediately before expected-head, non-force merge;
8. merged main is verified separately; trusted main package signing/attestation must execute rather than being inferred from PR smoke.

## Research applied this round

No external code or dependency was copied.

- **CPython Windows documentation** — https://docs.python.org/3/using/windows.html and current `Doc/using/windows.rst`. It documents `PYTHON_MANAGER_AUTOMATIC_INSTALL`, default-enabled automatic runtime installs, and the boolean setting used by the launcher. Applied lesson: disable automatic runtime installation for the Workbench launcher process before probing either launch command.
- **actions/setup-python** — https://github.com/actions/setup-python . It recommends selecting Python explicitly and makes that interpreter available to subsequent `python` commands. Applied lesson: prefer the configured PATH interpreter before the multi-runtime `py` fallback.
- **actions/checkout** — https://github.com/actions/checkout . Current README is Checkout v7; v5+ moved to Node 24 and v7 adds safer fork pull-request handling. Applied lesson: do not leave a newly introduced workflow on a deprecated Node 20 action runtime.
- **actions/setup-node** — https://github.com/actions/setup-node . Current README is setup-node v7; v5+ moved to Node 24 and documents disabling automatic package-manager caching when it is not required. Applied lesson: use v7 and `package-manager-cache: false` for this dependency-free contract job.
- **OWASP ZAP History** — https://www.zaproxy.org/docs/desktop/ui/tabs/history/ . Applied only as a review-UX principle: retain separate execution/context state rather than collapsing history into a single security conclusion.

These sources inform launcher/reviewer/CI design only; HackGPT does not copy their code or claim equivalent semantics.

## Preserved AI, privacy, evidence, and execution boundaries

The retained application still uses exact scoped authorization, finite typed adapter declarations, exact-plan approval, bounded effects/requests/time/output, candidate-only imported observations, cancellation/deadline paths, durable receipts, integrity-checked reports, conservative retesting, structured reviewer evidence, coverage-aware review, explicit AI-processing provenance and trusted package-attestation verification.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the implemented reference adapter, not a mandatory gateway. Deterministic no-AI remains available. Localhost transport does not attest local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority, or upgrades candidate evidence to verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external-target exploitation, real credential/customer-row collection, payload deployment, persistence, lateral movement, paid inference, public deployment, or upstream outreach is part of this work. Raw internal exports remain sensitive and are not universally sanitized client handovers.

## Remaining validation and product work

1. **Validate the exact PR #10 successor.** Require all merge-gate workflows above on the exact newest source. If one fails, inspect its completed log and repair the failure rather than merging around it.
2. **Merge only after final review.** Re-read main and PR head immediately before merge, review the final diff, and use expected-head protection with no force update.
3. **Verify merged main separately.** Require Workbench/browser/frontend/startup/package/Basic/Enterprise on the actual merge revision. Trusted signing/attestation must run on main.
4. **Continue Gate D/E product work after shipping paths are green.** Prefer explicit model/tool/cancellation/history state, actionable reviewer flows, and dependable install/startup over cosmetic additions or platform sprawl.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, DOM contracts from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, PR package smoke from trusted-main signing, and portable-source packaging from native installers. A historical green run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries, and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
