# Evidence Workbench current development ledger

## Active milestone: post-merge release hardening (in progress)

PR #1 and the review-readiness continuation in PR #2 are now merged into the **HostX0/HackGpt** fork. PR #2 merged on 2026-09-24 at `2cf544d46f9d6c1b4383230ff7d0aa004a8cb56d`, preserving source head `f767a39351e157d0d3b573418079b1b52484577e`. This fork is the active product branch; no upstream acceptance claim is implied. Historical ledgers remain preserved in [PROGRESS_HISTORY.md](PROGRESS_HISTORY.md), [PROGRESS_CONTINUATION_HISTORY_2026-09-23.md](PROGRESS_CONTINUATION_HISTORY_2026-09-23.md) and [ROADMAP_BASELINE.md](ROADMAP_BASELINE.md).

The owner-authorized continuation remains product-focused: preserve the legacy application and Evidence Workbench, repair retained shipping paths, keep deterministic no-AI operation, require independent finite tool approval, and report exact limitations rather than universal coverage. Development continues while substantial in-purpose backlog and validation gaps remain; an old occurrence/count limit is not a product-completion criterion.

## Exact main state at merge `2cf544d46f9d6c1b4383230ff7d0aa004a8cb56d`

- **Evidence Workbench run `35950225891`: success.** This is post-merge main evidence for the native Workbench matrix; it does not certify the legacy application or every deployment environment.
- **Release Package run `35950225936`: failure after successful build and platform smoke.** `build-package` and exact-package smoke on GitHub-hosted Ubuntu, macOS and Windows all passed. In trusted main context, both `actions/attest` invocations also succeeded: build provenance attestation `49731512` and SBOM attestation `49731517` were signed, uploaded to the repository and logged through Sigstore. The final preservation/verification step then failed before evidence upload.
- The failure is **not a signing failure**. The exact job log shows `gh attestation verify "_release/.tar.gz"` followed by `failed to open local artifact`. The build job exported `package-basename`, while that verification expression read `package_basename`; GitHub therefore expanded the artifact basename to an empty string. The same workflow had used the hyphenated output successfully in the two signing steps, which is why signatures existed while verification failed.

These results supersede older pre-merge descriptions for this exact main revision only. Historical Python 3.8/cvsslib, Black, invalid UTF-8, LDAP/PortAudio, missing test path and artifact-action failures must not be repeated as current blockers unless they regress on newer evidence.

## Current release-verification repair candidate

Branch `fix/release-attestation-verification` normalizes the build output to one underscore-form key, `package_basename`, and uses that exact key for signing, verification and final artifact upload. The verification step now fails closed before cryptographic verification if the package or generated bundles are missing/empty, and rejects missing attestation IDs/URLs rather than publishing incomplete evidence.

The candidate also verifies the **exact local bundles that are preserved for reviewers** instead of merely asking the API for any matching attestation:

- build provenance bundle with predicate `https://slsa.dev/provenance/v1`;
- CycloneDX SBOM bundle with predicate `https://cyclonedx.org/bom`;
- both checks bind the artifact to this repository and `$GITHUB_SHA` through `gh attestation verify --bundle ... --source-digest`;
- provenance and SBOM verification transcripts are retained separately and included in the release-evidence artifact.

`workbench/tests/test_release_evidence.py` adds a repository-workflow regression that rejects the original hyphen/underscore output mismatch, requires the exact package expression, both bundle verifications, both predicate types, source-revision binding and retained verification transcripts. The existing regression still proves that pull-request package validation receives no attestation/OIDC write authority.

Hosted validation is required at the exact publication head before this candidate can be called repaired. In particular, pull-request CI can validate build/smoke and the static trusted-context contract, but only a trusted post-merge/main run can actually exercise OIDC signing and bundle verification. PR success therefore must not be relabeled as signed-package success.

## Research-driven design notes for this round

Primary references reviewed on 2026-09-24:

- GitHub CLI `gh attestation verify`: https://cli.github.com/manual/gh_attestation_verify — local `--bundle` verification is supported; provenance is the default predicate, while stronger policy can bind repository, signer/source revision and predicate type.
- GitHub artifact-attestation guidance: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations — SBOM attestations require an explicit non-default predicate type during verification.
- `actions/attest` v4: https://github.com/actions/attest — `bundle-path`, `attestation-id` and `attestation-url` are first-class outputs; generated bundles are JSON-serialized Sigstore bundles suitable for preservation and later verification.
- CycloneDX predicate guidance: https://cyclonedx.org/specification/overview/ — `https://cyclonedx.org/bom` is the recognized predicate type for CycloneDX BOM attestations.
- Comparable OSS release practice: Convex documents verifying a shipped archive with `gh attestation verify`, and Petiglyph documents verifying the built archives themselves rather than assuming release-level attestation availability. These informed the artifact-first verification shape; no external code was copied.

Limitation: cryptographic verification establishes signed provenance/SBOM claims for exact package bytes; it is not a security certification, native platform code signing, assessment-report signing or proof that the software is vulnerability-free.

## Preserved reliability and execution boundaries

The original Workbench and subsequent contributions remain intact: integrity-checked reports, explicit failed/skipped/inconclusive coverage, conservative retest states, exact request-digest approval, finite typed adapters, candidate-only imported observations, bounded public-web scope, durable execution receipts, cancellation/deadline paths, owned synthetic proof with a denied control, reviewed pinned Semgrep execution, delayed-response UI transaction guards, selection-bound exports/comparisons, linked-report navigation, startup diagnostics/locking, exact-once adapter lifecycle execution and terminal-persistence-failure handling.

AI remains optional and provider-neutral at the evidence/action/report boundary. Ollama is the only implemented adapter and reference local path, not a mandatory gateway. Localhost transport does not prove local inference; external processing requires explicit engagement-specific approval and minimized disclosed fields. Model output never expands scope, grants tool authority or turns candidate evidence into verification.

Autonomous tests use owned synthetic fixtures, denied controls and redacted canaries only. No external target, real credential/customer row, payload deployment, persistence, lateral movement, paid inference, public deployment or upstream outreach is part of this work.

## Remaining validation and product work

1. **Validate the exact candidate head.** Workbench, startup, package build/smoke, Basic CI and retained Enterprise paths must be read separately; a green individual job is not whole-repository release evidence.
2. **Exercise trusted attestation after review/merge.** Only the trusted main context receives OIDC/attestation authority. Both exact local bundles and final evidence upload must pass there before Gate E can count this release path repaired.
3. **Keep informational checks honest.** Advisory security output and placeholder compliance/performance jobs remain evidence gaps, not clean scans, benchmarks or certifications.
4. **Continue cumulative Gates A-E.** Broader model usefulness, controlled role execution, native signed installers and wider accessibility/reviewer validation remain substantive backlog. Do not turn decorative features or unrelated ecosystem expansion into progress.

## Verification discipline

For every newer candidate, distinguish source head from GitHub's generated PR checkout, local/DOM tests from real browser E2E, protocol doubles from live model compatibility, individual jobs from aggregate workflows, and portable-source smoke from trusted attestation/native signing. A green historical run never certifies a later commit. Raw internal exports remain sensitive and are not universally sanitized client handovers. No findings is not a security guarantee; failed reproduction is not proof of impossibility.

See [ROADMAP.md](ROADMAP.md) for cumulative Gates A-E, [README.md](README.md) and [START_HERE.md](START_HERE.md) for the current user path, [OLLAMA.md](OLLAMA.md) for model boundaries and [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for direction rather than shipped claims.
