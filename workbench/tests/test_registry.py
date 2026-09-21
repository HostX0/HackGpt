import tempfile
import threading
import unittest
from pathlib import Path

from workbench.registry import ExecutionRegistry, RegistryPolicy


class _StepCancel:
    def __init__(self, trigger_at):
        self.trigger_at = trigger_at
        self.calls = 0

    def is_set(self):
        self.calls += 1
        return self.calls >= self.trigger_at


class ExecutionRegistryTests(unittest.TestCase):
    def test_describe_returns_only_reviewed_adapters(self):
        declarations = ExecutionRegistry().describe()
        self.assertEqual({item["adapter"]["id"] for item in declarations}, {
            "native-project-metadata", "native-web-headers", "semgrep-project-local",
        })
        self.assertTrue(all("command" not in item for item in declarations))
        semgrep = next(item for item in declarations if item["adapter"]["id"] == "semgrep-project-local")
        self.assertEqual(semgrep["launcher"], "fixed_container")
        self.assertEqual(semgrep["network"], "none")
        self.assertFalse(semgrep["writes"])

    def test_unknown_adapter_and_dynamic_execution_fields_fail_closed(self):
        registry = ExecutionRegistry()
        with self.assertRaises(ValueError):
            registry.execute("python-module", {"command": "anything"})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                registry.execute("native-project-metadata", {
                    "root": directory, "asset_key": "fixture", "command": "anything"
                })
            with self.assertRaises(ValueError):
                registry.plan("semgrep-project-local", {
                    "root": directory, "asset_key": "fixture", "command": "anything"
                })

    def test_filesystem_policy_blocks_project_adapters_but_not_web(self):
        registry = ExecutionRegistry(RegistryPolicy(allow_filesystem=False, allow_network=True))
        self.assertEqual([item["adapter"]["id"] for item in registry.describe()], ["native-web-headers"])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                registry.execute("native-project-metadata", {"root": directory, "asset_key": "fixture"})
            with self.assertRaises(PermissionError):
                registry.plan("semgrep-project-local", {"root": directory, "asset_key": "fixture"})

    def test_network_policy_blocks_web_but_offline_semgrep_remains_describable(self):
        calls = []
        registry = ExecutionRegistry(RegistryPolicy(allow_filesystem=True, allow_network=False))
        ids = {item["adapter"]["id"] for item in registry.describe()}
        self.assertIn("semgrep-project-local", ids)
        self.assertNotIn("native-web-headers", ids)
        with self.assertRaises(PermissionError):
            registry.execute(
                "native-web-headers",
                {"target": "https://example.com", "asset_key": "fixture"},
                web_reader=lambda target: calls.append(target),
            )
        self.assertEqual(calls, [])

    def test_semgrep_plan_is_sanitized_and_does_not_probe_docker(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = ExecutionRegistry().plan("semgrep-project-local", {
                "root": directory,
                "asset_key": "fixture",
                "max_files": 20,
                "timeout_seconds": 30,
            })
        summary = plan["request_summary"]
        self.assertEqual(plan["declaration"]["launcher"], "fixed_container")
        self.assertEqual(plan["declaration"]["network"], "none")
        self.assertFalse(summary["full_path_included"])
        self.assertEqual(summary["tool"], "semgrep-ce")
        self.assertEqual(summary["max_files"], 20)

    def test_project_execution_remains_candidate_and_secret_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("API_KEY=DO_NOT_EXPORT")
            result = ExecutionRegistry().execute(
                "native-project-metadata", {"root": directory, "asset_key": "fixture"}
            )
        self.assertEqual(result["findings"][0]["verification"], "candidate")
        self.assertNotIn("DO_NOT_EXPORT", repr(result))

    def test_web_execution_remains_candidate_and_body_free(self):
        result = ExecutionRegistry().execute(
            "native-web-headers",
            {"target": "https://example.com", "asset_key": "fixture"},
            web_reader=lambda _: {
                "status": 200,
                "headers": {"content-type": "text/html"},
                "method": "HEAD",
                "redirect_followed": False,
            },
        )
        self.assertTrue(result["findings"])
        self.assertTrue(all(item["verification"] == "candidate" for item in result["findings"]))
        self.assertTrue(all(item["evidence"]["body_read"] is False for item in result["findings"]))

    def test_pre_cancelled_execution_stops_before_adapter_io(self):
        cancel = threading.Event()
        cancel.set()
        calls = []
        with self.assertRaises(InterruptedError):
            ExecutionRegistry().execute(
                "native-web-headers",
                {"target": "https://example.com", "asset_key": "fixture"},
                cancel=cancel,
                web_reader=lambda target: calls.append(target),
            )
        self.assertEqual(calls, [])

    def test_project_cancellation_is_propagated_beyond_registry_preflight(self):
        cancel = _StepCancel(trigger_at=4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(10):
                (root / f"file-{index}.txt").write_text("x")
            with self.assertRaises(InterruptedError):
                ExecutionRegistry().execute(
                    "native-project-metadata",
                    {"root": directory, "asset_key": "fixture"},
                    cancel=cancel,
                )
        self.assertGreaterEqual(cancel.calls, 4)

    def test_invalid_policy_is_rejected(self):
        for kwargs in ({"max_effect": "unbounded"}, {"allow_filesystem": 1}, {"allow_network": None}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                RegistryPolicy(**kwargs)


if __name__ == "__main__":
    unittest.main()
