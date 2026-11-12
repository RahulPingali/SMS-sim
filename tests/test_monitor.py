from sms_sim import monitor
from sms_sim.stats import Stats
from threading import Thread, Event
import unittest
import time

class TestMonitor(unittest.TestCase):
    def test_monitor_stops(self):
        stats_instance = Stats()
        stop_event = Event()
        output_list = []

        def fake_output(message):
            output_list.append(message)

        monitor_thread = Thread(
            target=monitor.run_monitor,
            args=(stats_instance, 0.1, stop_event, fake_output)
        )
        monitor_thread.start()

        time.sleep(0.3)
        stop_event.set()
        monitor_thread.join(timeout=1)

        self.assertFalse(monitor_thread.is_alive())
        self.assertTrue(len(output_list) > 0) 

    def test_monitor_periodic_updates(self):
        stats_instance = Stats()
        stop_event = Event()
        output_list = []

        def fake_output(message):
            output_list.append(message)

        monitor_thread = Thread(
            target=monitor.run_monitor,
            args=(stats_instance, 0.1, stop_event, fake_output)
        )
        monitor_thread.start()

        for _ in range(5):
            stats_instance.record(success=True, elapsed=0.1)
            time.sleep(0.05)

        stop_event.set() 
        monitor_thread.join(timeout=1)

        self.assertTrue(len(output_list) > 0)

    def test_invalid_interval(self):
        stats_instance = Stats()
        stop_event = Event()

        with self.assertRaises(ValueError):
            monitor.run_monitor(stats_instance, -1, stop_event, print) 

    def test_immediate_stop(self):
        stats_instance = Stats()
        stop_event = Event()
        output_list = []

        def fake_output(message):
            output_list.append(message)

        stop_event.set()

        monitor_thread = Thread(
            target=monitor.run_monitor,
            args=(stats_instance, 0.1, stop_event, fake_output)
        )

        monitor_thread.start()
        monitor_thread.join(timeout=1)
        self.assertFalse(monitor_thread.is_alive())
        self.assertEqual(len(output_list), 1)
        self.assertTrue(output_list[0].startswith("Final Stats"))