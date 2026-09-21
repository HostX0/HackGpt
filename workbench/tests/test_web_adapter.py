import unittest

from workbench.web_adapter import WebHeaderAdapter, WebHeaderPolicy


class WebHeaderAdapterTests(unittest.TestCase):
    def test_vulnerable_fixture_yields_candidate_header_observations(self):
        adapter = WebHeaderAdapter()
        result = adapter.run(
            "https://example.com",
            asset_key="web-fixture",
            reader=lambda _: {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "method": "HEAD",
                "redirect_followed": False,
            },
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual({finding["rule"] for finding in result["findings"]}, {
            "web/missing-content-security-policy", "web/missing-content-type-options",
        })
        self.assertTrue(all(finding["verification"] == "candidate" for finding in result["findings"]))
        self.assertTrue(all(finding["evidence"]["body_read"] is False for finding in result["findings"]))

    def test_fixed_fixture_has_no_findings(self):
        result = WebHeaderAdapter().run(
            "https://example.com",
            asset_key="web-fixture",
            reader=lambda _: {
                "status": 200,
                "headers": {
                    "content-type": "text/html",
                    "content-security-policy": "default-src 'self'",
                    "x-content-type-options": "nosniff",
                },
                "method": "HEAD",
                "redirect_followed": False,
            },
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["coverage"]["objects_tested"], 1)
        self.assertEqual(result["coverage"]["objects_total"], 1)

    def test_non_2xx_is_partial_not_success_claim(self):
        result = WebHeaderAdapter().run(
            "https://example.com",
            asset_key="web-fixture",
            reader=lambda _: {
                "status": 302,
                "headers": {"content-type": "text/html"},
                "method": "HEAD",
                "redirect_followed": False,
            },
        )
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["findings"], [])
        self.assertTrue(any("inconclusive" in note for note in result["coverage"]["notes"]))

    def test_non_html_does_not_apply_html_rules(self):
        result = WebHeaderAdapter().run(
            "https://example.com",
            asset_key="web-fixture",
            reader=lambda _: {
                "status": 200,
                "headers": {"content-type": "application/json"},
                "method": "HEAD",
                "redirect_followed": False,
            },
        )
        self.assertEqual(result["findings"], [])
        self.assertTrue(any("not identified as HTML" in note for note in result["coverage"]["notes"]))

    def test_query_target_is_rejected_before_reader(self):
        calls = []
        with self.assertRaises(ValueError):
            WebHeaderAdapter().run(
                "https://example.com/?token=secret",
                asset_key="web-fixture",
                reader=lambda value: calls.append(value),
            )
        self.assertEqual(calls, [])

    def test_reader_cannot_return_response_body_or_raw_fields(self):
        with self.assertRaises(ValueError):
            WebHeaderAdapter().run(
                "https://example.com",
                asset_key="web-fixture",
                reader=lambda _: {
                    "status": 200,
                    "headers": {"content-type": "text/html"},
                    "method": "HEAD",
                    "redirect_followed": False,
                    "body": "sensitive",
                },
            )

    def test_reader_must_honor_head_no_redirect_contract(self):
        for field, value in (("method", "GET"), ("redirect_followed", True)):
            payload = {
                "status": 200,
                "headers": {"content-type": "text/html"},
                "method": "HEAD",
                "redirect_followed": False,
            }
            payload[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                WebHeaderAdapter().run("https://example.com", asset_key="web-fixture", reader=lambda _, p=payload: p)

    def test_unapproved_header_is_rejected(self):
        with self.assertRaises(ValueError):
            WebHeaderAdapter().run(
                "https://example.com",
                asset_key="web-fixture",
                reader=lambda _: {
                    "status": 200,
                    "headers": {"set-cookie": "session=secret"},
                    "method": "HEAD",
                    "redirect_followed": False,
                },
            )

    def test_execution_declaration_is_passive_and_one_request(self):
        declaration = WebHeaderAdapter(WebHeaderPolicy(timeout_seconds=9)).execution_declaration()
        self.assertEqual(declaration["effect_level"], "passive")
        self.assertEqual(declaration["network"], "scoped_target")
        self.assertEqual(declaration["filesystem"], "none")
        self.assertFalse(declaration["subprocess"])
        self.assertEqual(declaration["limits"], {"max_objects": 1, "max_requests": 1, "timeout_seconds": 9})

    def test_policy_is_fixed_to_one_request_and_bounded_timeout(self):
        for kwargs in ({"max_requests": 0}, {"max_requests": 2}, {"timeout_seconds": 0}, {"timeout_seconds": 61}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                WebHeaderPolicy(**kwargs)

    def test_fingerprint_is_stable_and_asset_scoped(self):
        def reader(_):
            return {"status": 200, "headers": {"content-type": "text/html"}, "method": "HEAD", "redirect_followed": False}

        one = WebHeaderAdapter().run("https://example.com", asset_key="asset-a", reader=reader)
        two = WebHeaderAdapter().run("https://example.com", asset_key="asset-a", reader=reader)
        other = WebHeaderAdapter().run("https://example.com", asset_key="asset-b", reader=reader)
        self.assertEqual([f["fingerprint"] for f in one["findings"]], [f["fingerprint"] for f in two["findings"]])
        self.assertNotEqual(one["findings"][0]["fingerprint"], other["findings"][0]["fingerprint"])


if __name__ == "__main__":
    unittest.main()
