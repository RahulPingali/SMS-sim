import unittest
import random
import string
from queue import Queue
from sms_sim.producer import generate_message
from sms_sim.producer import produce

class TestGenerateMessage(unittest.TestCase):
    def test_message_length(self):
        rng = random.Random(42)
        max_length = 50
        for _ in range(100):
            message = generate_message(rng, max_length)
            self.assertTrue(1 <= len(message) <= max_length)
    
    def test_same_seed(self):
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        message1 = generate_message(rng1, 50)
        message2 = generate_message(rng2, 50)
        self.assertEqual(message1, message2)

    def test_valid_characters(self):
        rng = random.Random(42)
        max_length = 50
        for _ in range(100):
            message = generate_message(rng, max_length)
            for char in message:
                self.assertIn(char, string.ascii_letters + string.digits + string.punctuation + ' ')

    def test_min_length(self):
        rng = random.Random(42)
        message = generate_message(rng, 1)
        self.assertEqual(len(message), 1)

    def test_invalid_max_length(self):
        rng = random.Random(42)
        with self.assertRaises(ValueError):
            generate_message(rng, 0)

class testProduce(unittest.TestCase):
    def test_produce_count(self):
        rng = random.Random(42)
        num_queue = Queue()
        num_messages = 10
        produce(num_queue, num_messages, rng, max_length=50)
        self.assertEqual(num_queue.qsize(), num_messages)

    def test_produce_message_validity(self):
        rng = random.Random(42)
        num_queue = Queue()
        num_messages = 10
        produce(num_queue, num_messages, rng, max_length=50)
        while not num_queue.empty():
            message = num_queue.get()
            self.assertIsInstance(message, str)
            self.assertTrue(1 <= len(message) <= 50)
            for char in message:
                self.assertIn(char, string.ascii_letters + string.digits + string.punctuation + ' ')

    def test_produce_reproducibility(self):
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        num_queue1 = Queue()
        num_queue2 = Queue()
        num_messages = 10
        produce(num_queue1, num_messages, rng1, max_length=50)
        produce(num_queue2, num_messages, rng2, max_length=50)
        while not num_queue1.empty() and not num_queue2.empty():
            message1 = num_queue1.get()
            message2 = num_queue2.get()
            self.assertEqual(message1, message2)
            
    def test_produce_zero_messages(self):
        rng = random.Random(42)
        num_queue = Queue()
        num_messages = 0
        produce(num_queue, num_messages, rng, max_length=50)
        self.assertEqual(num_queue.qsize(), 0)