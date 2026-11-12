import unittest

from sms_sim import main

import unittest

from sms_sim.config import Config
from sms_sim.main import run_simulation, parse_args


class TestMain(unittest.TestCase):

    def test_simulation_completes(self):
        config = Config(
            messages=20,
            senders=3,
            mean_delay=0.001,
            failure_rate=0.1,
            interval=0.01,
            queue_size=5,
            seed=42
        )

        output_lines = []

        result = run_simulation(
            config,
            output=output_lines.append
        )

        self.assertEqual(
            result["sent"] + result["failed"],
            20
        )

    def test_zero_messages(self):
        config = Config(
            messages=0,
            senders=3,
            mean_delay=0.001,
            failure_rate=0.1,
            interval=0.01,
            queue_size=5,
            seed=42
        )

        output_lines = []

        result = run_simulation(
            config,
            output=output_lines.append
        )

        self.assertEqual(
            result["sent"] + result["failed"],
            0
        )
    def test_parse_args(self):
        args = [
            "--messages", "50",
            "--senders", "5",
            "--mean-delay", "0.02",
            "--failure-rate", "0.2",
            "--interval", "0.05",
            "--queue-size", "10",
            "--seed", "123"
        ]

        config = parse_args(args)

        self.assertEqual(config.messages, 50)
        self.assertEqual(config.senders, 5)
        self.assertAlmostEqual(config.mean_delay, 0.02)
        self.assertAlmostEqual(config.failure_rate, 0.2)
        self.assertAlmostEqual(config.interval, 0.05)
        self.assertEqual(config.queue_size, 10)
        self.assertEqual(config.seed, 123)