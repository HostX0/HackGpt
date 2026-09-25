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
    mode="analyst",
    engine_version="0.1.0",
):
    return {
        "id": run,
        "target": target,
        "environment": environment,
        "status": status,
        "mode": mode,
        "engine_version": engine_version,
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
    source=None,
    evidence=None,
):
    item = {
        "fingerprint": fp,
        "rule": rule,
        "title": title,
        "remediation": remediation,
        "evidence_sha256": evidence_sha,
        "id": finding_id,
    }
    if source is not None:
        item["source"] = source
    if evidence is not None:
        item["evidence"] = evidence
    return item


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

    def test_exact_adapter_version_allows_not_reproduced(self):
        prior = finding(
            "x",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/1",
        )
        current = report(
            "b",
            environment="synthetic_lab",
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "1"},
                }
            ],
        )
        diff = compare_reports(report("a", findings=[prior]), current)
        item = diff["items"][0]
        self.assertEqual(item["state"], "not_reproduced")
        self.assertEqual(item["recheck"]["coverage"]["status"], "completed")
        self.assertEqual(
            item["recheck"]["coverage"]["expected_adapter"],
            {"id": "native-web-headers", "version": "1"},
        )

    def test_versioned_web_adapter_contract_supplies_fixed_head_method(self):
        prior = finding(
            "x",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/1",
            evidence={"method": "HEAD"},
        )
        current = report(
            "b",
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "1"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "not_reproduced")
        self.assertEqual(item["recheck"]["coverage"]["status"], "completed")
        self.assertEqual(item["recheck"]["coverage"]["observed_methods"], ["HEAD"])

    def test_unknown_adapter_version_never_infers_method_contract(self):
        prior = finding(
            "x",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/9",
            evidence={"method": "HEAD"},
        )
        current = report(
            "b",
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "9"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "method_unknown")
        self.assertEqual(item["recheck"]["coverage"]["observed_methods"], [])

    def test_adapter_version_change_is_not_retested(self):
        prior = finding(
            "x",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/1",
        )
        current = report(
            "b",
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "2"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "version_changed")
        self.assertEqual(
            item["recheck"]["coverage"]["observed_adapters"],
            [{"id": "native-web-headers", "version": "2"}],
        )

    def test_missing_prior_adapter_identity_is_not_retested(self):
        prior = finding("x", rule="web/missing-content-security-policy")
        current = report(
            "b",
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "1"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "identity_unknown")

    def test_legacy_method_change_is_not_retested(self):
        prior = finding("x", evidence={"method": "HEAD"})
        current = report(
            "b",
            checks=[
                {
                    "tool": "http_baseline",
                    "status": "completed",
                    "evidence": {"method": "GET"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "not_retested")
        self.assertEqual(item["recheck"]["coverage"]["status"], "method_changed")
        self.assertEqual(item["recheck"]["coverage"]["expected_method"], "HEAD")
        self.assertEqual(item["recheck"]["coverage"]["observed_methods"], ["GET"])

    def test_same_fingerprint_remains_present_despite_adapter_version_drift(self):
        prior = finding(
            "same",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/1",
        )
        current_finding = finding(
            "same",
            rule="web/missing-content-security-policy",
            source="adapter/native-web-headers/2",
        )
        current = report(
            "b",
            findings=[current_finding],
            checks=[
                {
                    "tool": "native-web-headers",
                    "status": "completed",
                    "adapter": {"id": "native-web-headers", "version": "2"},
                }
            ],
        )
        item = compare_reports(report("a", findings=[prior]), current)["items"][0]
        self.assertEqual(item["state"], "still_present")
        self.assertEqual(item["recheck"]["coverage"]["status"], "version_changed")

    def test_mode_and_engine_drift_are_reported_without_overriding_exact_coverage(self):
        current = report(
            "b",
            mode="verify",
            engine_version="0.2.0",
            checks=[{"tool": "http_baseline", "status": "completed"}],
        )
        diff = compare_reports(
            report(
                "a",
                findings=[finding("x")],
                mode="analyst",
                engine_version="0.1.0",
            ),
            current,
        )
        self.assertFalse(diff["scope_comparison"]["same_mode"])
        self.assertFalse(diff["scope_comparison"]["same_engine_version"])
        self.assertEqual(diff["items"][0]["state"], "not_reproduced")


if __name__ == "__main__":
    unittest.main()
