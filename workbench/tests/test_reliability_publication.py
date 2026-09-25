import copy
import tempfile
import threading
import time
import unittest

from workbench.engine import (
    Assessment,
    Cancelled,
    Deadline,
    Scope,
    public_addresses,
    verify_integrity,
)
from workbench.server import State, Store, durable_for_review


def scope():
    return Scope.parse(
        {
            "target": "https://example.com",
            "mode": "analyst",
            "authorized": True,
            "authorization": "Reliability publication fixture",
        }
    )


def reader(_):
    return {
        "status": 200,
        "headers": {"content-type": "application/json"},
        "method": "HEAD",
        "redirect_followed": False,
    }


class ReliabilityPublicationTests(unittest.TestCase):
    def test_assessment_never_notifies_terminal_unsealed_snapshot(self):
        snapshots = []
        report = Assessment(
            scope(), remote_reader=reader, notify=snapshots.append
        ).run()
        self.assertTrue(verify_integrity(report))
        self.assertTrue(snapshots)
        self.assertTrue(all(item["status"] == "running" for item in snapshots))
        self.assertEqual(report["events"][-1]["kind"], "finished")

    def test_state_publishes_only_after_durable_finalize(self):
        with tempfile.TemporaryDirectory() as directory:
            state = State(directory)
            assessment = Assessment(scope(), remote_reader=reader, notify=state.update)
            state.active = assessment.report["id"]
            state.live = copy.deepcopy(assessment.report)
            state.store.save_active(state.live)
            state.run(assessment)
            result = state.get(assessment.report["id"])
            self.assertTrue(verify_integrity(result))
            self.assertEqual(result["durability"]["status"], "durable")
            self.assertEqual(
                result["durability"]["terminal_publication"], "after_atomic_commit"
            )
            self.assertFalse(result["durability"]["checkpoint_gap_observed"])
            self.assertTrue(durable_for_review(result))
            self.assertEqual(state.store.get(result["id"]), result)

    def test_finalize_failure_is_explicit_memory_only(self):
        with tempfile.TemporaryDirectory() as directory:
            state = State(directory)
            assessment = Assessment(scope(), remote_reader=reader, notify=state.update)
            state.active = assessment.report["id"]
            state.live = copy.deepcopy(assessment.report)
            state.store.save_active(state.live)

            def fail(_):
                raise OSError("synthetic persistence failure")

            state.store.finalize = fail
            state.run(assessment)
            result = state.get(assessment.report["id"])
            self.assertTrue(verify_integrity(result))
            self.assertEqual(result["durability"]["status"], "not_durable")
            self.assertEqual(
                result["durability"]["reason"], "terminal_persistence_failed"
            )
            self.assertFalse(durable_for_review(result))
            self.assertTrue(
                any("memory-only" in item for item in result["limitations"])
            )

    def test_checkpoint_failure_is_visible_even_when_terminal_commit_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            state = State(directory)
            assessment = Assessment(scope(), remote_reader=reader, notify=state.update)
            state.active = assessment.report["id"]
            state.live = copy.deepcopy(assessment.report)
            original = state.store.save_active
            original(state.live)

            def fail_checkpoint(_):
                raise OSError("synthetic checkpoint failure")

            state.store.save_active = fail_checkpoint
            state.update(copy.deepcopy(state.live))
            self.assertTrue(state.checkpoint_persistence_failed)
            state.run(assessment)
            result = state.get(assessment.report["id"])
            self.assertEqual(result["durability"]["status"], "durable")
            self.assertTrue(result["durability"]["checkpoint_gap_observed"])
            self.assertTrue(verify_integrity(result))

    def test_restart_recovery_is_explicitly_durable_interrupted_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            running = Assessment(scope()).report
            store.save_active(running)
            state = State(directory)
            recovered = state.store.get(running["id"])
            self.assertEqual(recovered["status"], "interrupted")
            self.assertEqual(recovered["durability"]["status"], "durable")
            self.assertEqual(
                recovered["durability"]["terminal_publication"],
                "restart_recovery_transaction",
            )
            self.assertTrue(durable_for_review(recovered))
            self.assertTrue(verify_integrity(recovered))

    def test_cancel_interrupts_slow_dns_wait_without_opening_connection(self):
        cancel = threading.Event()

        def slow(*_args, **_kwargs):
            time.sleep(0.5)
            return []

        timer = threading.Timer(0.03, cancel.set)
        timer.start()
        started = time.monotonic()
        try:
            with self.assertRaises(Cancelled):
                public_addresses("example.com", 443, slow, Deadline(1), cancel)
        finally:
            timer.cancel()
        self.assertLess(time.monotonic() - started, 0.2)


if __name__ == "__main__":
    unittest.main()
