"""Regression tests for the test-only live-model loopback relay."""

from __future__ import annotations

import json
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from workbench.tests.live_ollama_validation import _LoopbackRelay


class _CatalogHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - stdlib handler contract
        if self.path != "/api/tags":
            self.send_error(404)
            return
        body = json.dumps(
            {"models": [{"name": "fixture", "digest": "sha256:" + "a" * 64}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A002 - stdlib handler contract
        return


class LiveModelRelayTests(unittest.TestCase):
    def test_relay_rejects_public_or_unspecified_destinations(self):
        for value in ("8.8.8.8", "0.0.0.0", "not-an-ip", "2001:db8::1"):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    _LoopbackRelay(value)

    def test_relay_forwards_only_to_fixed_private_destination(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _CatalogHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with _LoopbackRelay("127.0.0.1", server.server_port) as relay_port:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{relay_port}/api/tags", timeout=3
                ) as response:
                    value = json.load(response)
            self.assertEqual(value["models"][0]["name"], "fixture")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
