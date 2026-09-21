"""Local API security and persistence integration tests, with disposable data."""
import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from workbench.engine import Assessment, Scope, verify_integrity
from workbench.server import Busy, LocalServer, State, Store

INPUT = {'target': 'lab', 'mode': 'verify', 'authorized': True, 'authorization': 'Local integration test', 'approve_verification': True}


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.state = State(self.directory.name)
        self.server = LocalServer(('127.0.0.1', 0), self.state, 'test-session-token')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.state.cancel.set()
        if self.state.worker:
            self.state.worker.join(timeout=5)
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=2)
        self.directory.cleanup()

    def call(self, path, body=None, auth=True, extra=None):
        headers = {'Authorization': 'Bearer test-session-token'} if auth else {}
        if body is not None: headers['Content-Type'] = 'application/json'
        headers.update(extra or {})
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            conn.request('GET' if body is None else 'POST', path, body=json.dumps(body) if body is not None else None, headers=headers)
            result = conn.getresponse()
            return result.status, dict(result.getheaders()), result.read()
        finally:
            conn.close()

    def test_api_requires_token(self):
        self.assertEqual(self.call('/api/health', auth=False)[0], 401)

    def test_wrong_token_rejected(self):
        self.assertEqual(self.call('/api/health', extra={'Authorization': 'Bearer wrong'})[0], 401)

    def test_host_rebinding_rejected(self):
        self.assertEqual(self.call('/api/health', extra={'Host': 'attacker.example'})[0], 403)

    def test_cross_origin_rejected(self):
        self.assertEqual(self.call('/api/health', extra={'Origin': 'https://elsewhere.example'})[0], 403)

    def test_null_origin_rejected(self):
        self.assertEqual(self.call('/api/health', extra={'Origin': 'null'})[0], 403)

    def test_same_origin_accepted(self):
        origin = 'http://127.0.0.1:' + str(self.server.server_port)
        self.assertEqual(self.call('/api/health', extra={'Origin': origin})[0], 200)

    def test_headers_no_store_and_csp(self):
        status, headers, _ = self.call('/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertNotIn('Access-Control-Allow-Origin', headers)

    def test_health_discloses_missing_adapters(self):
        result = json.loads(self.call('/api/health')[2])
        self.assertEqual(result['third_party_adapters'], 'not_integrated')

    def test_invalid_scope_rejected(self):
        self.assertEqual(self.call('/api/runs', {'target': 'lab'})[0], 400)

    def test_nonobject_json_rejected(self):
        self.assertEqual(self.call('/api/runs', [INPUT])[0], 400)

    def test_content_type_rejected(self):
        self.assertEqual(self.call('/api/runs', INPUT, extra={'Content-Type': 'text/plain'})[0], 400)

    def test_oversized_body_rejected_before_read(self):
        self.assertEqual(self.call('/api/runs', INPUT, extra={'Content-Length': '20000'})[0], 400)

    def test_encoding_rejected(self):
        self.assertEqual(self.call('/api/runs', INPUT, extra={'Content-Encoding': 'gzip'})[0], 400)

    def test_sensitive_files_not_served(self):
        for path in ('/.env', '/../../LICENSE', '/reports.sqlite3', '/api/runs/../'):
            with self.subTest(path=path):
                self.assertEqual(self.call(path)[0], 404)

    def test_static_ui_has_no_session_secret(self):
        status, _, body = self.call('/', auth=False)
        self.assertEqual(status, 200)
        self.assertIn(b'Evidence Workbench', body)
        self.assertNotIn(b'test-session-token', body)

    def test_unknown_run(self):
        self.assertEqual(self.call('/api/runs/' + 'a' * 32)[0], 404)

    def test_single_worker_limit(self):
        self.state.active = 'busy'
        self.assertEqual(self.call('/api/runs', INPUT)[0], 409)
        self.state.active = None

    def test_cancel_inactive_run(self):
        self.assertEqual(self.call('/api/runs/' + 'a' * 32 + '/cancel', {})[0], 409)

    def test_assessment_lifecycle_history_and_exports(self):
        status, _, raw = self.call('/api/runs', INPUT)
        self.assertEqual(status, 202)
        run_id = json.loads(raw)['id']
        self.state.worker.join(timeout=5)
        self.assertFalse(self.state.worker.is_alive())
        status, _, raw = self.call('/api/runs/' + run_id)
        report = json.loads(raw)
        self.assertEqual(status, 200)
        self.assertEqual(report['verdict'], 'verified_in_synthetic_lab_only')
        self.assertTrue(verify_integrity(report))
        history = json.loads(self.call('/api/runs')[2])['runs']
        self.assertEqual(history[0]['id'], run_id)
        status, headers, exported = self.call('/api/runs/' + run_id + '/export.json')
        self.assertEqual(status, 200)
        self.assertTrue(verify_integrity(json.loads(exported)))
        self.assertIn('attachment', headers['Content-Disposition'])
        self.assertIn(b'Coverage and execution', self.call('/api/runs/' + run_id + '/export.md')[2])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = Store(self.directory.name)
        scope = Scope.parse({**INPUT, 'mode': 'analyst', 'target': 'https://example.com'})
        self.report = Assessment(scope, remote_reader=lambda _: {'status': 200, 'headers': {'content-type': 'application/json'}}).run()

    def tearDown(self):
        self.directory.cleanup()

    def test_roundtrip_and_restart(self):
        self.store.save(self.report)
        reloaded = Store(self.directory.name).get(self.report['id'])
        self.assertEqual(reloaded, self.report)

    def test_invalid_integrity_not_stored(self):
        self.report['verdict'] = 'fake'
        with self.assertRaises(ValueError):
            self.store.save(self.report)

    def test_missing_report_is_none(self):
        self.assertIsNone(self.store.get('missing'))

    def test_database_private_permissions(self):
        import os
        if os.name == 'posix':
            self.assertEqual(self.store.path.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
