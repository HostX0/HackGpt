"""Ollama-only, loopback-only transport and metadata checks.

Metadata is not an attestation of the daemon's egress policy. Operators must
separately disable Ollama cloud features on the running service. No automatic
pull, sign-in, endpoint/provider fallback, or model substitution is supported.
"""
from __future__ import annotations

import http.client
import json
import os
import re
import socket
from typing import Any

MAX_RESPONSE_BYTES = 262144
MAX_REQUEST_BYTES = 65536
MAX_MODELS = 256
MAX_MODEL_NAME = 120
CLOUD_NOTE = (
    "Set OLLAMA_NO_CLOUD=1 on the Ollama service and restart it. "
    "This client cannot attest the daemon's cloud configuration or network egress."
)


class OllamaError(ValueError):
    """Stable, user-safe failure details; never include response bodies or prompts."""

    def __init__(self, code: str, message: str, next_step: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.next_step = next_step
        self.retryable = retryable

    def public(self) -> dict[str, Any]:
        return {"error": str(self), "code": self.code, "next_step": self.next_step,
                "retryable": self.retryable, "provider": "ollama"}


def valid_model_name(value: Any) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= MAX_MODEL_NAME
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*(?::[A-Za-z0-9][A-Za-z0-9._-]*)?", value) is not None
            and ".." not in value and "//" not in value and not value.endswith("/"))


def remote_metadata(value: dict[str, Any]) -> bool:
    # Check both fields: a cloud alias need not have 'cloud' in its visible name.
    return any(value.get(key) not in (None, "") for key in ("remote_host", "remote_model"))


