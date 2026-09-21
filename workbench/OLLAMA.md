# Ollama gateway and processing policy

Current contract, updated 2026-09-21. This supersedes the historical local-inference-only direction in Contributions 02–03. Ollama remains the only AI integration; locally running and cloud-backed models share the same assessment/evidence contract. AI may also be explicitly disabled.

## Transport is not inference location

`LocalRuntime` retains its name for compatibility and connects only to `127.0.0.1` on port `11434`, or the integer port in `HACKGPT_OLLAMA_PORT`. The transport does not follow redirects or proxy variables. Direct remote endpoints, workbench-held API keys, automatic sign-in, model pulls and automatic fallback are not implemented. Cloud access is through an operator-managed, already configured Ollama daemon.

Two independent controls exist:

| Control | Meaning |
|---|---|
| Model processing policy | `local_only` by default, or `cloud_allowed` after explicit boolean `allow_cloud: true`. |
| Assessment authorization | Declared target, mode, approval and finite action/request budgets, enforced independently of the model. |

Choosing a stronger or cloud-backed model does not grant more tools, widen scope or convert model text into evidence. Deterministic native checks remain available without AI.

## Consent and minimized disclosure

The GUI has an unchecked **Allow cloud processing for this assessment** control. It is disabled with AI off. Consent is reset on model/scope/authorization changes and after submitting a run; stale discovery or preflight results cannot apply old consent to a new selection. No first model is selected automatically. A submitted run records its immutable choice; resetting the next-run form does not revoke an already-dispatched request. Cancellation is currently checkpoint-based, not instantaneous.

The report's AI context is a deliberately restricted projection: environment/mode, finding IDs, native rule IDs, severity, verification state, remediation, check status/result and limitations. The current builder omits target URLs, authorization references, HTTP bodies, header values, raw proof material and credentials. Do not describe this as a general-purpose scrubber: future imported text, code and richer adapters require their own minimization and disclosure review. Reports stored locally still contain sensitive assessment information and are not encrypted at rest.

`allow_cloud` is strictly boolean in the scope, runtime and model endpoints; strings/numbers are rejected. A cloud consent flag with AI disabled is invalid. Operators must have permission to disclose the allowed fields under the engagement's data-processing terms. The workbench cannot verify a customer's legal consent from a checkbox and does not attest provider retention policy.

For local-only operation, cloud-like names and `remote_host`/`remote_model` catalog/show metadata are rejected before chat. For cloud-approved operation they are allowed and labeled `cloud_reported`. Aliases without `cloud` in the name are also checked. A local-reported model remains local-reported even when cloud is permitted; opting in does not force cloud use.

Metadata may be incomplete, misleading or change between check and inference. It is **not** an egress guarantee. Strong local-only deployments should configure the running Ollama service with `OLLAMA_NO_CLOUD=1`, restart it and enforce network controls separately. A response reporting unauthorized remote execution is rejected, but rejection cannot undo a prompt already sent by a misconfigured daemon.

## Model operations

All workbench model endpoints require the existing local session token and Host/Origin checks.

| Endpoint | Accepted body | Operation |
|---|---|---|
| `GET /api/models` | None | Local-only discovery; no inference. |
| `POST /api/models/discover` | Optional boolean `allow_cloud` | Discovery for the selected policy; no inference. |
| `POST /api/models/check` | Exact `model`, optional booleans `require_tools`, `allow_cloud` | Catalog and `/api/show`; no inference. |
| `POST /api/models/self-test` | Same closed fields as check | Fixed synthetic response/tool probes; model usage applies. |
| `POST /api/runs` | Existing assessment fields plus optional boolean `allow_cloud` | Bounded assessment with its recorded processing choice. |

Model endpoints reject extra fields such as target, prompt or credentials. The legacy health field `local_only: true` refers only to server binding; `local_only_scope: server_binding` and `ai_processing_policies` make this distinction explicit.

Every chat checks catalog/show again. The selected model must exist and report `completion`; tool-directed synthetic verification also requires `tools`. Unknown or unsupported capabilities are not guessed. Model parameters/quantization are display metadata, not a measured hardware recommendation.

### Structured response compatibility

The official Ollama structured-output documentation currently states that Ollama Cloud does not support structured outputs. Local-reported models use `format` with the schema (`server_schema`). Cloud-reported models instead receive the same schema as a trusted instruction and omit the unsupported `format` field (`prompt_then_validate`). The application still validates exact JSON keys, types and limits. This is **not** constrained decoding or a guarantee that the model will comply; malformed output fails explicitly without repair by another model.

Tool selection remains separately validated: one declared function, empty arguments, no arbitrary shell/filesystem/network action, at most two planning responses and one approved synthetic verification. Model text cannot change the independent result state.

### Explicit Test response

The GUI now exposes the previously implemented backend self-test. It never starts automatically. A fixed JSON readiness prompt is followed, when requested, by an inert `workbench_self_test` tool-call compatibility prompt. The returned function is validated but never executed; the probe has no execution callback. It does not receive target, authorization, findings, evidence or scanner content. Up to two inference requests may consume local compute or provider usage.

`inference_compatible` means only that these fixed contracts were satisfied in that probe. It is not assessment evidence, a quality/GPU benchmark, future reliability promise or proof of offline processing.

## Usage and error handling

Each assessment reports its model, processing policy, reported location and explicit approval. `inference_attempts` counts chat dispatch attempts after local byte validation, not metadata requests. `prompt_eval_count` and `eval_count` are retained only when valid nonnegative integer counters are returned. Unknown counters remain null. Aggregated counts are null when the received responses lack complete counter coverage; unreported failed calls remain outside those sums and are disclosed. `billing_cost` is null; no financial estimate is made.

Sampling/context/output settings stay bounded (`num_predict: 768`, `num_ctx: 4096`, temperature zero). These are requested daemon options, not proof of provider-side token enforcement. Maximum request/response bytes are 65,536/262,144; maximum messages is 16, with one declared tool per request. Quota/busy responses do not trigger retry, sign-in or model substitution. Error categories distinguish invalid policy/model, unreachable service, auth required, missing model, incompatible capabilities, oversized/malformed/incomplete/truncated output and denied actions. Thinking traces and arbitrary response metadata are not retained.

Socket timeouts remain per blocking operation, not a hard overall deadline; hard cancellation/deadlines are still roadmap priorities. Live provider authentication, cloud inference and GPU/model performance have not been tested in this development environment.

## Validation boundary

The test suite uses real owned loopback HTTP servers implementing a synthetic Ollama protocol, plus direct unit fixtures. A combined integration test traverses the workbench API, fake cloud-backed gateway, assessment engine, SQLite persistence and export integrity. No live model or cloud account is used. JavaScript tests use DOM/fetch doubles, not browser-to-server E2E. Read [PROGRESS.md](PROGRESS.md) and the exact commit's CI output for observed counts; a configured workflow is not a successful run.

## Primary references

Checked 2026-09-21; revisit capability assumptions when upgrading Ollama.

- Cloud via local gateway: https://docs.ollama.com/cloud
- Structured-output limitation and schema usage: https://docs.ollama.com/capabilities/structured-outputs
- Tool calling: https://docs.ollama.com/capabilities/tool-calling
- Chat response usage fields: https://docs.ollama.com/api/chat
- Local-only service configuration: https://docs.ollama.com/faq
