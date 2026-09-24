import unittest

from workbench.retest import compare_reports


def report(run, findings=None):
    return {
        "id": run,
        "target": "lab://fixture",
        "environment": "synthetic_lab",
        "status": "completed",
        "mode": "analyst",
        "engine_version": "0.1.0",
        "findings": findings or [],
        "checks": [],
    }


def finding(fingerprint, finding_id):
    return {
        "id": finding_id,
        "fingerprint": fingerprint,
        "rule": "header/content-security-policy",
        "title": "CSP missing",
        "remediation": "Add a scoped CSP",
        "evidence_sha256": "e" * 64,
    }


class RetestIdentityIntegrityTests(unittest.TestCase):
    def test_missing_fingerprint_fails_closed(self):
        prior = finding("x", "f-1")
        del prior["fingerprint"]
        with self.assertRaisesRegex(ValueError, "missing a comparison fingerprint"):
            compare_reports(report("before", [prior]), report("after"))

    def test_empty_fingerprint_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing a comparison fingerprint"):
            compare_reports(report("before", [finding("   ", "f-1")]), report("after"))

    def test_non_object_finding_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "must be an object"):
            compare_reports(report("before", ["not-a-finding"]), report("after"))

    def test_duplicate_previous_fingerprint_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate fingerprint"):
            compare_reports(
                report(
                    "before",
                    [finding("same", "f-1"), finding("same", "f-2")],
                ),
                report("after"),
            )

    def test_duplicate_current_fingerprint_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate fingerprint"):
            compare_reports(
                report("before"),
                report(
                    "after",
                    [finding("same", "f-1"), finding("same", "f-2")],
                ),
            )


if __name__ == "__main__":
    unittest.main()
