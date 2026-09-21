# Ollama-only AI contract

**Status: implemented client and readiness contracts; live model inference not validated in this contribution.**

The Evidence Workbench uses **Ollama as its only AI provider**. There are no hosted-provider credentials, remote endpoint fields, cloud fallback, silent model substitution or automatic model downloads. Native deterministic checks can run with AI disabled; this is not a second AI provider. The isolated workbench does not import the legacy application. Legacy provider code elsewhere in the repository remains untouched.

## Model readiness, not an inference benchmark

1. **Detect** calls the local model catalog, displays exact installed names and reports how many cloud/remote entries were filtered.
2. **Check model** validates an installed selection through `/api/show`, rejects remote aliases, and requires the `completion` capability. Model-directed synthetic verification additionally requires `tools`.
3. Readiness shows reported parameter size, quantization and capabilities. It explicitly says `inference_tested: false` and `cloud_configuration: not_attested`.
4. AI-enabled form submission repeats the metadata check before starting a run. The transport independently repeats model/remote metadata validation before **every** chat request; browser validation is not the security boundary.
5. A stale, missing, incompatible or unreachable model produces a named error and next action. The workbench never changes the user's chosen model to hide a failure.

Metadata checking sends no assessment prompt and does not test model accuracy, structured-output quality, tokenization, available GPU memory or speed. A completion-capable model can still return invalid JSON, time out or run out of resources; those failures remain visible. Deterministic findings do not depend on model claims.

## Local transport and its limits

The only connection destination is `127.0.0.1`, using port `11434` unless `HACKGPT_OLLAMA_PORT` sets another validated local port. There is no arbitrary hostname/URL setting. The transport does not honor HTTP proxy environment variables and refuses redirects.

A local Ollama daemon can itself use a cloud-backed model. Configure **the running Ollama service** with `OLLAMA_NO_CLOUD=1` and restart it when installing a local-only deployment. Setting this variable only on the workbench client does not reconfigure an existing daemon. For a stronger offline guarantee, an operator must enforce and verify the daemon's network egress policy separately.

The client filters cloud-tagged entries and checks `remote_model` / `remote_host` in catalog and selected-model metadata. It also rejects a chat response that reports remote inference. These checks are **not an attestation**: a dishonest/compromised daemon or a model changed between checks can evade metadata assumptions. Rejecting a remote response cannot undo an already transmitted prompt. The report context therefore remains minimized, and local service integrity is part of the trust boundary.

## Enforced request contract

| Property | Current limit |
|---|---|
| API operations | `GET /api/tags`, `POST /api/show`, `POST /api/chat` only |
| Model catalog | 256 entries, exact selection, 120-character supported names |
| Encoded request / response | 64 KiB / 256 KiB |
| Chat messages | At most 16 |
| Planning | At most two model decisions and one approved synthetic action |
| Tools | At most one declared tool, with fixed name and arguments checked by the engine |
| Output / context setting | `num_predict: 768`, `num_ctx: 4096`, temperature zero |
| Model residency request | `keep_alive: 2m` |
| Socket timeout | 3 seconds for metadata; 90 seconds for chat |

The token settings are runtime parameters, not a claim of optimal model performance or guaranteed prompt fit. The byte limit does not prove that every prompt fits every tokenizer/context window. Socket timeouts are **per blocking operation**, not hard total deadlines. Cancellation/deadline improvements remain on the roadmap.

The runtime rejects caller attempts to override model, endpoint, stream mode, options or keep-alive. It requires a completed non-streaming response, rejects output-budget truncation, validates the message/tool-call shape and omits model thinking traces from retained output. Structured summaries are validated by the interpretation adapter. No shell, filesystem access, model pulls, sign-in, cloud search or arbitrary network tool is provided to a model.

## Safe diagnostics

The authenticated local API exposes:

- `GET /api/models`: catalog or a categorized diagnostic, without inference.
- `POST /api/models/check`: accepts only `model` and optional boolean `require_tools`; returns metadata or HTTP 422 with a stable error code.

Codes distinguish unreachable service, timeout, busy service, invalid port/name/catalog, missing model, missing capabilities, unsupported completion/tools, blocked cloud model, redirect, unsupported authentication, oversized context/response and incomplete/invalid output. Responses do not echo daemon error bodies, prompts, model outputs or secrets. No automatic retry or provider fallback hides an error.

## Validation and review

The added Python tests use a real loopback HTTP **protocol fixture**, not a running Ollama model. They exercise routing, response limits, errors, local-alias/capability gates and bounded chat contracts. Frontend tests use Node's built-in test runner with DOM/fetch doubles: model detection, readiness, stale-response invalidation, preflight rejection, native-only operation and double-submit prevention. They are not browser layout or browser-to-server E2E tests.

See [PROGRESS.md](PROGRESS.md) for exact local and hosted test outcomes. No model quality, GPU benchmark, successful live inference, universal offline assurance or production readiness is claimed.

## Primary references

- Ollama model listing: https://docs.ollama.com/api/tags
- Ollama chat contract: https://docs.ollama.com/api/chat
- Tool calls: https://docs.ollama.com/capabilities/tool-calling
- Structured output: https://docs.ollama.com/capabilities/structured-outputs
- Local/cloud service settings: https://docs.ollama.com/faq
- Upstream API types (`ShowResponse`, `ListModelResponse`, `ChatResponse`): https://github.com/ollama/ollama/blob/main/api/types.go

These references were consulted on 2026-09-21. API contracts can change; the client fails visibly on unrecognized capability/response formats rather than asserting compatibility.
