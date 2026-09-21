# HackGPT Evidence Workbench

**Local-first assessment studio · version 0.1.0 · experimental foundation**

A new, isolated contribution in the **HostX0/HackGpt** fork. It does not replace or import the legacy application. It prioritizes reproducible evidence, explicit coverage and honest conclusions over broad, unverified feature claims.

Contribution initiated by **HostX0 (Abdulazeez)**, with AI-assisted implementation and review. Original HackGPT attribution is preserved. The repository's existing [LICENSE](../LICENSE) remains applicable; this contribution does not assert that the repository is MIT-licensed.

## Run

Use **Python 3.11 or newer**. No pip packages, root privileges, model download, external scanner installation or cloud account are required for the native checks and synthetic fixture.

```bash
git clone --branch feat/evidence-workbench https://github.com/HostX0/HackGpt.git
cd HackGpt
python -m workbench
```

Use `python3 -m workbench` where Python is named `python3`. Open the **private launch URL printed in the terminal**. It contains a session token in the URL fragment, which the frontend removes after reading. Do not share that launch URL. The service binds only to `127.0.0.1:8765`; do not expose it publicly or through a tunnel.

```bash
python -m workbench --port 8766 --data-dir ./local-workbench-data
```

**Do not run the legacy installer or Docker configuration for this new workbench.** Those entry points have different dependencies and behavior.

## Modes and current capabilities

| Mode | Implemented now | Boundary |
|---|---|---|
| Analyst | One HTTP metadata request; optional model interpretation through the currently implemented Ollama adapter; validated report | No exploitation; missing headers do not establish practical impact. |
| Controlled verification | Baseline plus an independently checked authorization/data canary in an ephemeral synthetic lab; optional bounded model selection of the approved action | Proof applies only to the deliberately vulnerable local fixture, never to an external website. |

Controlled mode requires separate approval. With AI disabled, the approved synthetic proof runs deterministically. With AI enabled, the model can request the single approved action or stop. A skipped action remains inconclusive. It cannot choose a new target, supply command arguments, access a shell or files, or remove the budget.

For public websites, external verification is currently **skipped / not implemented**. A lab result is never substituted for external-target evidence.

### Synthetic proof walkthrough

Select **Built-in synthetic lab**, then **Controlled verification**. Enter a non-secret authorization reference, confirm permission and approval, and start the assessment.

The engine starts a disposable HTTP fixture on loopback. A control route rejects unauthenticated access; a deliberately vulnerable route returns designated synthetic records containing a fresh `HACKGPT-SYNTHETIC-*` canary without credentials. The verifier checks both responses and records row count, schema/types and content digests. Ordinary fixture values are omitted from exported proof. A corrected fixture denies the read and produces no data summary. This demonstrates a data-boundary proof pattern without sampling real customer rows or exporting reusable credentials.

### Included

- Responsive browser interface: session unlock, scope form, execution modes, live timeline, findings, coverage, AI commentary, history and JSON/Markdown exports.
- Native HTTP metadata inspection: one HEAD request, no body capture or redirects, public web ports 80/443, private-address rejection and DNS-pinned sockets.
- Synthetic verification with a denied control, fresh canary and privacy-preserving data summary; maximum three native HTTP requests and one assessment worker at a time.
- Finding fingerprints, independent evidence hashes, ordered hash-linked events and finalized report checksums.
- SQLite history, integrity validation on persistence/export and restrictive file permissions where supported.
- Versioned scanner-result contract (`hackgpt.adapter-result/v1`) that forces imported findings to `candidate`; an adapter cannot self-promote a result to independently verified.
- Conservative retest comparison with `still_present`, `new`, `not_reproduced` and `not_retested`; absence alone never means fixed.
- Portable unsigned evidence-review ZIP bundles with JSON/Markdown and a checksummed manifest.
- Optional Ollama interpretation and allowlisted lab action selection; runtime-validated JSON and no fabricated fallback.
- Token-authenticated API, strict Host/Origin validation, no CORS enablement, CSP/no-store responses, body limits and cancellation checkpoints.

**Not included yet:** executable ZAP, Nuclei, Semgrep, Trivy or Nmap adapters; authenticated external application scans; private-network target scopes; external exploit verification; broad business-logic tests; multi-user hosting; report signing; PDF export; hard end-to-end deadlines; crash-safe restart recovery; an all-tools installer.

## AI architecture: local-first, provider-neutral contracts

The workbench's evidence, action and report contracts are **not tied to where inference runs**. Ollama is the **only AI adapter implemented in this preview**, and it remains our reference path for operator-controlled local inference. It is not a permanent product-wide gateway requirement. Future reviewed adapters may support self-hosted inference or third-party APIs without changing target authorization, action allowlists, evidence authority or report semantics.

The current Ollama adapter connects to the operator's daemon at `127.0.0.1:11434` (port configurable with `HACKGPT_OLLAMA_PORT`). A local gateway connection does **not** mean the selected model runs locally. Select an exact model already available through that daemon; there are no automatic downloads, account sign-ins, provider substitutions or cloud fallbacks.