class LocalRuntime:
    """Shared runtime for the workbench's only AI provider."""

    def __init__(self, model: str = "", port: int | str | None = None):
        if not isinstance(model, str) or (model and not valid_model_name(model)):
            raise OllamaError("invalid_model", "Invalid local model name.", "Select an exact installed model from Detect.")
        if "cloud" in model.lower():
            raise OllamaError("cloud_model_blocked", "Cloud-backed models are not allowed.", "Select a locally installed model.")
        value = os.getenv("HACKGPT_OLLAMA_PORT", "11434") if port is None else port
        if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).isascii() or not str(value).isdigit():
            raise OllamaError("invalid_port", "Invalid local Ollama port.", "Use an integer port between 1 and 65535.")
        self.port = int(value)
        if not 1 <= self.port <= 65535:
            raise OllamaError("invalid_port", "Invalid local Ollama port.", "Use an integer port between 1 and 65535.")
        self.model = model

    @property
    def endpoint(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def request(self, route: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        methods = {"/api/tags": "GET", "/api/show": "POST", "/api/chat": "POST"}
        if route not in methods or (data is None) != (methods[route] == "GET"):
            raise OllamaError("route_blocked", "Unsupported Ollama operation.", "Only model discovery, metadata and chat are supported.")
        if data is not None and not isinstance(data, dict):
            raise OllamaError("invalid_request", "Ollama request must be an object.", "Review the request contract.")
        body = json.dumps(data, allow_nan=False).encode("utf-8") if data is not None else None
        if body is not None and len(body) > MAX_REQUEST_BYTES:
            raise OllamaError("request_too_large", "AI context exceeds the request budget.", "Reduce the evidence summary before retrying.")
        # http.client neither reads proxy environment variables nor follows redirects.
        # Socket timeouts are per blocking operation, not an end-to-end deadline.
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=90 if route == "/api/chat" else 3)
        try:
            conn.request(methods[route], route, body=body,
                         headers={"Content-Type": "application/json", "Connection": "close"})
            response = conn.getresponse()
            if 300 <= response.status < 400:
                raise OllamaError("redirect_blocked", "Ollama redirect refused.", "Connect directly to the trusted local daemon.")
            if response.status in (401, 403):
                raise OllamaError("authentication_unsupported", "Ollama requested authentication.", "Use a local model; cloud sign-in and API keys are not supported.")
            if response.status == 404:
                raise OllamaError("not_found", "The selected model or Ollama endpoint was not found.", "Refresh installed models and check the local Ollama version.")
            if response.status in (429, 503):
                raise OllamaError("busy", "Ollama is busy or has no available capacity.", "Free local resources and retry explicitly.", retryable=True)
            if response.status != 200:
                raise OllamaError("service_error", "Ollama could not complete this request.", "Check the local daemon logs and model compatibility.")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise OllamaError("response_too_large", "Ollama response exceeds the byte budget.", "Use a smaller response or model catalog.")
            value = json.loads(raw)
            if not isinstance(value, dict) or "error" in value:
                raise OllamaError("invalid_response", "Ollama returned an invalid response.", "Check the daemon version and selected model.")
            return value
        except OllamaError:
            raise
        except (TimeoutError, socket.timeout) as exc:
            raise OllamaError("timeout", "Ollama did not respond within the socket timeout.", "Check local load or select a smaller installed model.", retryable=True) from exc
        except (json.JSONDecodeError, UnicodeDecodeError, RecursionError, http.client.HTTPException) as exc:
            raise OllamaError("invalid_response", "Ollama returned a malformed response.", "Check that the configured port belongs to Ollama.") from exc
        except OSError as exc:
            raise OllamaError("unreachable", "The local Ollama service is unreachable.", "Start Ollama and check HACKGPT_OLLAMA_PORT.", retryable=True) from exc
        finally:
            conn.close()

    def catalog(self) -> dict[str, Any]:
        models = self.request("/api/tags").get("models")
        if not isinstance(models, list) or len(models) > MAX_MODELS:
            raise OllamaError("invalid_catalog", "Invalid or oversized Ollama model catalog.", "Keep the local model catalog within the supported limit of 256 entries.")
        names, blocked = set(), 0
        for item in models:
            if not isinstance(item, dict) or not valid_model_name(item.get("name")):
                raise OllamaError("invalid_catalog", "Ollama returned malformed model metadata.", "Refresh the catalog after checking the daemon.")
            name = item["name"]
            if "cloud" in name.lower() or remote_metadata(item):
                blocked += 1
                continue
            names.add(name)
        available = sorted(names)
        state = "models_detected" if available else ("no_local_models" if models else "empty")
        note = (f"{len(available)} local model candidate(s) detected; Check model validates capabilities before inference. "
                if available else "No eligible local models detected. No automatic model download will occur. ")
        return {"provider": "ollama", "endpoint": self.endpoint, "available": True,
                "state": state, "models": available, "blocked_models": blocked,
                "cloud_configuration": "not_attested", "note": note + CLOUD_NOTE}

    def diagnostics(self) -> dict[str, Any]:
        try:
            return self.catalog()
        except OllamaError as exc:
            return {"available": False, "state": exc.code, "models": [],
                    "endpoint": self.endpoint, "cloud_configuration": "not_attested",
                    "note": str(exc) + " " + exc.next_step, **exc.public()}

    def local_models(self) -> list[str]:
        return self.catalog()["models"]

    def ensure_local(self) -> None:
        if not self.model or self.model not in self.local_models():
            raise OllamaError("model_not_installed", "Select an exact installed local model name.", "Refresh Detect. Automatic pulls and model substitution are disabled.")

    def inspect_model(self, *, require_tools: bool = False) -> dict[str, Any]:
        if not isinstance(require_tools, bool):
            raise ValueError("require_tools must be boolean")
        self.ensure_local()
        value = self.request("/api/show", {"model": self.model})
        if remote_metadata(value):
            raise OllamaError("cloud_model_blocked", "The selected alias resolves to a remote model.", "Choose a local model and disable Ollama cloud features.")
        capabilities = value.get("capabilities")
        if (not isinstance(capabilities, list) or len(capabilities) > 32
                or any(not isinstance(c, str) or len(c) > 80 for c in capabilities)):
            raise OllamaError("capabilities_unknown", "Ollama did not report model capabilities.", "Use a daemon/model version that reports completion and tool capabilities.")
        if "completion" not in capabilities:
            raise OllamaError("completion_unsupported", "This model cannot provide chat analysis.", "Choose a completion-capable local model, not an embedding-only model.")
        if require_tools and "tools" not in capabilities:
            raise OllamaError("tools_unsupported", "This model does not report tool-calling support.", "Use Analyst mode or select a tool-capable local model. No automatic substitution.")
        details = value.get("details", {})
        if not isinstance(details, dict):
            raise OllamaError("invalid_response", "Invalid model details.", "Check the local Ollama daemon.")
        return {"provider": "ollama", "model": self.model, "endpoint": self.endpoint,
                "state": "metadata_checked", "capabilities": sorted(set(capabilities)),
                "tool_calling": "tools" in capabilities,
                "parameter_size": str(details.get("parameter_size", "unknown"))[:80],
                "quantization": str(details.get("quantization_level", "unknown"))[:80],
                "cloud_configuration": "not_attested", "inference_tested": False,
                "note": "Metadata checked; this does not test inference quality or GPU capacity. " + CLOUD_NOTE}

    def chat(self, messages: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
        if set(extra) - {"tools", "format"}:
            raise OllamaError("override_blocked", "AI request configuration override denied.", "Model, endpoint, budgets and sampling are controlled by the runtime.")
        if not isinstance(messages, list) or not 1 <= len(messages) <= 16:
            raise ValueError("Invalid message count")
        for message in messages:
            if (not isinstance(message, dict) or set(message) - {"role", "content", "tool_calls", "tool_name"}
                    or message.get("role") not in {"system", "user", "assistant", "tool"}
                    or not isinstance(message.get("content"), str)):
                raise ValueError("Invalid chat message")
        tools = extra.get("tools", [])
        if not isinstance(tools, list) or len(tools) > 1:
            raise ValueError("At most one allowlisted tool is supported")
        # Never send assessment context until installed-model and remote-alias checks pass.
        # Recheck every inference: catalog/model metadata may change during a session.
        self.inspect_model(require_tools=bool(tools))
        data = {"model": self.model, "stream": False, "messages": messages,
                "options": {"temperature": 0, "num_predict": 768, "num_ctx": 4096},
                "keep_alive": "2m", **extra}
        response = self.request("/api/chat", data)
        if remote_metadata(response):
            raise OllamaError("remote_execution_reported", "Ollama reported remote inference; output rejected.", "Stop using this daemon and verify its cloud/egress policy. Rejection cannot undo an already-sent prompt.")
        if response.get("done") is not True:
            raise OllamaError("incomplete_response", "Ollama did not finish its response.", "Retry explicitly after checking local capacity.", retryable=True)
        if response.get("done_reason") == "length":
            raise OllamaError("output_truncated", "Ollama reached the output budget.", "Reduce context or select a more suitable local model.")
        message = response.get("message")
        if (not isinstance(message, dict) or message.get("role", "assistant") != "assistant"
                or not isinstance(message.get("content", ""), str)):
            raise OllamaError("invalid_response", "Invalid assistant message.", "Check model compatibility.")
        # Do not retain thinking traces, images or arbitrary daemon metadata.
        result = {"role": "assistant", "content": message.get("content", "")}
        if "tool_calls" in message:
            calls = message["tool_calls"]
            if not isinstance(calls, list) or len(calls) > 1 or any(not isinstance(c, dict) or not isinstance(c.get("function"), dict) for c in calls):
                raise OllamaError("invalid_tool_call", "Malformed tool request rejected.", "Use a model compatible with the declared tool schema.")
            result["tool_calls"] = calls
        return result
