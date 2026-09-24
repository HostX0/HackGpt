# Evidence Workbench current development ledger

## Active milestone: reviewer evidence and product-readiness hardening

This is the live continuation ledger for the owner's **HostX0/HackGpt** fork. Historical detail remains preserved in Git history and in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md), and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md). This file records current shipping state and current-source evidence; it does not replace those historical records.

The fork itself is the product target. Upstream acceptance is not a release gate. Preserve the retained application and Evidence Workbench, deterministic no-AI operation, finite independently approved tools, local-first/provider-neutral model contracts, evidence integrity, cancellation and truthful limitations. No owner-side installation or testing is required.

## Merged foundations through PR #9

PRs #2-#9 remain in fork `main`. They preserve the original Workbench while adding reviewed startup/install and package paths, scoped execution lifecycle, report/retest integrity, evidence and coverage review, optional AI-processing provenance, explicit resource ownership, and adapter lifecycle authority. Detailed source SHAs, workflow IDs and bounded evidence remain in Git history and the continuation ledgers.

PR #9 source `d87c7d42f985a301a4a4658c98c54bfb0494c2b6` passed Evidence Workbench `35994619392`, Startup `35994619390`, PR Package `35994619373`, Basic `35994619443`, and Enterprise `35994619370`, then merged with expected-head protection and no force update into main **`ab8529b36696e70897a8c068b0f23126fef9e6ee`**.

## PR #10: terminal history, durability, frontend discovery, and Windows startup

PR #10 is open at https://github.com/HostX0/HackGpt/pull/10 on branch `feat/run-history-lifecycle-review`, based on main `ab8529b36696e70897a8c068b0f23126fef9e6ee`.

### Reviewable terminal history and persistence

The report/history authority is unchanged, but the UI now makes recorded lifecycle facts directly reviewable:

- history rows show assessment `status`, `verdict`, and `mode` separately;
- retest options retain the recorded terminal status;
- malformed timestamps fail closed to `time invalid`; missing time or target is `not recorded`;
- running reports show persistence pending, explicit durable reports show durable final state, explicit `not_durable` shows memory-only state, and unrecognized durability fails closed;
- memory-only or unknown durability disables JSON/Markdown/bundle export and retest controls in the UI, matching the server-side durable-review boundary;
- legacy finalized reports remain reviewable under the existing server compatibility policy and are labeled as legacy durability metadata.

Raw reports, SQLite atomic finalization, server export/compare authorization and execution authority remain unchanged. Recorded strings use `textContent`; no `innerHTML`, new model call, target, scanner, filesystem/network authority, approval, schema or storage mutation is introduced.

### Frontend contract discovery and current action runtimes

The main Python matrix intentionally names selected CJS suites, so it did not discover a newly added standalone frontend contract. PR #10 adds a bounded, read-only **Workbench Frontend Contracts** workflow that syntax-checks reviewed frontend entry points, enumerates every `workbench/tests/*.cjs` file, fails if none exist, prints the exact files executed and runs the full Node contract set under a five-minute timeout.

On predecessor source `956bd3bc355029cdc7535f2c7adfec8f7d56d380`, run `36006443204` succeeded on Ubuntu 24.04.5 / Node 22.23.2 with **6 contract files and 73 tests: 73 passed, 0 failed, 0 skipped, 0 cancelled**. Its exact log also emitted GitHub's warning that `actions/checkout@v4` and `actions/setup-node@v4` target deprecated Node 20 action runtimes and were being forced onto Node 24.

The new workflow therefore uses current upstream **`actions/checkout@v7`** and **`actions/setup-node@v7`**, with `package-manager-cache: false` because no npm dependencies are installed. Exact successor `75c7de007c9f73cb43156fa6f604c386d2593db4` run `36006886501` then succeeded with checkout/setup-node v7, Node 22.23.2, the same six discovered files and **73/73 passing contracts**, with the prior Node-20 deprecation warning absent from the job log. The workflow remains ordinary `pull_request`, `contents: read`, no `pull_request_target`, credentials, attestation or write authority.

### Windows launcher reliability and no-surprise installation

The Windows helper had preferred `py -3`, and a hosted Windows startup lane exposed a real timeout even though `actions/setup-python` had already selected the desired runtime on PATH. The helper now prefers the configured `python` command and retains `py -3` as a compatibility fallback. Python `start.py` still enforces Python >=3.11 and all existing startup/preflight checks.

Current CPython Windows documentation also states that modern install-manager launch aliases may automatically install a runtime when none exists, controlled by default-enabled `PYTHON_MANAGER_AUTOMATIC_INSTALL`. The launcher now sets the documented boolean **`PYTHON_MANAGER_AUTOMATIC_INSTALL=false` before either launcher probe**. This is local to the launcher process: it does not modify global Python-manager configuration, install/uninstall runtimes or download packages.

`workbench/tests/test_windows_launcher_contract.py` binds the guard-before-probes ordering, PATH-python-before-`py` fallback, identical reviewed `start.py` entrypoint, and absence of explicit `pip install`, `py install`, `pymanager install`, PowerShell download, curl or wget paths.

