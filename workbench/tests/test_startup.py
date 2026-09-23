"""Local-only startup regression fixtures; no live model or external assessment."""

import contextlib
import http.client
import io
import json
import os
from pathlib import Path
import queue
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from workbench import start
from workbench.engine import Assessment, Scope, verify_integrity
from workbench.server import Store

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "workbench" / "start.py"


def unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def command(directory, *args):
    return [sys.executable, str(ENTRY), "--data-dir", str(directory), *args]


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workbench-start-test-")
        self.directory = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def check(self, *args):
        return subprocess.run(
            command(
                self.directory,
                "--check-install",
                "--json",
                "--port",
                str(unused_port()),
                *args
            ),
            cwd=self.directory,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_check_from_another_directory_has_no_report_database(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual(document["status"], "passed")
        self.assertFalse(document["assessment_database_opened"])
        self.assertFalse(document["inference_started"])
        self.assertFalse(document["scanner_started"])
        self.assertFalse((self.directory / "reports.sqlite3").exists())
        self.assertEqual({p.name for p in self.directory.iterdir()}, {".starter.lock"})

    def test_preflight_does_not_open_even_an_invalid_existing_database(self):
        path = self.directory / "reports.sqlite3"
        path.write_bytes(b"not a database; preserve exactly")
        before = path.read_bytes()
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_preflight_never_connects_to_a_model_or_remote_host(self):
        with patch(
            "socket.socket.connect", side_effect=AssertionError("no connect allowed")
        ):
            result = start.check_local_install(self.directory, unused_port())
        self.assertEqual(result["status"], "passed")

    def test_invalid_port_fails_before_creating_workspace(self):
        missing = self.directory / "not-created"
        result = subprocess.run(
            command(missing, "--check-install", "--port", "80"),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(missing.exists())

    def test_ambiguous_cli_options_rejected(self):
        for args in (("--json",), ("--check-install", "--open-browser")):
            with self.subTest(args=args):
                result = subprocess.run(
                    command(self.directory, *args),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode, 2)

    def test_unsupported_python_has_actionable_error(self):
        with patch.object(
            start.sys, "version_info", (3, 10, 0)
        ), contextlib.redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as exit_info:
                start.main(["--check-install"])
        self.assertEqual(exit_info.exception.code, 2)
        self.assertIn("Python 3.11", error.getvalue())

    def test_busy_port_does_not_recover_existing_running_checkpoint(self):
        store = Store(self.directory)
        report = Assessment(
            Scope.parse(
                {
                    "target": "lab",
                    "mode": "analyst",
                    "authorized": True,
                    "authorization": "Owned startup fixture",
                }
            )
        ).report
        store.save_active(report)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            result = subprocess.run(
                command(self.directory, "--port", str(listener.getsockname()[1])),
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(result.returncode, 1)
        with contextlib.closing(sqlite3.connect(store.path)) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM active_runs").fetchone()[0], 1
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM reports").fetchone()[0], 0
            )
        self.assertNotIn("#token=", result.stdout + result.stderr)

    def test_storage_failure_is_nonzero_and_does_not_expose_error_text(self):
        with patch.object(
            start, "check_local_install", side_effect=OSError("sensitive-path-detail")
        ), contextlib.redirect_stdout(io.StringIO()) as output:
            status = start.main(
                ["--check-install", "--json", "--data-dir", str(self.directory)]
            )
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")
        self.assertNotIn("sensitive-path-detail", output.getvalue())
        lock = start.WorkspaceLock(self.directory)
        lock.close()

    def test_lock_excludes_second_process_and_releases_without_deleting(self):
        lock = start.WorkspaceLock(self.directory)
        try:
            result = self.check()
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["code"], "workspace_busy")
        finally:
            lock.close()
        self.assertTrue((self.directory / ".starter.lock").exists())
        self.assertEqual(self.check().returncode, 0)

    def test_separate_workspaces_do_not_block_each_other(self):
        lock = start.WorkspaceLock(self.directory)
        try:
            other = self.directory / "other"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    start.main(
                        [
                            "--check-install",
                            "--data-dir",
                            str(other),
                            "--port",
                            str(unused_port()),
                        ]
                    ),
                    0,
                )
        finally:
            lock.close()

    @unittest.skipIf(
        os.name == "nt",
        "Windows symlink creation may require developer mode or administrator privileges",
    )
    def test_symlink_lock_is_rejected_without_touching_destination(self):
        victim = self.directory / "owned-file"
        victim.write_bytes(b"unchanged")
        (self.directory / ".starter.lock").symlink_to(victim)
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(victim.read_bytes(), b"unchanged")

    def test_browser_is_explicit_and_failure_does_not_claim_e2e(self):
        with patch(
            "webbrowser.open_new_tab", return_value=False
        ) as browser, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(
                start.main(
                    [
                        "--check-install",
                        "--data-dir",
                        str(self.directory),
                        "--port",
                        str(unused_port()),
                    ]
                ),
                0,
            )
            browser.assert_not_called()
            start.open_local_browser("http://127.0.0.1:8765/#token=synthetic-test")
        self.assertIn("Browser did not open", output.getvalue())
        self.assertNotIn("synthetic-test", output.getvalue())

    def test_platform_helper_can_check_from_another_directory(self):
        args = [
            "--check-install",
            "--json",
            "--port",
            str(unused_port()),
            "--data-dir",
            str(self.directory),
        ]
        if os.name == "nt":
            call = ["cmd", "/c", str(ROOT / "workbench" / "start.cmd"), *args]
        else:
            call = ["sh", str(ROOT / "workbench" / "start.command"), *args]
        result = subprocess.run(
            call, cwd=self.directory, capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "passed")

    def test_real_launcher_owned_assessment_and_duplicate_start_preserve_history(self):
        port = unused_port()
        process = subprocess.Popen(
            command(self.directory, "--port", str(port)),
            cwd=self.directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        lines = queue.Queue()
        reader = threading.Thread(
            target=lambda: [lines.put(line) for line in process.stdout], daemon=True
        )
        reader.start()
        token = None
        try:
            # Hosted macOS arm64 can take longer than ten seconds to start a fresh
            # interpreter/server process. Keep the same real readiness assertion,
            # but allow startup latency without weakening the duplicate-start or
            # assessment/history checks that follow.
            until = time.monotonic() + 30
            while time.monotonic() < until:
                try:
                    line = lines.get(timeout=0.2)
                except queue.Empty:
                    if process.poll() is not None:
                        self.fail(
                            "launcher exited before ready: " + process.stderr.read()
                        )
                    continue
                if line.startswith("Open locally: "):
                    token = line.strip().split("#token=", 1)[1]
                    break
            self.assertIsNotNone(token, "startup exceeded test deadline")

            def call(path, body=None):
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                try:
                    headers = {"Authorization": "Bearer " + token}
                    if body is not None:
                        headers["Content-Type"] = "application/json"
                    connection.request(
                        "GET" if body is None else "POST",
                        path,
                        body=None if body is None else json.dumps(body),
                        headers=headers,
                    )
                    response = connection.getresponse()
                    return response.status, json.loads(response.read())
                finally:
                    connection.close()

            self.assertEqual(call("/api/health")[0], 200)
            status, created = call(
                "/api/runs",
                {
                    "target": "lab",
                    "mode": "verify",
                    "authorized": True,
                    "authorization": "Owned startup integration fixture",
                    "approve_verification": True,
                    "use_ai": False,
                },
            )
            self.assertEqual(status, 202)
            until = time.monotonic() + 10
            while time.monotonic() < until:
                status, report = call("/api/runs/" + created["id"])
                if report["status"] != "running":
                    break
                time.sleep(0.05)
            self.assertTrue(verify_integrity(report))
            self.assertEqual(report["durability"]["status"], "durable")
            self.assertEqual(report["verdict"], "verified_in_synthetic_lab_only")
            before = call("/api/runs")[1]
            # Inject an owned valid in-flight checkpoint after the first process
            # has started. A second State constructor would recover it incorrectly.
            active = Assessment(
                Scope.parse(
                    {
                        "target": "lab",
                        "mode": "analyst",
                        "authorized": True,
                        "authorization": "Owned in-flight fixture",
                    }
                )
            ).report
            Store(self.directory).save_active(active)
            second = subprocess.run(
                command(self.directory, "--port", str(unused_port())),
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(second.returncode, 1)
            self.assertIn("already in use", second.stderr)
            self.assertNotIn("#token=", second.stdout)
            self.assertEqual(before, call("/api/runs")[1])
            with contextlib.closing(
                sqlite3.connect(self.directory / "reports.sqlite3")
            ) as database:
                saved = database.execute(
                    "SELECT content FROM active_runs WHERE id = ?", (active["id"],)
                ).fetchone()
                self.assertIsNotNone(saved, "a denied duplicate must not run recovery")
                self.assertEqual(json.loads(saved[0])["status"], "running")
            exported = call("/api/runs/" + created["id"] + "/export.json")[1]
            self.assertTrue(verify_integrity(exported))
        finally:
            process.terminate()
            process.wait(timeout=10)
            reader.join(timeout=2)
            process.stdout.close()
            process.stderr.close()
        # Death releases the OS lock without unsafe stale-PID or unlink handling.
        self.assertEqual(self.check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
