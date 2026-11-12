import random
from queue import Queue
from threading import Thread, Event
from sms_sim.producer import produce
from sms_sim.sender import run_sender
from sms_sim.monitor import run_monitor
from sms_sim.stats import Stats
import argparse
from sms_sim import config

def run_simulation(config, output=print):
    """Run the pipeline and return the final stats.
    Starts the monitor and sender threads, then the producer. After the
    producer finishes, sends one None sentinel per sender, waits for all
    senders to exit, and stops the monitor. Returns stats.snapshot():
    a dict with sent, failed, and avg_time.
    """
    message_queue = Queue(maxsize=config.queue_size)
    stats_instance = Stats()
    stop_event = Event()

    monitor_thread = Thread(
        target=run_monitor,
        args=(stats_instance, config.interval, stop_event, output)
    )
    monitor_thread.start()
    sender_threads = []

    for i in range(config.senders):
        if config.seed is not None:
            sender_rng = random.Random(config.seed + 1 + i)
        else:
            sender_rng = random.Random()

        sender_thread = Thread(
            target=run_sender,
            args=(
                message_queue,
                stats_instance,
                config.mean_delay,
                config.failure_rate,
                sender_rng
            )
        )

        sender_threads.append(sender_thread)
        sender_thread.start()

    if config.seed is not None:
        producer_rng = random.Random(config.seed)
    else:
        producer_rng = random.Random()

    producer_thread = Thread(
        target=produce,
        args=(
            message_queue,
            config.messages,
            producer_rng,
            config.max_message_length
        )
    )
    producer_thread.start()
    producer_thread.join()

    for _ in range(config.senders):
        message_queue.put(None)

    for sender_thread in sender_threads:
        sender_thread.join()

    stop_event.set()
    monitor_thread.join()

    return stats_instance.snapshot()

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Simulated SMS Worker Pipeline")
    
    parser.add_argument(
        "--messages", 
        type=int, 
        default=config.DEFAULT_MESSAGES, 
        help="Total number of messages to simulate"
    )
    parser.add_argument(
        "--senders", 
        type=int, 
        default=config.DEFAULT_SENDERS, 
        help="Number of concurrent sender threads"
    )
    parser.add_argument(
        "--mean-delay", 
        type=float, 
        default=config.DEFAULT_MEAN_DELAY, 
        help="Mean delay per message in seconds"
    )
    parser.add_argument(
        "--failure-rate", 
        type=float, 
        default=config.DEFAULT_FAILURE_RATE, 
        help="Probability of message failure (0.0 to 1.0)"
    )
    parser.add_argument(
        "--interval", 
        type=float, 
        default=config.DEFAULT_INTERVAL, 
        help="Monitor stats display interval in seconds"
    )
    parser.add_argument(
        "--queue-size", 
        type=int, 
        default=config.DEFAULT_QUEUE_SIZE, 
        help="Maximum capacity of the message queue"
    )
    parser.add_argument(
        "--max-length", 
        type=int, 
        default=config.DEFAULT_MAX_MESSAGE_LENGTH, 
        help="Maximum length of a generated message string"
    )
    parser.add_argument(
        "--seed", 
        type=int, 
        default=config.DEFAULT_SEED, 
        help="Random seed for reproducibility"
    )

    args = parser.parse_args(argv)

    try:
        return config.Config(
            messages=args.messages,
            senders=args.senders,
            mean_delay=args.mean_delay,
            failure_rate=args.failure_rate,
            interval=args.interval,
            queue_size=args.queue_size,
            max_message_length=args.max_length,
            seed=args.seed
        )
    except ValueError as e:
        parser.error(str(e))

def main(argv=None):
    simulation_config = parse_args(argv)

    print("Starting SMS Alert Pipeline...")

    results = run_simulation(simulation_config)

    print(
        f"Simulation complete. "
        f"Sent: {results['sent']}, "
        f"Failed: {results['failed']}"
    )


if __name__ == "__main__":
    main()