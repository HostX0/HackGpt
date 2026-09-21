# Evidence Workbench review-preview release notes

## 0.1.0 review preview

This is an isolated contribution under `workbench/`; it does not replace the legacy HackGPT entry points and is not a claim of complete penetration-testing coverage.

### Implemented

- Loopback single-operator assessment UI and token-authenticated local API.
- Explicit authorization/scope capture with Analyst and Controlled verification modes.
- Evidence-first report model with finding/evidence digests, hash-linked events and report integrity checks.
- Owned disposable authorization/data proof using a denied control and fresh synthetic canary.
- Shared assessment deadline/cancellation across native DNS, TCP connect, TLS, HTTP response and current Ollama transport.
- SQLite running checkpoints, atomic terminal publication, non-durable failure state and interruption recovery.
- Candidate-only scanner-result parsers for Semgrep JSON, Trivy JSON and Nuclei JSONL; these do not execute those tools.
- Finite execution registry with typed declarations, operator authority ceiling, a metadata-only project adapter and one bounded HEAD-only web adapter.
- Durable adapter plan/approval/execution lifecycle with exact request-digest binding, minimized stored summaries, authenticated API/GUI controls and versioned execution receipts.
- Coverage-aware retesting and checksummed reviewer evidence bundles.
- Current Ollama adapter with explicit local/cloud processing policy and synthetic protocol self-tests.
- Machine-readable review manifest, CycloneDX SBOM for the isolated shipped component and a revision-generated synthetic sample report.
- Real Chromium browser-to-loopback E2E in CI using the actual token-authenticated server/UI, responsive widths 1440/768/390, accessibility-tree naming checks, keyboard traversal, owned synthetic controlled-verification flow, history rendering and runtime-exception monitoring.
- Fresh-checkout smoke jobs on GitHub-hosted Ubuntu, macOS and Windows runners using only the isolated standard-library workbench path. The smoke starts the real loopback server, exercises authenticated health/adapter discovery, completes the owned synthetic verification, checks durable persistence/integrity and exports the saved report.

### Experimental or incomplete

- Third-party scanner binaries/images are not bundled or executable from the new workbench; parser support is not runner support.
- Authenticated external application test accounts/role runners are not implemented.
- Live real-model compatibility/performance has not been established by CI protocol doubles.
- The current real browser E2E is Chromium on GitHub-hosted Ubuntu; it is not a multi-browser compatibility claim and does not replace manual assistive-technology review.
- Cross-platform fresh-checkout smoke now covers GitHub-hosted Ubuntu/macOS/Windows, but a signed release-grade installer/container package is not yet produced.
- The current review manifest remains conservative about release-level E2E/cross-platform attestation until validation aggregation is explicitly wired into the release-evidence artifact.
- Future third-party runner packaging still needs pinned binary/image versions, checksums, licenses, sandbox boundaries and SBOM entries before those tools can be described as shipped.
- Application-level encryption at rest and multi-user/public hosting are unsupported.

### Safety and interpretation

`candidate` and `observed_only` are not equivalent to demonstrated exploitation. `verified_in_lab` applies only to the owned synthetic fixture. `not_reproduced` is not renamed fixed. No findings in executed checks is not a security guarantee. Hashes are unsigned and do not prove authorship.

No external target, customer database, reusable credential, paid AI request, persistence or lateral movement is part of the review-preview validation path.
