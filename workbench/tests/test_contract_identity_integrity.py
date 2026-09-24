import unittest

from workbench.contracts import ADAPTER_SCHEMA, normalize_adapter_result


def payload(findings):
    return {
        "schema": ADAPTER_SCHEMA,
        "adapter": {"id": "example-adapter", "version": "1"},
        "status": "completed",
        "coverage": {"objects_tested": 2, "objects_total": 2, "notes": []},
        "findings": findings,
    }


def finding(external_id=None):
    item = {
        "rule": "example/missing-policy",
        "title": "Missing policy",
        "severity": "medium",
        "confidence": 0.9,
        "evidence": {"kind": "owned-fixture"},
        "remediation": "Add the policy.",
    }
    if external_id is not None:
        item["external_id"] = external_id
    return item


class AdapterIdentityIntegrityTests(unittest.TestCase):
    def test_duplicate_implicit_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ambiguous duplicate identity"):
            normalize_adapter_result(
                payload([finding(), finding()]), asset_key="owned-fixture"
            )

    def test_duplicate_explicit_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ambiguous duplicate identity"):
            normalize_adapter_result(
                payload([finding("same"), finding("same")]),
                asset_key="owned-fixture",
            )

    def test_distinct_external_ids_produce_distinct_fingerprints(self):
        result = normalize_adapter_result(
            payload([finding("first"), finding("second")]), asset_key="owned-fixture"
        )
        fingerprints = [item["fingerprint"] for item in result["findings"]]
        self.assertEqual(len(fingerprints), 2)
        self.assertEqual(len(set(fingerprints)), 2)
        self.assertEqual(
            [item["external_id"] for item in result["findings"]],
            ["first", "second"],
        )


if __name__ == "__main__":
    unittest.main()
