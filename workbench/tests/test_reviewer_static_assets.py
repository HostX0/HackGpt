"""Real loopback delivery checks for the reviewer evidence UI assets."""

import http.client
import tempfile
import threading
import unittest

from workbench.server import State
from workbench.workspace_server import WorkbenchServer


class ReviewerStaticAssetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.state = State(self.directory.name)
        self.server = WorkbenchServer(
            ("127.0.0.1", 0), self.state, "reviewer-static-test-token"
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.state.cancel.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.directory.cleanup()

    def get(self, path):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=3
        )
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_reviewer_assets_are_served_by_the_real_workspace_entrypoint(self):
        expected = {
            "/reviewer.js": ("text/javascript; charset=utf-8", b"Reviewer evidence"),
            "/reviewer.css": ("text/css; charset=utf-8", b".reviewer-evidence"),
        }
        for path, (content_type, marker) in expected.items():
            with self.subTest(path=path):
                status, headers, body = self.get(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], content_type)
                self.assertEqual(headers["Cache-Control"], "no-store")
                self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
                self.assertIn(marker, body)
                self.assertNotIn(b"reviewer-static-test-token", body)

    def test_existing_adapter_asset_route_remains_compatible(self):
        status, headers, body = self.get("/adapter.js")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/javascript; charset=utf-8")
        self.assertTrue(body)

    def test_unreviewed_static_path_is_not_exposed(self):
        self.assertEqual(self.get("/reviewer.map")[0], 404)


if __name__ == "__main__":
    unittest.main()
