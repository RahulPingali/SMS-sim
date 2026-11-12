from sms_sim import stats
import unittest
from threading import Thread
from queue import Queue

class TestStats(unittest.TestCase):
    def test_initial_stats(self):
        stats_instance = stats.Stats()
        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 0)
        self.assertEqual(snapshot["failed"], 0)
        self.assertEqual(snapshot["avg_time"], 0.0)

    def test_record_success(self):
        stats_instance = stats.Stats()
        stats_instance.record(success=True, elapsed=1.5)
        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 1)
        self.assertEqual(snapshot["failed"], 0)
        self.assertAlmostEqual(snapshot["avg_time"], 1.5)

    def test_record_failure(self):
        stats_instance = stats.Stats()
        stats_instance.record(success=False, elapsed=2.0)
        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 0)
        self.assertEqual(snapshot["failed"], 1)
        self.assertAlmostEqual(snapshot["avg_time"], 2.0)

    def test_record_multiple(self):
        stats_instance = stats.Stats()
        stats_instance.record(success=True, elapsed=1.0)
        stats_instance.record(success=False, elapsed=2.0)
        stats_instance.record(success=True, elapsed=3.0)
        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 2)
        self.assertEqual(snapshot["failed"], 1)
        self.assertAlmostEqual(snapshot["avg_time"], (1.0 + 2.0 + 3.0) / 3)
    
    def test_concurrent_recording(self):
        stats_instance = stats.Stats()
        def record_stats():
            for _ in range(100):
                stats_instance.record(success=True, elapsed=1.0)
                stats_instance.record(success=False, elapsed=2.0)

        threads = [Thread(target=record_stats) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        snapshot = stats_instance.snapshot()
        self.assertEqual(snapshot["sent"], 500)
        self.assertEqual(snapshot["failed"], 500)
        self.assertAlmostEqual(snapshot["avg_time"], (500 * 1.0 + 500 * 2.0) / 1000)