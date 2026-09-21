import unittest
from workbench.contracts import ADAPTER_SCHEMA, normalize_adapter_result


class ContractTests(unittest.TestCase):
    def good(self):
        return {
            "schema": ADAPTER_SCHEMA,
            "adapter": {"id": "fixture.scanner", "version": "1.2.3"},
            "status": "completed",
            "coverage": {"objects_tested": 3, "objects_total": 3, "notes": ["fixture only"]},
            "findings": [{
                "rule": "sql/injection-candidate",
                "title": "Possible query injection",
                "severity": "high",
                "confidence": 0.91,
                "evidence": {"location": "/search", "parameter": "q", "indicator": "synthetic"},
                "remediation": "Use parameterized queries and validate the affected data flow.",
                "external_id": "fixture-1",
            }],
        }

    def test_normalizes_as_candidate_not_verified(self):
        result = normalize_adapter_result(self.good(), asset_key="asset-1")
        self.assertEqual(result["findings"][0]["verification"], "candidate")
        self.assertEqual(result["verification_authority"], "workbench_only")
        self.assertEqual(len(result["findings"][0]["evidence_sha256"]), 64)

    def test_fingerprint_stable_for_same_asset(self):
        one = normalize_adapter_result(self.good(), asset_key="asset-1")
        two = normalize_adapter_result(self.good(), asset_key="asset-1")
        self.assertEqual(one["findings"][0]["fingerprint"], two["findings"][0]["fingerprint"])

    def test_fingerprint_separates_assets(self):
        one = normalize_adapter_result(self.good(), asset_key="asset-1")
        two = normalize_adapter_result(self.good(), asset_key="asset-2")
        self.assertNotEqual(one["findings"][0]["fingerprint"], two["findings"][0]["fingerprint"])

    def test_rejects_adapter_claiming_extra_verification_field(self):
        payload = self.good(); payload["findings"][0]["verification"] = "verified"
        with self.assertRaises(ValueError):
            normalize_adapter_result(payload, asset_key="asset")

    def test_rejects_invalid_coverage(self):
        payload = self.good(); payload["coverage"]["objects_tested"] = 4
        with self.assertRaises(ValueError):
            normalize_adapter_result(payload, asset_key="asset")

    def test_error_requires_summary(self):
        payload = self.good(); payload["status"] = "error"; payload["findings"] = []
        with self.assertRaises(ValueError):
            normalize_adapter_result(payload, asset_key="asset")

    def test_rejects_oversized_evidence(self):
        payload = self.good(); payload["findings"][0]["evidence"] = {"x": "a" * 40000}
        with self.assertRaises(ValueError):
            normalize_adapter_result(payload, asset_key="asset")


if __name__ == "__main__": unittest.main()
