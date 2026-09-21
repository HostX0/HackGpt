"""Live local-model compatibility evidence for the bounded review workflow.

This module is executed explicitly by CI, not by unittest discovery. It talks to a real
Ollama daemon containing one preloaded small model, runs the workbench's fixed
assessment-data-free structured-output self-test, and writes a machine-readable record.
It does not run an assessment, execute a tool, use customer data, or contact a cloud
model through the workbench.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from workbench.ollama import Ollama

SCHEMA = "hackgpt.live-model-validation/v1"
DEFAULT_MODEL = "smollm2:135m-instruct-q5_K_M"
DEFAULT_DIGEST_PREFIX = "a703ae7fccb0"


def _catalog_digest(client: Ollama, model: str) -> str:
    value = client.request("/api/tags")
    models = value.get("models")
    if not isinstance(models, list):
        raise RuntimeError("Ollama catalog did not contain a model list")
    for item in models:
        if isinstance(item, dict) and item.get("name") == model:
            digest = item.get("digest")
            if not isinstance(digest, str) or len(digest) < 12:
                raise RuntimeError("Selected model did not report a usable digest")
            return digest
    raise RuntimeError("Selected live-validation model was not present in the Ollama catalog")


def main() -> int:
    model = os.environ.get("HACKGPT_LIVE_OLLAMA_MODEL", DEFAULT_MODEL)
    expected_prefix = os.environ.get("HACKGPT_LIVE_OLLAMA_DIGEST_PREFIX", DEFAULT_DIGEST_PREFIX).lower()
    output_path = Path(os.environ.get("HACKGPT_LIVE_OLLAMA_EVIDENCE", "_live_model_review/live-model-validation.json"))
    deadline_seconds = float(os.environ.get("HACKGPT_LIVE_OLLAMA_DEADLINE_SECONDS", "60"))
    if not 5 <= deadline_seconds <= 180:
        raise RuntimeError("live-model deadline must be between 5 and 180 seconds")

    client = Ollama(model=model, allow_cloud=False)
    client.set_deadline(time.monotonic() + deadline_seconds)

    digest = _catalog_digest(client, model)
    normalized_digest = digest.lower().removeprefix("sha256:")
    if not normalized_digest.startswith(expected_prefix):
        raise RuntimeError(
            f"live-validation model digest mismatch: expected prefix {expected_prefix}, got {digest}"
        )

    result = client.self_test(require_tools=False)
    telemetry = client.telemetry()
    if result.get("state") != "inference_compatible":
        raise RuntimeError("real model did not satisfy the fixed workbench inference contract")
    if result.get("execution_location") != "local_reported":
        raise RuntimeError("real-model validation was not reported as local inference")
    if result.get("processing_policy") != "local_only" or result.get("cloud_processing_approved") is not False:
        raise RuntimeError("real-model validation did not preserve local-only policy")
    if result.get("assessment_data_sent") is not False or result.get("self_test_scope") != "synthetic_self_test":
        raise RuntimeError("real-model probe crossed the assessment-data-free self-test boundary")
    if result.get("tool_calling_tested") is not False:
        raise RuntimeError("live compatibility job must not execute or require a tool call")
    if telemetry.get("inference_attempts") != 1 or telemetry.get("responses_received") != 1:
        raise RuntimeError("live-model validation expected exactly one inference request/response")
    if telemetry.get("execution_location") != "local_reported":
        raise RuntimeError("telemetry did not preserve local-reported processing location")

    document = {
        "schema": SCHEMA,
        "checked_out_revision": os.environ.get("GITHUB_SHA", "unknown"),
        "provider": "ollama",
        "model": model,
        "model_digest": digest,
        "expected_digest_prefix": expected_prefix,
        "processing_policy": result["processing_policy"],
        "execution_location": result["execution_location"],
        "cloud_processing_approved": False,
        "structured_output_tested": result.get("structured_output_tested") is True,
        "tool_calling_tested": False,
        "assessment_data_sent": False,
        "self_test_scope": "synthetic_self_test",
        "inference_attempts": telemetry["inference_attempts"],
        "responses_received": telemetry["responses_received"],
        "prompt_tokens_reported": telemetry.get("prompt_tokens_reported"),
        "output_tokens_reported": telemetry.get("output_tokens_reported"),
        "billing_cost": None,
        "assessment_started": False,
        "tool_executed": False,
        "external_assessment_target": False,
        "customer_data": False,
        "note": (
            "A real preloaded model satisfied the fixed synthetic structured-output compatibility probe. "
            "This validates one model/runtime combination only; it is not a quality benchmark, a security verdict, "
            "or a claim that all Ollama/models/providers are compatible. Network isolation is supplied separately by CI."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(document, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
