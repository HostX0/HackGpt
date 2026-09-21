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
| Analyst | One HTTP metadata request; optional local-model interpretation and structured report | No exploitation; missing headers do not establish practical impact. |
| Controlled verification | Baseline plus an independently checked authorization canary in an ephemeral synthetic lab; optional bounded model selection of the approved action | Proof applies only to the deliberately vulnerable local fixture, never to an external website. |

Controlled mode requires separate approval. With AI disabled, the approved synthetic proof runs deterministically. With AI enabled, the model can request the single approved action or stop. A skipped action remains inconclusive. It cannot choose a new target, supply command arguments, access a shell or files, or remove the budget.

For public websites, external verification is currently **skipped / not implemented**. A lab result is never substituted for external-target evidence.

### Synthetic proof walkthrough

Select **Built-in synthetic lab**, then **Controlled verification**. Enter a non-secret authorization reference, confirm permission and approval, and start the assessment.

The engine starts a disposable HTTP fixture on loopback. A control route rejects unauthenticated access; a deliberately vulnerable route returns a fresh synthetic marker without credentials. The verifier checks both responses and hashes the marker. No real records, account credentials, shell access or data extraction are involved. Tests also run a corrected fixture and ensure that the proof is not reported as successful.

### Included

- Responsive browser interface: session unlock, scope form, execution modes, live timeline, findings, coverage, AI commentary, history and JSON/Markdown exports.
- Native HTTP metadata inspection: one HEAD request, no body capture or redirects, public web ports 80/443, private-address rejection and DNS-pinned sockets.
- Synthetic verification with a denied control and per-run marker; maximum three native HTTP requests and one assessment worker at a time.
- Finding fingerprints, independent evidence hashes, ordered hash-linked events and finalized report checksums.
- SQLite history, integrity validation on persistence/export and restrictive file permissions where supported.
- Optional Ollama interpretation and allowlisted lab action selection; runtime-validated JSON and no fabricated fallback.
- Token-authenticated API, strict Host/Origin validation, no CORS enablement, CSP/no-store responses, body limits and cancellation checkpoints.

**Not included yet:** ZAP, Nuclei, Semgrep, Trivy or Nmap adapters; authenticated application scans; private-network target scopes; external exploit verification; broad business-logic tests; multi-user hosting; report signing; PDF export; an all-tools installer.

## Local Ollama

Ollama is optional and separate. Choose an already installed local model with structured-output support; model-directed verification also needs tool-calling support. Click **Detect**, then use an exact installed model name. Models are not downloaded automatically.

Configure the **Ollama service itself** with `OLLAMA_NO_CLOUD=1`. Setting this variable only in a workbench process does not reconfigure an already-running Ollama server. Cloud-tagged and explicitly remote models are filtered, but the client cannot independently attest the server's networking behavior.

The client connects only to `127.0.0.1:11434`. An operator can change the local port through `HACKGPT_OLLAMA_PORT`; there is no remote endpoint field. Model context excludes raw HTTP bodies, arbitrary response-header values and authorization notes. An unavailable server, missing model or invalid response is recorded as a limitation.

Live model inference and GPU performance were not tested for this first contribution. Orchestration and schema contracts were tested with controlled response fixtures.

## Interpreting results

`observed_only` is not proof of exploitation. `verified_in_lab` is restricted to the synthetic fixture. A run can be completed, partial, errored or cancelled. Completion means the selected checks finished, not that the whole target is secure.

**No findings is not a security guarantee. A failed or skipped verification does not prove that exploitation is impossible.** Coverage and unsupported tests remain visible.

Checksums are unsigned: they detect changes relative to a trusted digest and internal inconsistencies, not authorship. Someone with complete write access can recompute all hashes.

Reports default to `~/.hackgpt-workbench` and are **not encrypted at rest** in this preview. Treat the database/exports as sensitive, use an encrypted device and manage retention deliberately. Authorization references must not contain secrets.

## Validation

```bash
python -m unittest discover -s workbench/tests -v
python -m compileall -q workbench
node --check workbench/static/app.js
```

Node is only needed for the optional JavaScript syntax check, not application runtime. The new GitHub Actions workflow is configured for Python 3.11, 3.12 and 3.13, without a legacy installer or external scans. Inspect actual hosted run status before claiming CI success.

The initial development session also ran offline Chromium layout/interaction checks at 1440, 768 and 390 pixels with mocked fetch transport and real synthetic-lab report data. That harness is not included in this contribution. These checks are **not browser-to-server E2E**. The checked-in native tests separately exercise the actual loopback HTTP API, storage and exports. Full validation limitations are recorded in [PROGRESS.md](PROGRESS.md).

## Before wider deployment

The standard-library HTTP server is intended here for a local single-user preview, not public production hosting. Multi-user isolation and a production service need separate engineering and review.

Cancellation happens at checkpoints, not by instantly interrupting active I/O. Per-socket timeouts exist, but the system resolver and slow reads are not yet covered by one enforceable wall-clock deadline. Atomic terminal-status publication, stronger deadline enforcement and cross-version special-address tests are immediate follow-up work.

See [ROADMAP.md](ROADMAP.md) for staged development. This is a tested starting point, not a complete penetration-testing suite.

## References

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/faq
- https://docs.python.org/3/library/http.server.html
