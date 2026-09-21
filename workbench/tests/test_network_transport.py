import errno
import threading
import time
import unittest
from unittest import mock

from workbench.engine import Cancelled, Deadline, DeadlineExceeded
from workbench.network_transport import _connect_bounded


class _FakeSocket:
    def __init__(self, result):
        self.result = result
        self.closed = False
        self.blocking = []
        self.timeouts = []

    def setblocking(self, value):
        self.blocking.append(value)

    def connect_ex(self, _endpoint):
        return self.result

    def getsockopt(self, *_args):
        return 0

    def settimeout(self, value):
        self.timeouts.append(value)

    def close(self):
        self.closed = True


class NetworkTransportConnectTests(unittest.TestCase):
    def test_cancel_closes_pending_connect_without_waiting_for_socket_timeout(self):
        fake = _FakeSocket(errno.EINPROGRESS)
        cancel = threading.Event()
        timer = threading.Timer(0.03, cancel.set)
        timer.start()
        started = time.monotonic()
        try:
            with mock.patch("workbench.network_transport.socket.socket", return_value=fake), \
                 mock.patch("workbench.network_transport.select.select", return_value=([], [], [])):
                with self.assertRaises(Cancelled):
                    _connect_bounded("93.184.216.34", 443, Deadline(1), cancel)
        finally:
            timer.cancel()
        self.assertTrue(fake.closed)
        self.assertLess(time.monotonic() - started, 0.3)

    def test_deadline_closes_pending_connect(self):
        fake = _FakeSocket(errno.EINPROGRESS)
        started = time.monotonic()
        with mock.patch("workbench.network_transport.socket.socket", return_value=fake), \
             mock.patch("workbench.network_transport.select.select", return_value=([], [], [])):
            with self.assertRaises(DeadlineExceeded):
                _connect_bounded("93.184.216.34", 443, Deadline(0.03))
        self.assertTrue(fake.closed)
        self.assertLess(time.monotonic() - started, 0.3)

    def test_immediate_connect_returns_blocking_socket_with_remaining_deadline(self):
        fake = _FakeSocket(0)
        with mock.patch("workbench.network_transport.socket.socket", return_value=fake):
            result = _connect_bounded("93.184.216.34", 443, Deadline(1))
        self.assertIs(result, fake)
        self.assertEqual(fake.blocking, [False, True])
        self.assertTrue(fake.timeouts)
        self.assertGreater(fake.timeouts[-1], 0)
        self.assertLessEqual(fake.timeouts[-1], 1)
        self.assertFalse(fake.closed)

    def test_connect_error_closes_socket(self):
        fake = _FakeSocket(getattr(errno, "ECONNREFUSED", 111))
        with mock.patch("workbench.network_transport.socket.socket", return_value=fake):
            with self.assertRaises(OSError):
                _connect_bounded("93.184.216.34", 443, Deadline(1))
        self.assertTrue(fake.closed)


if __name__ == "__main__":
    unittest.main()
