# SMS Alert Simulation

## Overview

This program simulates a concurrent, multithreaded SMS processing pipeline. A producer generates random messages up to a maximum length and pushes them into a bounded queue, creating backpressure that makes a fast producer wait when senders fall behind.

Multiple concurrent sender threads pull from this queue, simulate a randomized delay followed by a success or failure outcome based on a configurable failure rate, and record each result in a shared statistics object.

A monitor thread reads from that thread-safe statistics object to print periodic live updates at a configurable interval, concluding with a final summary of total sent and failed messages once everything is processed.

## How to Run

Requires **Python 3.13** (developed and tested on Python 3.13.2).

Run all commands from the project root, the folder containing `sms_sim/`.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The core simulation uses Python's standard library and does not require third-party packages.

### 4. Run the simulation with default settings

```bash
python -m sms_sim.main
```

### 5. Run with custom parameters

```bash
python -m sms_sim.main --messages 100 --senders 4 --mean-delay 0.05 --failure-rate 0.1 --seed 42
```

### Configuration Options

| Flag | Meaning | Default |
|---|---|---|
| `--messages` | Total messages to generate | 1000 |
| `--senders` | Number of sender threads | 4 |
| `--mean-delay` | Mean simulated send time (seconds) | 0.05 |
| `--failure-rate` | Probability a send fails (0 to 1) | 0.05 |
| `--interval` | Seconds between monitor updates | 0.5 |
| `--queue-size` | Maximum messages buffered in the queue | 50 |
| `--max-length` | Maximum generated message length | 100 |
| `--seed` | Seed for repeatable random sequences | None |

To view all available options:

```bash
python -m sms_sim.main --help
```

## How to Test

Run all tests:

```bash
python -m unittest discover -s tests -v
```

Run an individual test module:

```bash
python -m unittest tests.test_sender -v
```

Available test modules:

- `test_producer`
- `test_stats`
- `test_sender`
- `test_monitor`
- `test_config`
- `test_main`

The test suite includes unit tests for individual components, a concurrency test for the `Stats` lock, and integration tests for the complete pipeline.

Injectable dependencies, including the sleep function, random-number generators, and monitor output function, allow components to be tested quickly and with controlled behavior.

## Design

- **Producer:** Generates random messages and inserts them into the shared queue. It blocks when the queue is full, providing backpressure.
- **Senders:** Each sender repeatedly retrieves a message, sleeps for a randomized delay, determines success or failure based on the configured failure rate, records the result in `Stats`, and calls `task_done()` in a `finally` block.
- **Stats:** Stores sent counts, failed counts, and total elapsed processing time behind a single lock. The `snapshot()` method copies all values during one lock acquisition, ensuring the monitor receives a consistent view of the statistics.
- **Monitor:** Wakes every configured interval using `Event.wait(interval)` and prints a statistics snapshot. Setting the stop event wakes it immediately, avoiding unnecessary delays during shutdown. It prints a final summary before exiting.

### Processing Time Measurement

Processing time is measured using `time.perf_counter()`, a monotonic, high-resolution timer.

Timing begins when a sender starts processing a retrieved message and ends after the simulated send completes.

The average includes simulated sending delay and processing overhead but excludes time spent waiting in the queue.

The average is calculated as:

**Average processing time = Total elapsed processing time / Total completed messages**

If no messages have been processed, the average is reported as zero.

## Key Decisions

- **Threads:** Threads are appropriate because the simulated workload primarily involves I/O-style waiting. `time.sleep()` releases the GIL, allowing sender threads to make progress concurrently.
- **Bounded queue:** Python's `queue.Queue` is thread-safe, and limiting its capacity prevents the producer from buffering an unlimited number of messages when senders are slow.
- **One sentinel per sender:** After the producer finishes, the main thread inserts one `None` sentinel per sender. Each sender consumes a sentinel and exits, allowing clean shutdown without polling or timeouts.
- **Small critical section:** The statistics lock protects only counter and elapsed-time updates. Simulated sending delays occur outside the lock, allowing sender threads to run concurrently.
- **Injectable dependencies:** The sleep function, random-number generators, and output function can be supplied to individual components, making them easier to test.
- **Validation up front:** `Config` validates parameters before threads start. This avoids launching the simulation with invalid settings that could cause worker threads to fail.
- **Shutdown order:** The main thread joins the producer, enqueues the sentinels, joins the senders, sets the monitor stop event, and finally joins the monitor. During normal execution, this ensures all generated messages are processed before the final statistics are reported.

## Scaling to Production

This project is a single-process simulation. In a production system, I would consider the following improvements:

- **Message broker:** Replace the in-memory queue with Kafka, Amazon SQS, or RabbitMQ to support durable message storage and communication between separate services.
- **Horizontal scaling:** Run senders as independent workers that can scale according to workload.
- **Retries and dead-letter queues:** Introduce retries with exponential backoff for transient failures and a dead-letter queue for messages that repeatedly fail.
- **Rate limiting:** Respect the SMS provider's throughput limits to avoid rejected requests or service throttling.
- **Monitoring and alerting:** Replace console-based reporting with structured metrics, dashboards, and alerts.

Retries and dead-letter queue functionality were intentionally excluded from this version to keep the core concurrency implementation focused, correct, and explainable.

## Limitations and Trade-offs

- Failed sends are **counted and dropped**, without retries.
- `time.sleep()` is subject to operating-system scheduling and timer resolution, so very small delays may take longer than requested and affect the measured average processing time.
- The `--seed` option makes random sequences reproducible, but thread scheduling can affect how work is distributed among senders and the resulting success/failure totals.
- Graceful shutdown in response to **Ctrl+C** is not explicitly implemented.
- Simulated delays and failure probabilities do not represent the behavior of a real SMS provider.
- The current test suite does not include a dedicated unit test that independently exercises multiple sender threads. Adding one would be a useful future improvement.

## AI Usage

I used AI assistance throughout this project, primarily Claude, as a learning resource, design discussion partner, and code reviewer.

I spent several hours focusing on the system design before implementation because I wanted to understand the architecture and concurrency concepts thoroughly. My goal was to make the implementation smoother by understanding the design decisions and their trade-offs first.

- **Design and concepts:** Claude helped me explore architectural decisions, scalability considerations, and trade-offs. We discussed threading, the GIL, locks, bounded queues, and graceful shutdown using sentinels.
- **Debugging and corrections:** I used AI to troubleshoot issues, understand unexpected behavior, and identify syntax or implementation mistakes when I got stuck.
- **Testing:** AI helped me identify additional edge cases, improve test coverage, and refine tests that needed revision.
- **Code review:** I used Claude as a senior-engineer-style reviewer to evaluate my implementation, discuss potential weaknesses, and identify improvements before submission.

Throughout the project, my focus was on understanding the system, implementing its components, and being able to explain the reasoning behind my design decisions.