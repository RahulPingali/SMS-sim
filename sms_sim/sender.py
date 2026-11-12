import time

def run_sender(message_queue, stats, mean_delay, failure_rate, rng, sleep=time.sleep):
    """
    Simulate sending messages from the message_queue.
    For each message, simulate a delay based on mean_delay and a random failure based on failure_rate.
    Record the result in stats.
    Accept an RNG instance for reproducible, deterministic testing.
    Accept a sleep function for testing purposes (default is time.sleep).
    """

    if mean_delay <= 0:
        raise ValueError("mean_delay must be a positive number")
    if not (0 <= failure_rate <= 1):
        raise ValueError("failure_rate must be between 0 and 1")
    while True:
        message = message_queue.get()
        try:
            if message is None:
                break

            start_time = time.perf_counter()
            delay = rng.expovariate(1.0 / mean_delay)
            sleep(delay)
            success = rng.random() >= failure_rate
            elapsed_time = time.perf_counter() - start_time
            stats.record(success, elapsed_time)

        finally:
            message_queue.task_done()
