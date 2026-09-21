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
- Versioned execution-plan/receipt contracts with minimized request summaries and object/request/time accounting.
- Coverage-aware retesting and checksummed reviewer evidence bundles.
- Current Ollama adapter with explicit local/cloud processing policy and synthetic protocol self-tests.
- Machine-readable review manifest, CycloneDX SBOM for the isolated shipped component and a revision-generated synthetic sample report.

### Experimental or incomplete

- Execution receipts are implemented at the registry boundary but are not yet fully wired through every durable assessment/API/GUI path.
- Third-party scanner binaries/images are not bundled or executable from the new workbench.
- Authenticated external application test accounts/role runners are not implemented.
- Live real-model compatibility/performance has not been established by CI protocol doubles.
- Browser-to-server E2E and keyboard/accessibility validation are not yet release evidence.
- Cross-platform fresh-install smoke testing, signing and release-grade installer/container packaging remain incomplete.
- Application-level encryption at rest and multi-user/public hosting are unsupported.

### Safety and interpretation

`candidate` and `observed_only` are not equivalent to demonstrated exploitation. `verified_in_lab` applies only to the owned synthetic fixture. `not_reproduced` is not renamed fixed. No findings in executed checks is not a security guarantee. Hashes are unsigned and do not prove authorship.

No external target, customer database, reusable credential, paid AI request, persistence or lateral movement is part of the review-preview validation path.
