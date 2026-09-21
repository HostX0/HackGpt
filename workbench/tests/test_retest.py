import unittest
from workbench.retest import compare_reports


def report(run, target="lab://fixture", findings=None, checks=None, status="completed"):
    return {"id": run, "target": target, "environment": "synthetic_lab", "status": status,
            "findings": findings or [], "checks": checks or []}


def finding(fp, rule="header/content-security-policy", title="CSP missing"):
    return {"fingerprint": fp, "rule": rule, "title": title}


class RetestTests(unittest.TestCase):
    def test_still_present(self):
        diff = compare_reports(report("a", findings=[finding("x")]), report("b", findings=[finding("x")]))
        self.assertEqual(diff["counts"]["still_present"], 1)

    def test_absent_with_comparable_check_is_not_reproduced_not_fixed(self):
        current = report("b", checks=[{"tool": "http_baseline", "status": "completed"}])
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        self.assertEqual(diff["items"][0]["state"], "not_reproduced")
        self.assertNotIn("fixed", {item["state"] for item in diff["items"]})

    def test_missing_coverage_is_not_retested(self):
        diff = compare_reports(report("a", findings=[finding("x")]), report("b"))
        self.assertEqual(diff["items"][0]["state"], "not_retested")

    def test_scope_change_prevents_reproduced_claim(self):
        current = report("b", target="lab://other", checks=[{"tool": "http_baseline", "status": "completed"}])
        diff = compare_reports(report("a", findings=[finding("x")]), current)
        self.assertFalse(diff["comparable_scope"])
        self.assertEqual(diff["items"][0]["state"], "not_retested")

    def test_new_finding(self):
        diff = compare_reports(report("a"), report("b", findings=[finding("y")]))
        self.assertEqual(diff["counts"]["new"], 1)

    def test_running_report_rejected(self):
        with self.assertRaises(ValueError):
            compare_reports(report("a"), report("b", status="running"))


if __name__ == "__main__": unittest.main()
