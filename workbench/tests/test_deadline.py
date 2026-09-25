import socket
import time
import unittest

from workbench.engine import (
    Assessment,
    Deadline,
    DeadlineExceeded,
    Scope,
    public_addresses,
    verify_integrity,
)
from workbench.ollama_runtime import LocalRuntime, OllamaError


def scope():
    return Scope.parse(
        {
            "target": "https://example.com",
            "mode": "analyst",
            "authorized": True,
            "authorization": "Deadline fixture",
        }
    )


class DeadlineTests(unittest.TestCase):
    def test_deadline_rejects_invalid_budget(self):
        for value in (0, -1, True, 301, "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Deadline(value)

    def test_bounded_resolver_returns_before_slow_resolver_finishes(self):
        def slow(*_args, **_kwargs):
            time.sleep(0.5)
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))]

        started = time.monotonic()
        with self.assertRaises(DeadlineExceeded):
            public_addresses("example.com", 443, slow, Deadline(0.03))
        self.assertLess(time.monotonic() - started, 0.3)

    def test_assessment_reports_timed_out_not_completed(self):
        def slow_reader(_):
            time.sleep(0.04)
            return {
                "status": 200,
                "headers": {"content-type": "application/json"},
                "method": "HEAD",
                "redirect_followed": False,
            }

        report = Assessment(
            scope(), remote_reader=slow_reader, deadline_seconds=0.01
        ).run()
        self.assertEqual(report["status"], "timed_out")
        self.assertEqual(report["verdict"], "inconclusive")
        self.assertTrue(
            any(check["tool"] == "assessment_deadline" for check in report["checks"])
        )
        self.assertTrue(verify_integrity(report))

    def test_report_declares_wall_clock_budget(self):
        report = Assessment(
            scope(),
            remote_reader=lambda _: {
                "status": 200,
                "headers": {"content-type": "application/json"},
                "method": "HEAD",
                "redirect_followed": False,
            },
            deadline_seconds=5,
        ).run()
        self.assertEqual(report["execution_budget"]["wall_clock_seconds"], 5.0)
        self.assertIn("network/model", report["execution_budget"]["enforcement"])

    def test_ollama_runtime_caps_operations_to_assessment_deadline(self):
        runtime = LocalRuntime("local:test")
        runtime.set_deadline(time.monotonic() + 0.2)
        self.assertLessEqual(runtime._operation_timeout(90), 0.2)
        self.assertTrue(runtime.telemetry()["assessment_deadline_attached"])

    def test_ollama_expired_deadline_fails_before_network(self):
        runtime = LocalRuntime("local:test")
        with self.assertRaises(OllamaError) as captured:
            runtime.set_deadline(time.monotonic() - 1)
        self.assertEqual(captured.exception.code, "deadline_exceeded")


if __name__ == "__main__":
    unittest.main()
