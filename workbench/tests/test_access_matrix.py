import json
import unittest

from workbench.access_matrix import evaluate_access_matrix

ASSET = "asset:synthetic-role-matrix"


def expectations():
    return [
        {"role": "viewer", "resource": "reports:self", "should_allow": True},
        {"role": "viewer", "resource": "reports:admin", "should_allow": False},
        {"role": "admin", "resource": "reports:admin", "should_allow": True},
    ]


class AccessMatrixTests(unittest.TestCase):
    def test_fixed_matrix_completes_without_findings(self):
        result = evaluate_access_matrix(expectations(), [
            {"role": "viewer", "resource": "reports:self", "observed": "allowed", "control_confirmed": True},
            {"role": "viewer", "resource": "reports:admin", "observed": "denied", "control_confirmed": True},
            {"role": "admin", "resource": "reports:admin", "observed": "allowed", "control_confirmed": True},
        ], asset_key=ASSET)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["matrix_summary"]["mismatches"], 0)
        self.assertEqual(result["coverage"]["objects_tested"], 3)

    def test_unexpected_allow_becomes_candidate_not_verified(self):
        result = evaluate_access_matrix(expectations(), [
            {"role": "viewer", "resource": "reports:self", "observed": "allowed", "control_confirmed": True},
            {"role": "viewer", "resource": "reports:admin", "observed": "allowed", "control_confirmed": True},
            {"role": "admin", "resource": "reports:admin", "observed": "allowed", "control_confirmed": True},
        ], asset_key=ASSET)
        finding = result["findings"][0]
        self.assertEqual(finding["verification"], "candidate")
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["confidence"], 0.9)
        self.assertTrue(finding["evidence"]["denied_control_confirmed"])
        self.assertEqual(result["matrix_summary"]["unexpected_allows"], 1)

    def test_missing_denied_control_lowers_confidence(self):
        result = evaluate_access_matrix([
            {"role": "viewer", "resource": "admin", "should_allow": False},
        ], [
            {"role": "viewer", "resource": "admin", "observed": "allowed", "control_confirmed": False},
        ], asset_key=ASSET)
        self.assertEqual(result["findings"][0]["confidence"], 0.45)
        self.assertFalse(result["findings"][0]["evidence"]["denied_control_confirmed"])

    def test_missing_and_error_cases_are_partial_not_passed(self):
        result = evaluate_access_matrix(expectations(), [
            {"role": "viewer", "resource": "reports:self", "observed": "error", "control_confirmed": False},
            {"role": "viewer", "resource": "reports:admin", "observed": "denied", "control_confirmed": True},
        ], asset_key=ASSET)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["coverage"]["objects_tested"], 1)
        self.assertEqual(result["coverage"]["objects_total"], 3)
        self.assertEqual(result["matrix_summary"]["incomplete_cases"], 2)
        states = {(case["role"], case["resource"]): case["result"] for case in result["cases"]}
        self.assertEqual(states[("viewer", "reports:self")], "inconclusive")
        self.assertEqual(states[("admin", "reports:admin")], "inconclusive")

    def test_unexpected_denial_is_matrix_mismatch_not_security_finding(self):
        result = evaluate_access_matrix([
            {"role": "viewer", "resource": "self", "should_allow": True},
        ], [
            {"role": "viewer", "resource": "self", "observed": "denied", "control_confirmed": True},
        ], asset_key=ASSET)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["matrix_summary"]["mismatches"], 1)
        self.assertEqual(result["cases"][0]["result"], "mismatch")

    def test_contract_never_accepts_credentials_or_bodies(self):
        with self.assertRaises(ValueError):
            evaluate_access_matrix([
                {"role": "viewer", "resource": "admin", "should_allow": False, "password": "secret"},
            ], [], asset_key=ASSET)
        with self.assertRaises(ValueError):
            evaluate_access_matrix([
                {"role": "viewer", "resource": "admin", "should_allow": False},
            ], [
                {"role": "viewer", "resource": "admin", "observed": "allowed", "control_confirmed": True, "response_body": "secret"},
            ], asset_key=ASSET)

    def test_duplicate_and_outside_scope_observations_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate_access_matrix([
                {"role": "viewer", "resource": "admin", "should_allow": False},
                {"role": "viewer", "resource": "admin", "should_allow": False},
            ], [], asset_key=ASSET)
        with self.assertRaisesRegex(ValueError, "outside"):
            evaluate_access_matrix([
                {"role": "viewer", "resource": "self", "should_allow": True},
            ], [
                {"role": "viewer", "resource": "admin", "observed": "allowed", "control_confirmed": True},
            ], asset_key=ASSET)

    def test_finding_evidence_contains_no_reusable_secret_fields(self):
        result = evaluate_access_matrix([
            {"role": "viewer", "resource": "admin", "should_allow": False},
        ], [
            {"role": "viewer", "resource": "admin", "observed": "allowed", "control_confirmed": True},
        ], asset_key=ASSET)
        raw = json.dumps(result["findings"][0])
        self.assertNotIn("password", raw.lower())
        self.assertNotIn("token", raw.lower())
        self.assertTrue(result["findings"][0]["evidence"]["credentials_included"] is False)


if __name__ == "__main__":
    unittest.main()
