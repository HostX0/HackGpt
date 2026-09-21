"""Loopback API tests for the assessment-data-free Ollama compatibility probe."""
import http.client
import json
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from workbench.ollama_runtime import OllamaError
from workbench.server import LocalServer, State


class SelfTestApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.state = State(self.directory.name)
        self.server = LocalServer(("127.0.0.1", 0), self.state, "self-test-token")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.state.cancel.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.directory.cleanup()

    def call(self, body, *, auth=True):
        headers = {"Content-Type": "application/json"}
        if auth:
            headers["Authorization"] = "Bearer self-test-token"
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            conn.request("POST", "/api/models/self-test", body=json.dumps(body), headers=headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    @patch("workbench.server.Ollama")
    def test_self_test_is_authenticated_and_forwards_only_fixed_options(self, ollama_class):
        client = Mock()
        client.self_test.return_value = {
            "provider": "ollama",
            "model": "local:test",
            "state": "inference_compatible",
            "assessment_data_sent": False,
        }
        ollama_class.return_value = client

        status, value = self.call({"model": "local:test", "require_tools": True})
        self.assertEqual(status, 200)
        self.assertEqual(value["state"], "inference_compatible")
        self.assertFalse(value["assessment_data_sent"])
        ollama_class.assert_called_once_with("local:test")
        client.self_test.assert_called_once_with(require_tools=True)
        self.assertIsNone(self.state.active)

        unauthenticated, _ = self.call({"model": "local:test"}, auth=False)
        self.assertEqual(unauthenticated, 401)

    @patch("workbench.server.Ollama")
    def test_extra_fields_are_rejected_before_model_access(self, ollama_class):
        status, _ = self.call({"model": "local:test", "require_tools": False, "target": "https://example.com"})
        self.assertEqual(status, 400)
        ollama_class.assert_not_called()

    @patch("workbench.server.Ollama")
    def test_require_tools_is_strict_boolean(self, ollama_class):
        status, _ = self.call({"model": "local:test", "require_tools": "yes"})
        self.assertEqual(status, 400)
        ollama_class.assert_not_called()

    @patch("workbench.server.Ollama")
    def test_ollama_failure_returns_stable_safe_error(self, ollama_class):
        client = Mock()
        client.self_test.side_effect = OllamaError(
            "self_test_failed",
            "The selected local model did not satisfy the workbench inference contract.",
            "Choose a compatible local model.",
        )
        ollama_class.return_value = client
        status, value = self.call({"model": "local:test"})
        self.assertEqual(status, 422)
        self.assertEqual(value["code"], "self_test_failed")
        self.assertEqual(value["provider"], "ollama")
        self.assertNotIn("prompt", json.dumps(value).lower())


if __name__ == "__main__":
    unittest.main()
