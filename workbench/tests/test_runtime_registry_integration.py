import http.server
import socket
import socketserver
import threading
import time
import unittest
from unittest import mock

from workbench.engine import Assessment, Cancelled, Deadline, DeadlineExceeded, Scope
from workbench.network_transport import inspect_remote
from workbench.ollama_runtime import LocalRuntime, OllamaError
from workbench.retest import compare_reports
from workbench.web_adapter import WebHeaderAdapter

_REAL_CREATE_CONNECTION = socket.create_connection


def external_scope():
    return Scope.parse({
        "target": "https://example.com",
        "mode": "analyst",
        "authorized": True,
        "authorization": "registry lifecycle fixture",
    })


class _HeadFixture(http.server.BaseHTTPRequestHandler):
    delay = 0.0
    requests = []

    def do_HEAD(self):
        type(self).requests.append((self.command, self.path))
        if type(self).delay:
            time.sleep(type(self).delay)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

    def log_message(self, *_args):
        pass


class _SilentTLSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        time.sleep(0.8)


class _SlowOllama(http.server.BaseHTTPRequestHandler):
    calls = 0

    def do_GET(self):
        type(self).calls += 1
        time.sleep(0.8)
        raw = b'{"models": []}'
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *_args):
        pass


class RuntimeAndRegistryIntegrationTests(unittest.TestCase):
    def test_external_baseline_uses_registry_adapter_contract(self):
        report = Assessment(
            external_scope(),
            remote_reader=lambda _: {"status": 200, "headers": {"content-type": "text/html"}},
        ).run()
        checks = [check for check in report["checks"] if check.get("tool") == "native-web-headers"]
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["status"], "completed")
        self.assertEqual(checks[0]["adapter"]["version"], "1")
        self.assertTrue(report["findings"])
        self.assertTrue(all(item["verification"] == "candidate" for item in report["findings"]))
        self.assertTrue(all(item["rule"].startswith("web/") for item in report["findings"]))

    def test_registry_web_rule_maps_to_comparable_retest_coverage(self):
        prior = {
            "id": "before", "target": "https://example.com", "environment": "authorized_public_web",
            "status": "completed", "checks": [],
            "findings": [{
                "fingerprint": "f" * 64,
                "rule": "web/missing-content-security-policy",
                "title": "CSP missing",
                "remediation": "Add a scoped CSP",
                "evidence_sha256": "e" * 64,
                "id": "old",
            }],
        }
        current = {
            "id": "after", "target": "https://example.com", "environment": "authorized_public_web",
            "status": "completed", "findings": [],
            "checks": [{"tool": "native-web-headers", "status": "completed"}],
        }
        diff = compare_reports(prior, current)
        self.assertEqual(diff["counts"]["not_reproduced"], 1)
        self.assertEqual(diff["items"][0]["recheck"]["coverage"]["tool"], "native-web-headers")

    def test_partial_registry_result_keeps_assessment_inconclusive(self):
        report = Assessment(
            external_scope(),
            remote_reader=lambda _: {"status": 302, "headers": {}},
        ).run()
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["verdict"], "inconclusive")
        check = next(item for item in report["checks"] if item["tool"] == "native-web-headers")
        self.assertEqual(check["status"], "inconclusive")

    def test_cancel_interrupts_tls_handshake_after_connection(self):
        cancel = threading.Event()
        closed = threading.Event()
        sock = mock.Mock()
        sock.close.side_effect = closed.set
        context = mock.Mock()

        def blocked_handshake(_sock, server_hostname=None):
            if not closed.wait(0.6):
                self.fail("cancellation watcher did not close the TLS socket")
            raise OSError("closed by cancellation")

        context.wrap_socket.side_effect = blocked_handshake
        timer = threading.Timer(0.05, cancel.set)
        timer.start()
        started = time.monotonic()
        try:
            with mock.patch("workbench.engine.public_addresses", return_value=["8.8.8.8"]), \
                 mock.patch("workbench.network_transport._connect_bounded", return_value=sock), \
                 mock.patch("workbench.engine.ssl.create_default_context", return_value=context):
                with self.assertRaises(Cancelled):
                    inspect_remote("https://example.com", Deadline(2), cancel)
        finally:
            timer.cancel()
        self.assertLess(time.monotonic() - started, 0.6)

    def test_cancel_interrupts_slow_http_response(self):
        _HeadFixture.delay = 0.8
        _HeadFixture.requests = []
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _HeadFixture)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        cancel = threading.Event()
        timer = threading.Timer(0.05, cancel.set)
        port = server.server_address[1]

        def owned_connect(_address, _port, deadline, _cancel=None):
            return _REAL_CREATE_CONNECTION(("127.0.0.1", port), timeout=deadline.remaining(2))

        started = time.monotonic()
        timer.start()
        try:
            with mock.patch("workbench.engine.public_addresses", return_value=["93.184.216.34"]), \
                 mock.patch("workbench.network_transport._connect_bounded", side_effect=owned_connect):
                with self.assertRaises(Cancelled):
                    WebHeaderAdapter().run("http://example.com", asset_key="cancel-fixture", cancel=cancel)
        finally:
            timer.cancel()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            _HeadFixture.delay = 0.0
        self.assertLess(time.monotonic() - started, 0.7)
        self.assertEqual(_HeadFixture.requests, [("HEAD", "/")])

    def test_shared_deadline_interrupts_slow_http_response(self):
        _HeadFixture.delay = 0.8
        _HeadFixture.requests = []
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _HeadFixture)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]

        def owned_connect(_address, _port, deadline, _cancel=None):
            return _REAL_CREATE_CONNECTION(("127.0.0.1", port), timeout=deadline.remaining(2))

        started = time.monotonic()
        try:
            with mock.patch("workbench.engine.public_addresses", return_value=["93.184.216.34"]), \
                 mock.patch("workbench.network_transport._connect_bounded", side_effect=owned_connect):
                with self.assertRaises(DeadlineExceeded):
                    inspect_remote("http://example.com", Deadline(0.08))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            _HeadFixture.delay = 0.0
        self.assertLess(time.monotonic() - started, 0.7)

    def test_shared_deadline_interrupts_silent_tls_handshake(self):
        server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), _SilentTLSHandler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]

        def owned_connect(_address, _port, deadline, _cancel=None):
            return _REAL_CREATE_CONNECTION(("127.0.0.1", port), timeout=deadline.remaining(2))

        started = time.monotonic()
        try:
            with mock.patch("workbench.engine.public_addresses", return_value=["93.184.216.34"]), \
                 mock.patch("workbench.network_transport._connect_bounded", side_effect=owned_connect):
                with self.assertRaises(DeadlineExceeded):
                    inspect_remote("https://example.com", Deadline(0.08))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertLess(time.monotonic() - started, 0.7)

    def test_attached_cancel_interrupts_slow_model_transport(self):
        _SlowOllama.calls = 0
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _SlowOllama)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        cancel = threading.Event()
        runtime = LocalRuntime(port=server.server_address[1])
        runtime.set_cancel(cancel)
        timer = threading.Timer(0.05, cancel.set)
        timer.start()
        started = time.monotonic()
        try:
            with self.assertRaises(OllamaError) as captured:
                runtime.request("/api/tags")
        finally:
            timer.cancel()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertEqual(captured.exception.code, "cancelled")
        self.assertLess(time.monotonic() - started, 0.7)
        self.assertIn("discards its result", captured.exception.next_step)
        self.assertTrue(runtime.telemetry()["cancellation_attached"])

    def test_shared_deadline_interrupts_slow_model_transport(self):
        _SlowOllama.calls = 0
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _SlowOllama)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        runtime = LocalRuntime(port=server.server_address[1])
        runtime.set_deadline(time.monotonic() + 0.08)
        started = time.monotonic()
        try:
            with self.assertRaises(OllamaError) as captured:
                runtime.request("/api/tags")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertEqual(captured.exception.code, "deadline_exceeded")
        self.assertLess(time.monotonic() - started, 0.7)

    def test_pre_cancelled_model_request_fails_before_network(self):
        cancel = threading.Event()
        cancel.set()
        runtime = LocalRuntime("local:test", port=65534)
        runtime.set_cancel(cancel)
        with self.assertRaises(OllamaError) as captured:
            runtime.request("/api/tags")
        self.assertEqual(captured.exception.code, "cancelled")
        self.assertIn("No model request was sent", captured.exception.next_step)


if __name__ == "__main__":
    unittest.main()
