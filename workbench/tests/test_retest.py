import hashlib
import unittest
from workbench.retest import compare_reports


def report(
    run,
    target="lab://fixture",
    environment="synthetic_lab",
    findings=None,
    checks=None,
    status="completed",
):
    return {
        "id": run,
        "target": target,
        "environment": environment,
        "status": status,
        "findings": findings or [],
        "checks": checks or [],
    }


def finding(
    fp,
    rule="header/content-security-policy",
    title="CSP missing",
    remediation="Add a scoped CSP",
    evidence_sha="e" * 64,
    finding_id="f-1",
):
    return {
        "fingerprint": fp,
        "rule": rule,
        "title": title,
        "remediation": remediation,
        "evidence_sha256": evidence_sha,
        "id": finding_id,
    }


class RetestTests(unittest.TestCase):
    def test_still_present(self):
        diff = compare_reports(
            report("a", findings=[finding("x")]), report("b", findings=[finding("x")])
        )
        self.assertEqual(diff["counts"]["still_present"], 1)
        self.assertEqual(diff["items"][0]["recheck"]["previous_run"], "a")
        self.assertEqual(diff["items"][0]["recheck"]["current_run"], "b")

    def test_absent_with_comparable_check_is_not_reproduced_not_fixed(self):
        current = report("b", checks=[{"tool": "http_baseline", "status": "completed"}])
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        item = diff["items"][0]
        self.assertEqual(item["state"], "not_reproduced")
        self.assertNotIn("fixed", {entry["state"] for entry in diff["items"]})
        self.assertEqual(item["recheck"]["coverage"]["status"], "completed")
        self.assertEqual(item["recheck"]["remediation_applied"], "unknown")

    def test_remediation_and_prior_evidence_are_hash_linked_without_claiming_application(
        self,
    ):
        prior = finding(
            "x",
            remediation="Rotate synthetic fixture policy",
            evidence_sha="a" * 64,
            finding_id="finding-old",
        )
        diff = compare_reports(
            report("before", findings=[prior]),
            report("after", checks=[{"tool": "http_baseline", "status": "completed"}]),
        )
        binding = diff["items"][0]["recheck"]
        self.assertEqual(binding["previous_finding_id"], "finding-old")
        self.assertEqual(binding["previous_evidence_sha256"], "a" * 64)
        self.assertEqual(
            binding["remediation_sha256"],
            hashlib.sha256(b"Rotate synthetic fixture policy").hexdigest(),
        )
        self.assertTrue(binding["remediation_guidance_present"])
        self.assertEqual(binding["remediation_applied"], "unknown")

    def test_missing_coverage_is_not_retested(self):
        diff = compare_reports(report("a", findings=[finding("x")]), report("b"))
        item = diff["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "not_executed")

    def test_failed_mapped_check_preserved_as_not_retested(self):
        current = report(
            "b",
            checks=[
                {
                    "tool": "http_baseline",
                    "status": "error",
                    "reason": "synthetic scanner failure",
                }
            ],
        )
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        item = diff["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "error")
        self.assertEqual(
            item["recheck"]["coverage"]["reason"], "synthetic scanner failure"
        )

    def test_scope_change_prevents_reproduced_claim_and_is_explicit(self):
        current = report(
            "b",
            target="lab://other",
            checks=[{"tool": "http_baseline", "status": "completed"}],
        )
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        self.assertFalse(diff["comparable_scope"])
        self.assertFalse(diff["scope_comparison"]["same_target"])
        self.assertTrue(diff["scope_comparison"]["same_environment"])
        self.assertEqual(diff["items"][0]["state"], "not_retested")
        self.assertIn("Target or environment changed", diff["items"][0]["reason"])

    def test_environment_change_prevents_reproduced_claim(self):
        current = report(
            "b",
            environment="authorized_public_web",
            checks=[{"tool": "http_baseline", "status": "completed"}],
        )
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        self.assertFalse(diff["comparable_scope"])
        self.assertTrue(diff["scope_comparison"]["same_target"])
        self.assertFalse(diff["scope_comparison"]["same_environment"])
        self.assertEqual(diff["items"][0]["state"], "not_retested")

    def test_unmapped_rule_never_becomes_not_reproduced(self):
        prior = finding("x", rule="semgrep/example.rule")
        current = report("b", checks=[{"tool": "http_baseline", "status": "completed"}])
        diff = compare_reports(report("a", findings=[prior]), current)
        item = diff["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "unmapped")

    def test_new_finding(self):
        diff = compare_reports(report("a"), report("b", findings=[finding("y")]))
        self.assertEqual(diff["counts"]["new"], 1)
        item = diff["items"][0]
        self.assertEqual(item["state"], "new")
        self.assertEqual(item["recheck"]["remediation_applied"], "not_applicable")

    def test_running_report_rejected(self):
        with self.assertRaises(ValueError):
            compare_reports(report("a"), report("b", status="running"))


if __name__ == "__main__":
    unittest.main()