The default processing policy is **Local only**. Enable **Allow cloud processing for this assessment** to use a cloud-backed Ollama model. This consent does not expand target scope or tool permissions. Normalized rule IDs, severities, proof states, remediation, check outcomes and limitations may leave the device. Target URLs, authorization notes, credentials and raw evidence are omitted by the current native context builder. This is minimization, not a universal secret-detection guarantee for future adapters. Customer/provider policies and usage limits still apply.

Cloud approval is not saved globally. The GUI resets it when the selected model or assessment scope changes and after a run is submitted. In-flight requests cannot be unsent; an active run uses its recorded configuration and can be cancelled at checkpoints. For a stronger local-only deployment, configure the **running Ollama daemon** with `OLLAMA_NO_CLOUD=1`, restart it and apply appropriate egress controls. Model metadata is not egress attestation.

**Detect** lists policy-eligible model names without changing the selected model. **Check model** inspects metadata without inference. **Test response** explicitly sends fixed synthetic prompts to check response/tool contracts; it sends no assessment content, executes no tool and can consume model usage. Neither check measures assessment quality, GPU performance or vulnerability coverage.

Capabilities are checked independently of execution location. Current Ollama documentation says cloud models do not support server-constrained structured outputs; the cloud path therefore requests the same JSON contract in a trusted prompt and validates the response in application code. Invalid/truncated output remains an AI error, never a fabricated finding. A model that supports analysis but not tools can still be used in Analyst mode.

Reports retain the chosen processing policy, model, reported execution location, request attempts and token counts **when returned by the daemon**. Missing usage is unknown, not zero; no price or billing estimate is invented. See [OLLAMA.md](OLLAMA.md) for the exact implemented adapter contract and limitations. Live local/cloud model inference has not yet been validated; automated model tests use synthetic loopback protocol fixtures.

## Reviewer APIs and evidence

Finalized intact reports can be exported as JSON/Markdown and, through the authenticated loopback API, as `export.bundle.zip`. The bundle contains an unsigned checksum manifest. This makes review more portable; it is not a digital signature or authorship attestation.

The compare endpoint accepts two stored finalized runs and reports conservative change states. A prior finding absent from a later run is `not_reproduced` only when the scope is comparable and the mapped check completed. Otherwise it is `not_retested`. The workbench never labels a finding fixed solely because it disappeared.

The adapter-result contract is execution-neutral. It is deliberately implemented before scanner execution so future parsers/runners cannot redefine the evidence model. Real scanner adapters remain a roadmap item and must declare coverage, permissions/effect and versions before execution is added.

## Interpreting results

`candidate` is imported scanner evidence that has not been independently verified. `observed_only` is a native observation, not proof of exploitation. `verified_in_lab` is restricted to the synthetic fixture. A run can be completed, partial, errored or cancelled. Completion means the selected checks finished, not that the whole target is secure.

**No findings is not a security guarantee. A failed or skipped verification does not prove that exploitation is impossible.** Coverage and unsupported tests remain visible.

Checksums are unsigned: they detect changes relative to a trusted digest and internal inconsistencies, not authorship. Someone with complete write access can recompute all hashes.

Reports default to `~/.hackgpt-workbench` and are **not encrypted at rest** in this preview. Treat the database/exports as sensitive, use an encrypted device and manage retention deliberately. Authorization references must not contain secrets.

## Validation

```bash
python -m unittest discover -s workbench/tests -v
python -m compileall -q workbench
node --check workbench/static/app.js
node --test workbench/tests/test_ollama_ui.cjs
```

Node is only needed for JavaScript syntax and behavior tests, not application runtime. The GitHub Actions workbench workflow runs on Python 3.11, 3.12 and 3.13 without a legacy installer or external scans. Validation counts and exact run limitations are recorded in [PROGRESS.md](PROGRESS.md).

The initial development session also ran offline Chromium layout/interaction checks at 1440, 768 and 390 pixels with mocked fetch transport and real synthetic-lab report data. That harness is not included in this contribution. These checks are **not browser-to-server E2E**. The checked-in native tests separately exercise the actual loopback HTTP API, storage and exports.

## Release gates and remaining engineering

The standard-library HTTP server is intended here for a local single-user preview, not public production hosting. Multi-user isolation and a production service need separate engineering and review.

Cancellation happens at checkpoints, not by instantly interrupting active I/O. Per-socket timeouts exist, but the system resolver, slow reads and model calls are not yet covered by one enforceable wall-clock deadline. Atomic terminal-status publication, interruption/restart recovery, real scanner execution, browser E2E/accessibility and fresh-install packaging remain material release gaps.

[ROADMAP.md](ROADMAP.md) defines measurable cumulative Gates A–E. Missing gates are not treated as accessories, and the sprint should not stop early until the declared milestone's gates actually pass. [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) defines the professional assessment lifecycle and evidence/privacy principles.

Successful workbench CI produces a revision-bound review artifact with tracked source, the existing LICENSE, checksums and test logs. It is not an executable release or a security certification.

## References

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/faq
- https://docs.python.org/3/library/http.server.html