The dedicated Startup workflow has also moved to **`actions/checkout@v7`** and **`actions/setup-python@v7`**, matching current upstream action guidance and eliminating the exact hosted Node-20 action-runtime warning observed on its predecessor. Its three-OS matrix now explicitly runs `test_windows_launcher_contract` alongside startup/trace tests so launcher policy is not left to unrelated suite discovery.

Implementation commits for this continuation include `b5dc4d874ea1ecb65ef819df903711456bf2d346` / `d48b95ec19f5e66bb255d5748c6e5d5ad584aa17` for the documented automatic-install guard, `2208fb932115b126da394c4e6e246f5c0c5ac2b8` for current frontend action runtimes, `aba16def1ec685a6d04a31cd54a947e0363d116c` for current Startup action runtimes, and `56cdc065f9125ff30657ae5d76b075b41be11337` for executing the launcher contract in every Startup OS lane.

### Current validation boundary

This ledger commit is a documentation successor to implementation source `56cdc065f9125ff30657ae5d76b075b41be11337`; therefore every required merge gate must complete again on the exact resulting source head before PR #10 merges. Predecessor green results remain evidence only for their exact source.

Required merge gate:

1. Evidence Workbench, including real Chromium browser E2E/accessibility, native Python matrix, owned-fixture Semgrep, assessment-data-free local Ollama compatibility and three-OS fresh-install = success;
2. Workbench Frontend Contracts discovers all CJS contracts using checkout/setup-node v7 = success;
3. Workbench Startup on Ubuntu/macOS/Windows using checkout/setup-python v7, including the launcher contract = success;
4. PR Release Package deterministic build + exact-package Ubuntu/macOS/Windows smoke = success; PR signing remains intentionally unavailable and is not successful signing;
5. Basic CI including Docker build/test = success;
6. Enterprise CI including Python 3.8 legacy-core, 3.9/3.10/3.11 full unit/integration, fail-closed Black/Flake8 and non-publishing Docker build = success;
7. final main/head/diff review immediately before expected-head, non-force merge;
8. merged main verified separately, including trusted package signing/attestation rather than inference from PR smoke.

## Research applied this round

No external code or dependency was copied.

- **CPython Windows documentation** — https://docs.python.org/3/using/windows.html and current `Doc/using/windows.rst`: documents `PYTHON_MANAGER_AUTOMATIC_INSTALL`, default-enabled automatic runtime installation and the boolean manager setting. Applied: disable automatic install only for the Workbench launcher process.
- **actions/setup-python** — https://github.com/actions/setup-python: current README is v7, uses Node 24 action internals and recommends an explicitly selected Python version. Applied: current Startup action runtime and PATH-interpreter preference.
- **actions/checkout** — https://github.com/actions/checkout: current README is v7; v5+ uses Node 24 and v7 adds safer fork-PR handling. Applied to the new Frontend Contracts and Startup workflows without privileged triggers.
- **actions/setup-node** — https://github.com/actions/setup-node: current README is v7 and documents disabling automatic package-manager caching when unnecessary. Applied: v7 plus `package-manager-cache: false` for the dependency-free frontend job.
- **OWASP ZAP History** — https://www.zaproxy.org/docs/desktop/ui/tabs/history/: used only as a review-UX principle for retaining execution/context state instead of collapsing history into a security conclusion.

## Preserved boundaries and next work

The retained application still uses exact scoped authorization, finite typed adapter declarations, exact-plan approval, bounded effects/requests/time/output, candidate-only imported observations, cancellation/deadline paths, durable receipts, integrity-checked reports, conservative retesting, structured reviewer evidence, explicit AI-processing provenance and trusted package-attestation verification. Ollama remains the reference model adapter rather than a mandatory gateway; deterministic no-AI remains available. Model output never expands scope or tool authority.

Autonomous tests remain limited to owned synthetic fixtures, denied controls and redacted canaries. No external-target exploitation, credential/customer-row collection, payload deployment, persistence, lateral movement, paid inference, public deployment or upstream outreach is part of this work.

After exact-head PR #10 validation, re-read main/head and final diff, merge only with expected-head protection and no force update, then verify merged main separately. Subsequent Gate D/E work should prefer explicit model/tool/cancellation/history state, actionable reviewer flows and dependable installation/startup over cosmetic additions or platform sprawl.

## Verification discipline

Distinguish source head from GitHub's generated PR checkout, DOM contracts from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, PR package smoke from trusted-main signing, and portable-source packaging from native installers. A historical green run never certifies a later commit. No findings is not a security guarantee; failed reproduction is not proof of impossibility; `not_reproduced` is explicitly not a fixed verdict.

See [ROADMAP.md](ROADMAP.md), [README.md](README.md), [START_HERE.md](START_HERE.md), [OLLAMA.md](OLLAMA.md), and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for the retained product contract and cumulative Gates A-E.
