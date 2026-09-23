"""Fixed inference compatibility probe for the selected Ollama model.

The probe contains no assessment target, evidence, authorization reference or user
content. It verifies only whether the selected model follows the workbench's
structured-output contract and, when requested, its inert tool-call contract.
Nothing returned by this probe is security evidence and no tool is executed.
"""

from __future__ import annotations

import json
from typing import Any

from .ollama_runtime import OllamaError

_SELF_TEST_SYSTEM = (
    "You are performing a compatibility self-test. This prompt contains no "
    "security assessment data. Follow the requested response contract exactly."
)
_SELF_TEST_SCOPE = "synthetic_self_test"


def _failed(detail: str) -> OllamaError:
    return OllamaError(
        "self_test_failed",
        "The selected model did not satisfy the workbench inference contract.",
        detail + " This is a compatibility result, not a security verdict.",
    )


def validate_local_inference(
    client: Any, *, require_tools: bool = False
) -> dict[str, Any]:
    """Run a bounded, assessment-data-free compatibility probe.

    ``client`` must implement ``inspect_model`` and ``chat`` using the policy-aware Ollama
    runtime. The function never receives an execution callback, so a model tool call
    cannot cause an action even when the tool-call contract is being tested.
    """
    if not isinstance(require_tools, bool):
        raise ValueError("require_tools must be boolean")

    metadata = client.inspect_model(require_tools=require_tools)
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["ready"]},
            "scope": {"type": "string", "enum": [_SELF_TEST_SCOPE]},
        },
        "required": ["status", "scope"],
        "additionalProperties": False,
    }
    message = client.chat(
        [
            {"role": "system", "content": _SELF_TEST_SYSTEM},
            {
                "role": "user",
                "content": 'Return exactly {"status":"ready","scope":"synthetic_self_test"}.',
            },
        ],
        format=schema,
    )
    try:
        value = json.loads(message.get("content", ""))
    except (AttributeError, TypeError, json.JSONDecodeError) as exc:
        raise _failed("Structured JSON output was invalid.") from exc
    if value != {"status": "ready", "scope": _SELF_TEST_SCOPE}:
        raise _failed("Structured JSON output did not match the fixed self-test value.")

    tool_tested = False
    if require_tools:
        tool = {
            "type": "function",
            "function": {
                "name": "workbench_self_test",
                "description": "Compatibility-only no-op. Return empty arguments. The workbench will not execute it.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        }
        tool_message = client.chat(
            [
                {"role": "system", "content": _SELF_TEST_SYSTEM},
                {
                    "role": "user",
                    "content": "Call the declared workbench_self_test tool once with empty arguments.",
                },
            ],
            tools=[tool],
        )
        calls = (
            tool_message.get("tool_calls", []) if isinstance(tool_message, dict) else []
        )
        if (
            len(calls) != 1
            or not isinstance(calls[0], dict)
            or not isinstance(calls[0].get("function"), dict)
        ):
            raise _failed("Tool-calling output was missing or malformed.")
        function = calls[0]["function"]
        if (
            function.get("name") != "workbench_self_test"
            or function.get("arguments") != {}
        ):
            raise _failed(
                "Tool-calling output changed the fixed tool name or arguments."
            )
        tool_tested = True

    result = dict(metadata)
    result.update(
        {
            "state": "inference_compatible",
            "inference_tested": True,
            "structured_output_tested": True,
            "tool_calling_tested": tool_tested,
            "assessment_data_sent": False,
            "self_test_scope": _SELF_TEST_SCOPE,
            "note": (
                "A fixed synthetic prompt satisfied the selected model contract. "
                "No assessment target, evidence or authorization data was sent; no tool was executed. "
                "This does not benchmark model quality, prove security coverage or attest Ollama network egress."
            ),
        }
    )
    return result
