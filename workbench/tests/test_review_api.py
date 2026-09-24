"""Integration tests for reviewer-facing retest and evidence bundle endpoints."""

import http.client
import io
import json
import tempfile
import threading
import unittest
import zipfile

from workbench.engine import Assessment, Scope
from workbench.server import LocalServer, State

BASE = {
    "target": "https://example.com",
    "mode": "analyst",
    "authorized": True,
    "authorization": "Reviewer API fixture",
    "approve_verification": False,
}


class ReviewApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.state = State(self.directory.name)
        self.server = LocalServer(("127.0.0.1", 0), self.state, "review-token")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.state.cancel.set()
        if self.state.worker:
            self.state.worker.join(timeout=5)
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.directory.cleanup()

    def call(self, path):
        conn = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=3
        )
        try:
            conn.request("GET", path, headers={"Authorization": "Bearer review-token"})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def make_report(self, headers):
        scope = Scope.parse(BASE)
        report = Assessment(
            scope,
            remote_reader=lambda _: {
                "status": 200,
                "headers": {"content-type": "text/html", **headers},
                "method": "HEAD",
                "redirect_followed": False,
                "resolved_ip": "203.0.113.10",
            },
        ).run()
        self.state.store.save(report)
        return report

    def test_bundle_endpoint_contains_manifest(self):
        report = self.make_report({})
        status, headers, raw = self.call(f"/api/runs/{report['id']}/export.bundle.zip")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["run_id"], report["id"])
            self.assertFalse(manifest["signed"])
            self.assertIn("report.json", archive.namelist())
            self.assertIn("report.md", archive.namelist())

    def test_compare_endpoint_does_not_claim_fixed(self):
        previous = self.make_report({})
        current = self.make_report(
            {
                "content-security-policy": "default-src 'self'",
                "x-content-type-options": "nosniff",
            }
        )
        status, _, raw = self.call(
            f"/api/runs/{previous['id']}/compare/{current['id']}"
        )
        self.assertEqual(status, 200)
        diff = json.loads(raw)
        self.assertEqual(diff["counts"]["not_reproduced"], 2)
        self.assertNotIn("fixed", {item["state"] for item in diff["items"]})

    def test_compare_unknown_run_returns_404(self):
        current = self.make_report({})
        status, _, _ = self.call(f"/api/runs/{'a' * 32}/compare/{current['id']}")
        self.assertEqual(status, 404)

    def test_compare_endpoint_rejects_self_comparison(self):
        current = self.make_report({})
        status, _, raw = self.call(
            f"/api/runs/{current['id']}/compare/{current['id']}"
        )
        self.assertEqual(status, 409)
        error = json.loads(raw)
        self.assertIn("distinct assessment runs", error["error"])


if __name__ == "__main__":
    unittest.main()
