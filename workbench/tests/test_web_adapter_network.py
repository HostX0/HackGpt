import http.server
import socket
import threading
import unittest
from unittest import mock

from workbench.web_adapter import WebHeaderAdapter

_REAL_CREATE_CONNECTION = socket.create_connection


class _HeadFixture(http.server.BaseHTTPRequestHandler):
    response_headers = {}
    status = 200
    requests = []

    def do_HEAD(self):
        type(self).requests.append((self.command, self.path))
        self.send_response(type(self).status)
        for name, value in type(self).response_headers.items():
            self.send_header(name, value)
        self.end_headers()

    def do_GET(self):
        type(self).requests.append((self.command, self.path))
        self.send_response(405)
        self.end_headers()

    def log_message(self, *_args):
        pass


class WebAdapterOwnedNetworkFixtureTests(unittest.TestCase):
    def setUp(self):
        _HeadFixture.requests = []
        _HeadFixture.status = 200
        _HeadFixture.response_headers = {"Content-Type": "text/html"}
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _HeadFixture)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def _run(self):
        port = self.server.server_address[1]

        def owned_connect(_address, timeout=None, **_kwargs):
            return _REAL_CREATE_CONNECTION(("127.0.0.1", port), timeout=timeout)

        # The adapter is given an ordinary public URL so its normal URL contract remains
        # unchanged. Only the test's resolution/connect boundary is redirected to this
        # owned ephemeral fixture; the actual inspect_remote HTTP code path still runs.
        with mock.patch("workbench.engine.public_addresses", return_value=["93.184.216.34"]), \
             mock.patch("workbench.engine.socket.create_connection", side_effect=owned_connect):
            return WebHeaderAdapter().run("http://example.com", asset_key="owned-network-fixture")

    def test_production_reader_path_uses_head_and_yields_candidates(self):
        result = self._run()
        self.assertEqual(_HeadFixture.requests, [("HEAD", "/")])
        self.assertEqual(result["status"], "completed")
        self.assertEqual({item["rule"] for item in result["findings"]}, {
            "web/missing-content-security-policy", "web/missing-content-type-options",
        })
        self.assertTrue(all(item["verification"] == "candidate" for item in result["findings"]))
        self.assertNotIn("resolved_ip", repr(result))

    def test_production_reader_path_fixed_fixture_has_no_findings(self):
        _HeadFixture.response_headers = {
            "Content-Type": "text/html",
            "Content-Security-Policy": "default-src 'self'",
            "X-Content-Type-Options": "nosniff",
        }
        result = self._run()
        self.assertEqual(_HeadFixture.requests, [("HEAD", "/")])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["coverage"]["objects_tested"], 1)

    def test_response_body_is_never_requested_from_owned_fixture(self):
        self._run()
        self.assertFalse(any(method == "GET" for method, _ in _HeadFixture.requests))


if __name__ == "__main__":
    unittest.main()
