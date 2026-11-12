import unittest
import random
from queue import Queue
from threading import Thread

from sms_sim import sender
from sms_sim.stats import Stats


class TestSender(unittest.TestCase):
    def test_sender_success(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.1
        failure_rate = 0.0
        rng = random.Random(42)

        # Fake sleep to avoid real delays during testing
        def fake_sleep(seconds):
            pass

        # Add a message and shutdown sentinel
        message_queue.put("Test message")
        message_queue.put(None)

        # Run sender in a separate thread
        sender_thread = Thread(
            target=sender.run_sender,
            args=(
                message_queue,
                stats_instance,
                mean_delay,
                failure_rate,
                rng,
                fake_sleep
            )
        )

        sender_thread.start()
        sender_thread.join(timeout=2)

        # Verify the sender terminated
        self.assertFalse(sender_thread.is_alive())

        # Verify statistics
        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 1)
        self.assertEqual(snapshot["failed"], 0)
    
    def test_send_failure(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.1
        failure_rate = 1.0  # Force failure
        rng = random.Random(42)

        def fake_sleep(seconds):
            pass

        message_queue.put("Test message")
        message_queue.put(None)

        sender_thread = Thread(
            target=sender.run_sender,
            args=(
                message_queue,
                stats_instance,
                mean_delay,
                failure_rate,
                rng,
                fake_sleep
            )
        )

        sender_thread.start()
        sender_thread.join(timeout=2)

        self.assertFalse(sender_thread.is_alive())

        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 0)
        self.assertEqual(snapshot["failed"], 1)

    def test_send_multiple(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.1
        failure_rate = 0.5  # 50% chance of failure
        rng = random.Random(42)

        def fake_sleep(seconds):
            pass

        num_messages = 10
        for _ in range(num_messages):
            message_queue.put("Test message")
        message_queue.put(None)

        sender_thread = Thread(
            target=sender.run_sender,
            args=(
                message_queue,
                stats_instance,
                mean_delay,
                failure_rate,
                rng,
                fake_sleep
            )
        )

        sender_thread.start()
        sender_thread.join(timeout=5)

        self.assertFalse(sender_thread.is_alive())

        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"] + snapshot["failed"], num_messages)

    def test_fake_sleep(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.1
        failure_rate = 0.0
        rng = random.Random(42)

        sleep_called = []

        def fake_sleep(seconds):
            sleep_called.append(seconds)

        message_queue.put("Test message")
        message_queue.put(None)

        sender_thread = Thread(
            target=sender.run_sender,
            args=(
                message_queue,
                stats_instance,
                mean_delay,
                failure_rate,
                rng,
                fake_sleep
            )
        )

        sender_thread.start()
        sender_thread.join(timeout=2)

        self.assertFalse(sender_thread.is_alive())
        self.assertEqual(len(sleep_called), 1)
    
    def test_invalid_mean_delay(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.0  # Invalid
        failure_rate = 0.0
        rng = random.Random(42)

        with self.assertRaises(ValueError):
            sender.run_sender(message_queue, stats_instance, mean_delay, failure_rate, rng)
    
    def test_invalid_failure_rate(self):
        message_queue = Queue()
        stats_instance = Stats()
        mean_delay = 0.1
        failure_rate = 1.5  # Invalid
        rng = random.Random(42)

        with self.assertRaises(ValueError):
            sender.run_sender(message_queue, stats_instance, mean_delay, failure_rate, rng)
    