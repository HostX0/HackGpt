# Evidence Workbench current development ledger

## Active milestone: review-readiness hardening (in progress)

Owner-authorized continuation on 2026-09-21. The existing hourly automation was re-enabled without changing its original DTSTART, hourly cadence or COUNT=48 maximum end time. No new task, reset or extension. PR #1 merged into **HostX0/HackGpt**, not upstream. No owner installation/testing/action is required during this sprint.

The complete first-milestone ledger is preserved byte-for-byte in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), Git blob `1e3f288fa2666feac06a87558f6e01e74e8d8d9d`. Its Contributions 01-12 are dated historical checkpoints: the last entry's incomplete C/E state and 288 Python/23 JS totals are not current status. The corresponding old roadmap is preserved in [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md), Git blob `113fdd48b9d4ea10c901c6a60fd0874831014edd`. The active cumulative criteria are in [ROADMAP.md](ROADMAP.md).

## Verified historical baseline (not validation of future changes)

- Source head: `328bfda14c1e2ea458391e491c575a8ee5303b9e`.
- Hosted PR checkout: `87100841867832c72e26073bfc71ad664fe34481`.
- Merged fork main: `2048e59143b568fa80c1736a3d02921491252eef`.
- Published Workbench subtree: `87d20c356c44d1a1c7fa35f6241c0a8b58316919`.
- [Evidence Workbench 35589788372](https://github.com/HostX0/HackGpt/actions/runs/35589788372) passed its native Python 3.11/3.12/3.13, pinned Semgrep, real local-model, real Chromium browser and platform smoke jobs. This is separate from the failing legacy workflows.
- [Release Package 35589788385](https://github.com/HostX0/HackGpt/actions/runs/35589788385) passed the exact-byte Ubuntu/macOS/Windows source-package smoke and provenance/SBOM attestation path. GitHub artifact ID `10633947927`; outer ZIP SHA-256 `cb873f5247f7cde6dafa7c02fb008f06297054296fba76cca94c29b2f7a2de31`; enclosed source archive SHA-256 `9bc6b79f79aab63f14b30193d5edc8704855f35c8d57375ded0918a75a84296e`.
- The first milestone added durable adapter API/GUI execution, pinned Semgrep, real-model and browser/platform/package validation after historical Contribution 12; they were not entered into that old ledger. Their source and hosted runs, not an invented backdated narrative, establish the baseline.

The immediate continuation used that downloaded **published** package, verified both SHA-256 values and computed the local original Workbench Git subtree hash: it exactly matched the live hosted `87d20c...` subtree. It did not use the blocked unpublished draft. Local direct `git clone` could not resolve github.com; the connected GitHub reads and the already downloaded published artifact remained available. This was a local network limitation, not a permission or safety denial.

## Contribution 13: public scope/DNS repair and review/CI reconciliation

### Implemented in the candidate working tree

- Shared public-web address validation rejects multicast, deprecated IPv6 site-local addresses, zone identifiers and explicit special/transition prefixes. A mixed DNS answer fails before a transport connection; public unicast order/deduplication remain compatible. Special-purpose globally reachable anycast assignments inside the excluded prefixes are deliberately outside this conservative policy, not mislabeled universally unroutable.
- Pre-cancelled or expired DNS work is rejected before resolver dispatch. Omitting an explicit deadline no longer removes cancellation or permits an indefinite caller wait. An already-running OS resolver remains cooperative/daemon work, not forcibly killed.
- A regression traverses the real finite registry and durable adapter lifecycle using only injected DNS answers: rejection creates a sealed `failed` record with no successful receipt and no connection. It does not scan an outside target.
- README, OLLAMA, PRODUCT_DIRECTION, RELEASE_NOTES and the live roadmap/ledger now distinguish implemented Semgrep, historical live-model/E2E/package evidence, source-package attestations and unsigned sensitive assessment exports. The native `python -m workbench` entry point remains independent of legacy installation. No provider exclusivity or universal-completeness claim was added.
- All three inherited `actions/upload-artifact@v3` uses in the two legacy workflows move to v4. Their dependency-install jobs receive `libldap2-dev`, `libsasl2-dev`, `portaudio19-dev` and `python3-dev`. Original test/lint commands are retained; no additional exit-code suppression or continue-on-error is introduced.
- Fork Docker CI is explicitly build-only: no DockerHub login, credentials or image push. Its success text no longer declares production deployment readiness. Existing test/lint/security deficiencies remain visible and must be evaluated separately.
- New offline scope/cancellation/lifecycle and documentation/workflow regression tests. Historical documents are checksum-tested, not rewritten or passed off as fresh validation.

### Validation for this candidate

Local candidate based on main `2048e59143b568fa80c1736a3d02921491252eef`, validated on 2026-09-21 with Linux x86_64, Python 3.13.5 and Node 22.16.0:

- `python -m unittest discover -s workbench/tests -v`: **342 discovered, 341 passed, 1 skipped, 0 failures/errors**, in 29.830 seconds. The skipped test is the existing opt-in real Semgrep-container integration; Docker is unavailable locally. It is not counted as a pass.
- The added tests include **9** offline scope/DNS/cancellation/durable-lifecycle regressions and **8** documentation/workflow consistency regressions. Adversarial cases were first reproduced against the unchanged source; the repaired candidate passes them. No external assessment connections are made by these fixtures.
- `node --test workbench/tests/*.cjs`: **28 passed, 0 failed/skipped**. These are DOM/fetch behavior contracts, not browser E2E.
- Workbench Python compilation, both frontend JavaScript syntax checks and structural YAML parsing of both modified legacy workflows passed. YAML parsing is not GitHub runner execution.
- `python -m workbench.tests.fresh_install_smoke` passed: real loopback server, owned synthetic assessment, durable SQLite export and history. No live model or external target was used.
- Local browser E2E and live model inference were not rerun in this contribution. The prior development browser policy denied loopback navigation; no alternate route was used to bypass that restriction. Historical hosted Chromium/model evidence above does not validate a new revision.
- No legacy dependency installation or native LDAP/PortAudio build was run locally; network/Docker availability limits remain explicit. Current hosted workflows must establish the actual result after publication.

These are candidate-working-tree results, not a claim of an uploaded feature commit or new hosted success. Record the published code commit and subsequent hosted results in the next checkpoint; preserve the distinction between PR source SHA and GitHub checkout merge SHA.

### Confirmed legacy failures and unresolved follow-through

Historical [HackGPT CI/CD 35589788333](https://github.com/HostX0/HackGpt/actions/runs/35589788333) failed dependency installation before lint/test/import: python-ldap lacked `lber.h`, and PyAudio lacked `portaudio.h`. The security job failed setup because upload-artifact v3 is deprecated. Historical [Enterprise CI/CD 35589788387](https://github.com/HostX0/HackGpt/actions/runs/35589788387) also had setup/dependency failures. Fixing these first errors is not evidence that later legacy tests passed.

The main repository tree lacks the `tests/unit/` and `tests/integration/` directories referenced by the enterprise workflow. Broad formatter/type/dependency/runtime compatibility has not been established. Existing advisory `|| true` commands and placeholder performance/compliance echo jobs are not real passing security/performance/compliance evaluations. Do not remove assertions, replace missing legacy tests with irrelevant Workbench tests, disable workflows or conceal failures to get green status. Reproduce remaining errors against the unchanged baseline, then repair coherently within authorized scope.

### Gate impact and remaining work

Continuation A/C/D have concrete implemented progress; B still needs an additional meaningful concurrency/storage-fault slice; E needs current candidate aggregate/package runs and explicit baseline diagnosis or repair of the remaining legacy failures. The continuation is **not complete**, and historical Gates A-E passing is not an early-stop condition for this resumed work.

No external assessment target, real customer data/credentials, paid model/API calls, account provisioning, payloads, persistence, lateral movement, public deployment or upstream submission. The blocked unpublished handover draft in PR comment `5754686659` remains excluded; no replay, repackaging or alternate write route was used.

### Primary repair references

Reviewed 2026-09-21:
- https://github.com/actions/upload-artifact (v4 migration and immutable artifact names)
- https://www.python-ldap.org/en/latest/installing.html (OpenLDAP/SASL build prerequisites)
- https://people.csail.mit.edu/hubert/pyaudio/ (PortAudio/Python development prerequisites)
- https://docs.python.org/3/library/ipaddress.html and the IANA registries linked in ROADMAP.md (special-purpose classification versus the narrower public-web policy)
