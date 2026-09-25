"""Offline regression tests: DNS answers are fixtures, never contacted."""

import socket
import threading
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from workbench.engine import Cancelled, Deadline, DeadlineExceeded, public_addresses
from workbench import network_transport


def resolver_for(*addresses):
    def resolve(*args, **kwargs):
        return [
            (
                socket.AF_INET6 if ":" in ip else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (ip, 443),
            )
            for ip in addresses
        ]

    return resolve


class PublicScopePolicyTests(unittest.TestCase):
    def test_multicast_and_site_local_are_not_public_web_targets(self):
        for address in (
            "224.0.0.1",
            "239.255.255.250",
            "ff02::1",
            "ff0e::1",
            "fec0::1",
        ):
            with self.subTest(address=address), self.assertRaises(ValueError):
                public_addresses("fixture.invalid", 443, resolver_for(address))

    def test_special_and_transition_ranges_are_denied(self):
        for address in (
            "0.1.2.3",
            "10.0.0.1",
            "100.64.0.1",
            "127.0.0.1",
            "169.254.169.254",
            "172.16.0.1",
            "192.168.0.1",
            "192.0.0.8",
            "192.0.0.9",
            "192.0.0.10",
            "192.88.99.2",
            "192.0.2.1",
            "198.18.0.1",
            "198.51.100.1",
            "203.0.113.1",
            "240.0.0.1",
            "255.255.255.255",
            "::",
            "::1",
            "::ffff:8.8.8.8",
            "64:ff9b::808:808",
            "64:ff9b:1::1",
            "100::1",
            "2001::1",
            "2001:1::1",
            "2001:db8::1",
            "2002:808:808::1",
            "3fff::1",
            "5f00::1",
            "fc00::1",
            "fe80::1",
        ):
            with self.subTest(address=address), self.assertRaises(ValueError):
                public_addresses("fixture.invalid", 443, resolver_for(address))

    def test_zone_identifier_is_rejected_even_on_global_address(self):
        with self.assertRaises(ValueError):
            public_addresses(
                "fixture.invalid", 443, resolver_for("2606:4700:4700::1111%scope")
            )

    def test_mixed_answers_fail_before_transport_connection(self):
        for denied in ("224.0.0.1", "fec0::1", "192.88.99.2"):
            with self.subTest(denied=denied), patch(
                "workbench.engine.socket.getaddrinfo", resolver_for("8.8.8.8", denied)
            ), patch(
                "workbench.network_transport._connect_bounded",
                side_effect=AssertionError("connection must not start"),
            ) as connect:
                with self.assertRaises(ValueError):
                    network_transport.inspect_remote(
                        "https://fixture.invalid/", Deadline(1)
                    )
                connect.assert_not_called()

    def test_denied_dns_is_durable_failure_without_success_receipt(self):
        from workbench.adapter_lifecycle import (
            AdapterLifecycle,
            verify_lifecycle_record,
        )
        from workbench.registry import ExecutionRegistry

        request = {"target": "https://fixture.invalid/", "asset_key": "owned-fixture"}
        with tempfile.TemporaryDirectory() as directory:
            lifecycle = AdapterLifecycle(
                Path(directory) / "reports.sqlite3", ExecutionRegistry()
            )
            plan = lifecycle.plan("native-web-headers", request)
            lifecycle.approve(plan["id"], plan["plan_sha256"])
            with patch(
                "workbench.engine.socket.getaddrinfo",
                resolver_for("8.8.8.8", "ff02::1"),
            ), patch(
                "workbench.network_transport._connect_bounded",
                side_effect=AssertionError("no connection"),
            ) as connect:
                with self.assertRaises(ValueError):
                    lifecycle.execute(plan["id"], "native-web-headers", request)
                connect.assert_not_called()
            stored = lifecycle.get(plan["id"])
            self.assertTrue(verify_lifecycle_record(stored))
            self.assertEqual(stored["status"], "failed")
            self.assertIsNone(stored["receipt"])
            self.assertEqual(stored["plan_sha256"], plan["plan_sha256"])
            self.assertEqual(stored["outcome"]["code"], "execution_rejected")

    def test_public_unicast_order_and_deduplication_remain_compatible(self):
        addresses = ("8.8.8.8", "2606:4700:4700::1111", "8.8.8.8")
        self.assertEqual(
            public_addresses("fixture.invalid", 443, resolver_for(*addresses)),
            list(addresses[:2]),
        )

    def test_pre_cancelled_resolution_does_not_dispatch_resolver(self):
        cancel = threading.Event()
        cancel.set()
        for deadline in (None, Deadline(1)):
            resolver = Mock(return_value=[])
            with self.subTest(deadline=deadline), self.assertRaises(Cancelled):
                public_addresses("fixture.invalid", 443, resolver, deadline, cancel)
            resolver.assert_not_called()

    def test_expired_resolution_does_not_dispatch_resolver(self):
        resolver = Mock(return_value=[])
        deadline = Deadline(1)
        deadline.expires_at = 0
        with self.assertRaises(DeadlineExceeded):
            public_addresses("fixture.invalid", 443, resolver, deadline)
        resolver.assert_not_called()

    def test_cancel_without_explicit_deadline_bounds_caller_wait(self):
        started, release, cancel, finished = (threading.Event() for _ in range(4))
        outcomes = []

        def resolve(*args, **kwargs):
            started.set()
            release.wait(2)
            return resolver_for("8.8.8.8")()

        def run():
            try:
                public_addresses("fixture.invalid", 443, resolve, cancel=cancel)
                outcomes.append("unexpected_completion")
            except Cancelled:
                outcomes.append("cancelled")
            finally:
                finished.set()

        worker = threading.Thread(target=run)
        worker.start()
        try:
            self.assertTrue(started.wait(1))
            cancel.set()
            self.assertTrue(
                finished.wait(0.5), "caller still waited on resolver after cancellation"
            )
            self.assertEqual(outcomes, ["cancelled"])
        finally:
            release.set()
            worker.join(2)


if __name__ == "__main__":
    unittest.main()
