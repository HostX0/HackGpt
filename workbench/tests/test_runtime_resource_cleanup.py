import json
import threading
import unittest
from unittest.mock import Mock, patch

from workbench.ollama import Ollama

MODEL = "local:test"


class RuntimeResourceCleanupTests(unittest.TestCase):
    def run_diagnostics(self, status, body):
        response_closed = threading.Event()
        connection_closed = threading.Event()
        response = Mock()
        response.status = status
        response.read.return_value = body
        response.close.side_effect = response_closed.set
        connection = Mock()
        connection.getresponse.return_value = response
        connection.close.side_effect = connection_closed.set

        with patch(
            "workbench.ollama_runtime.http.client.HTTPConnection",
            return_value=connection,
        ):
            result = Ollama(MODEL).diagnostics()

        self.assertTrue(response_closed.wait(1), "HTTP response was not closed")
        self.assertTrue(connection_closed.wait(1), "HTTP connection was not closed")
        response.close.assert_called_once_with()
        connection.close.assert_called_once_with()
        return result

    def test_successful_catalog_closes_response_and_connection(self):
        result = self.run_diagnostics(200, json.dumps({"models": []}).encode())
        self.assertTrue(result["available"])
        self.assertEqual(result["state"], "empty")

    def test_rejected_http_status_closes_response_and_connection(self):
        result = self.run_diagnostics(
            503, json.dumps({"error": "synthetic unavailable"}).encode()
        )
        self.assertFalse(result["available"])
        self.assertEqual(result["state"], "busy")
        self.assertTrue(result["retryable"])

    def test_response_close_error_still_closes_connection_and_preserves_status(self):
        connection_closed = threading.Event()
        response = Mock()
        response.status = 503
        response.close.side_effect = OSError("synthetic close failure")
        connection = Mock()
        connection.getresponse.return_value = response
        connection.close.side_effect = connection_closed.set

        with patch(
            "workbench.ollama_runtime.http.client.HTTPConnection",
            return_value=connection,
        ):
            result = Ollama(MODEL).diagnostics()

        self.assertTrue(connection_closed.wait(1), "HTTP connection was not closed")
        response.close.assert_called_once_with()
        connection.close.assert_called_once_with()
        self.assertEqual(result["state"], "busy")


if __name__ == "__main__":
    unittest.main()
