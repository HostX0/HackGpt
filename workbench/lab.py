"""Ephemeral loopback-only authorization fixture. Never a remote exploitation target."""
import hashlib
import http.client
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class CanaryLab:
    def __init__(self, fixed=False):
        self.fixed = fixed
        self.marker = ("HACKGPT-SYNTHETIC-" + secrets.token_hex(24)).encode()
        lab = self

        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):
                if self.path == "/control" or (lab.fixed and self.path == "/record"):
                    status, body = 401, b"Authorization required"
                elif self.path == "/record":
                    status, body = 200, lab.marker
                else:
                    status, body = 404, b"Not found"
                self.send_response(status)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, path, method="GET"):
        if path not in ("/", "/control", "/record"):
            raise ValueError("Unknown synthetic lab action")
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            conn.request(method, path, headers={"Connection": "close"})
            response = conn.getresponse()
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), response.read(4096)
        finally:
            conn.close()

    def prove(self):
        control, _, _ = self.request("/control")
        status, _, body = self.request("/record")
        return {
            "control_status": control,
            "record_status": status,
            "synthetic_marker_matched": status == 200 and secrets.compare_digest(body, self.marker),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "expected_sha256": hashlib.sha256(self.marker).hexdigest(),
            "credentials_sent": False,
            "paths": ["/control", "/record"],
            "environment": "ephemeral synthetic loopback lab",
        }
