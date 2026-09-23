import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from workbench.server import State
from workbench.workspace_server import WorkbenchServer


class AdapterApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = State(Path(self.tmp.name) / "state")
        self.token = "adapter-api-test-token"
        self.server = WorkbenchServer(("127.0.0.1", 0), self.state, self.token)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.tmp.cleanup()

    def call(self, method, path, body=None, *, authorized=True):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": f"127.0.0.1:{self.port}"}
        if authorized:
            headers["Authorization"] = "Bearer " + self.token
        raw = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            raw = json.dumps(body)
        connection.request(method, path, body=raw, headers=headers)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, json.loads(data) if data else None

    def test_registry_route_requires_session_token(self):
        status, _ = self.call("GET", "/api/adapters", authorized=False)
        self.assertEqual(status, 401)
        status, payload = self.call("GET", "/api/adapters")
        self.assertEqual(status, 200)
        ids = {item["adapter"]["id"] for item in payload["adapters"]}
        self.assertEqual(
            ids,
            {"native-project-metadata", "native-web-headers", "semgrep-project-local"},
        )

    def test_project_plan_approve_execute_persists_minimized_receipt(self):
        project = Path(self.tmp.name) / "private-customer-root"
        project.mkdir()
        (project / ".env").write_text(
            "DO_NOT_STORE=customer-secret-value", encoding="utf-8"
        )
        request = {
            "root": str(project),
            "asset_key": "asset-1",
            "max_files": 20,
            "max_depth": 4,
            "timeout_seconds": 5,
        }
        status, planned = self.call(
            "POST",
            "/api/adapters/plan",
            {
                "adapter_id": "native-project-metadata",
                "request": request,
            },
        )
        self.assertEqual(status, 201)
        self.assertEqual(planned["status"], "planned")
        self.assertEqual(
            planned["request_summary"]["project_label"], "private-customer-root"
        )
        self.assertFalse(planned["request_summary"]["full_path_included"])
        self.assertNotIn("request_sha256", planned)

        status, approved = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/approve",
            {
                "plan_sha256": planned["plan_sha256"],
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(approved["status"], "approved")

        status, completed = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/execute",
            {
                "adapter_id": "native-project-metadata",
                "request": request,
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(
            completed["receipt"]["result"]["verification_authority"], "workbench_only"
        )
        self.assertTrue(
            all(
                finding["verification"] == "candidate"
                for finding in completed["receipt"]["result"]["findings"]
            )
        )

        status, stored = self.call("GET", f"/api/adapter-runs/{planned['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(stored["status"], "completed")
        database = self.state.store.path.read_bytes()
        self.assertNotIn(str(project).encode(), database)
        self.assertNotIn(b"customer-secret-value", database)

    def test_completed_receipt_becomes_idempotent_candidate_only_report(self):
        project = Path(self.tmp.name) / "project-report"
        project.mkdir()
        (project / ".env").write_text(
            "SECRET_VALUE_SHOULD_NOT_BE_READ", encoding="utf-8"
        )
        request = {
            "root": str(project),
            "asset_key": "asset-report",
            "max_files": 20,
            "max_depth": 4,
            "timeout_seconds": 5,
        }
        status, planned = self.call(
            "POST",
            "/api/adapters/plan",
            {"adapter_id": "native-project-metadata", "request": request},
        )
        self.assertEqual(status, 201)
        status, _ = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/approve",
            {"plan_sha256": planned["plan_sha256"]},
        )
        self.assertEqual(status, 200)
        status, completed = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/execute",
            {"adapter_id": "native-project-metadata", "request": request},
        )
        self.assertEqual(status, 200)
        self.assertEqual(completed["status"], "completed")

        status, linked = self.call(
            "POST", f"/api/adapter-runs/{planned['id']}/report", {}
        )
        self.assertEqual(status, 201)
        self.assertTrue(linked["created"])
        status, report = self.call("GET", f"/api/runs/{linked['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(report["environment"], "reviewed_adapter_receipt")
        self.assertEqual(report["provenance"]["lifecycle_id"], planned["id"])
        self.assertEqual(report["checks"][0]["plan_sha256"], planned["plan_sha256"])
        self.assertTrue(report["findings"])
        self.assertTrue(
            all(item["verification"] == "candidate" for item in report["findings"])
        )
        self.assertEqual(report["ai"]["status"], "not_requested")
        self.assertNotIn(str(project), json.dumps(report))
        self.assertNotIn("SECRET_VALUE_SHOULD_NOT_BE_READ", json.dumps(report))

        status, linked_again = self.call(
            "POST", f"/api/adapter-runs/{planned['id']}/report", {}
        )
        self.assertEqual(status, 200)
        self.assertFalse(linked_again["created"])
        self.assertEqual(linked_again["id"], linked["id"])

    def test_report_bridge_rejects_noncompleted_lifecycle(self):
        project = Path(self.tmp.name) / "project-planned"
        project.mkdir()
        request = {
            "root": str(project),
            "asset_key": "asset-planned",
            "max_files": 10,
            "max_depth": 3,
            "timeout_seconds": 5,
        }
        status, planned = self.call(
            "POST",
            "/api/adapters/plan",
            {"adapter_id": "native-project-metadata", "request": request},
        )
        self.assertEqual(status, 201)
        status, payload = self.call(
            "POST", f"/api/adapter-runs/{planned['id']}/report", {}
        )
        self.assertEqual(status, 400)
        self.assertIn("completed", payload["error"])

    def test_changed_request_is_rejected_after_approval(self):
        project = Path(self.tmp.name) / "project-a"
        project.mkdir()
        request = {
            "root": str(project),
            "asset_key": "asset-2",
            "max_files": 10,
            "max_depth": 3,
            "timeout_seconds": 5,
        }
        status, planned = self.call(
            "POST",
            "/api/adapters/plan",
            {"adapter_id": "native-project-metadata", "request": request},
        )
        self.assertEqual(status, 201)
        status, _ = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/approve",
            {"plan_sha256": planned["plan_sha256"]},
        )
        self.assertEqual(status, 200)
        changed = dict(request)
        changed["max_files"] = 11
        status, payload = self.call(
            "POST",
            f"/api/adapter-runs/{planned['id']}/execute",
            {
                "adapter_id": "native-project-metadata",
                "request": changed,
            },
        )
        self.assertEqual(status, 400)
        self.assertIn("changed after approval", payload["error"])
        status, stored = self.call("GET", f"/api/adapter-runs/{planned['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(stored["status"], "approved")

    def test_closed_body_contract_rejects_extra_execution_fields(self):
        status, payload = self.call(
            "POST",
            "/api/adapters/plan",
            {
                "adapter_id": "native-project-metadata",
                "request": {},
                "command": "ignored",
            },
        )
        self.assertEqual(status, 400)
        self.assertIn("exactly", payload["error"])


if __name__ == "__main__":
    unittest.main()
