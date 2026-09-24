import unittest

from workbench.retest import compare_reports


def report(
    run,
    *,
    target="lab://fixture",
    environment="synthetic_lab",
    findings=None,
    checks=None,
):
    return {
        "id": run,
        "target": target,
        "environment": environment,
        "status": "completed",
        "mode": "analyst",
        "engine_version": "0.1.0",
        "findings": findings or [],
        "checks": checks or [],
    }


def finding():
    return {
        "id": "finding-1",
        "fingerprint": "fp-1",
        "rule": "header/content-security-policy",
        "title": "CSP missing",
        "remediation": "Add CSP",
        "evidence_sha256": "e" * 64,
    }


class RetestScopeIdentityTests(unittest.TestCase):
    def test_missing_target_identity_cannot_produce_not_reproduced(self):
        previous = report("before", target=None, findings=[finding()])
        current = report(
            "after",
            target=None,
            checks=[{"tool": "http_baseline", "status": "completed"}],
        )
        diff = compare_reports(previous, current)
        self.assertFalse(diff["comparable_scope"])
        self.assertIsNone(diff["scope_comparison"]["same_target"])
        self.assertEqual(diff["items"][0]["state"], "not_retested")
        self.assertIn("identity was not recorded", diff["items"][0]["reason"])

    def test_blank_environment_identity_cannot_produce_not_reproduced(self):
        previous = report("before", environment="   ", findings=[finding()])
        current = report(
            "after",
            environment="   ",
            checks=[{"tool": "http_baseline", "status": "completed"}],
        )
        diff = compare_reports(previous, current)
        self.assertFalse(diff["comparable_scope"])
        self.assertIsNone(diff["scope_comparison"]["same_environment"])
        self.assertEqual(diff["items"][0]["state"], "not_retested")

    def test_self_comparison_is_rejected(self):
        same = report("same-run", findings=[finding()])
        with self.assertRaisesRegex(ValueError, "distinct assessment runs"):
            compare_reports(same, same)

    def test_blank_run_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid report shape"):
            compare_reports(report("   "), report("after"))


if __name__ == "__main__":
    unittest.main()
