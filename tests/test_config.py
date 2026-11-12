import unittest
from sms_sim.config import Config

class TestConfig(unittest.TestCase):

    def test_default_config(self):
        config = Config()

        self.assertEqual(config.messages, 1000)
        self.assertEqual(config.senders, 4)
        self.assertEqual(config.mean_delay, 0.05)
        self.assertEqual(config.failure_rate, 0.05)

    def test_custom_config(self):
        config = Config(messages=500, senders=2, mean_delay=0.1, failure_rate=0.1)

        self.assertEqual(config.messages, 500)
        self.assertEqual(config.senders, 2)
        self.assertEqual(config.mean_delay, 0.1)
        self.assertEqual(config.failure_rate, 0.1)
    
    def test_invalid_messages(self):
        with self.assertRaises(ValueError):
            Config(messages=-1)

    def test_invalid_senders(self):
        with self.assertRaises(ValueError):
            Config(senders=0)

    def test_invalid_mean_delay(self):
        with self.assertRaises(ValueError):
            Config(mean_delay=-1)

    def test_invalid_failure_rate(self):
        with self.assertRaises(ValueError):
            Config(failure_rate=-1)