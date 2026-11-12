import random
import string

CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '

def generate_message(rng, max_length=100) -> str:
    """
    Generate and return a random message string.
    Message length ranges from 1 to max_length characters.
    Accept an RNG instance for reproducible, deterministic testing.
    """
    if not isinstance(rng, random.Random):
        raise TypeError("rng must be an instance of random.Random")
    if max_length < 1:
        raise ValueError("max_length must be a positive integer")
    
    length = rng.randint(1, max_length)
    selected = rng.choices(CHARACTERS, k=length)
    return "".join(selected)

def produce(num_queue, num_messages, rng, max_length=100):
    for _ in range(num_messages):
        message = generate_message(rng, max_length)
        num_queue.put(message)
