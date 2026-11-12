import math

# Default Constants
DEFAULT_MESSAGES = 1000
DEFAULT_SENDERS = 4
DEFAULT_MEAN_DELAY = 0.05
DEFAULT_FAILURE_RATE = 0.05
DEFAULT_INTERVAL = 0.5
DEFAULT_QUEUE_SIZE = 50
DEFAULT_MAX_MESSAGE_LENGTH = 100
DEFAULT_SEED = 42


class Config:
    def __init__(
        self,
        messages=DEFAULT_MESSAGES,
        senders=DEFAULT_SENDERS,
        mean_delay=DEFAULT_MEAN_DELAY,
        failure_rate=DEFAULT_FAILURE_RATE,
        interval=DEFAULT_INTERVAL,
        queue_size=DEFAULT_QUEUE_SIZE,
        max_message_length=DEFAULT_MAX_MESSAGE_LENGTH,
        seed=DEFAULT_SEED,
    ):
        self.messages = messages
        self.senders = senders
        self.mean_delay = mean_delay
        self.failure_rate = failure_rate
        self.interval = interval
        self.queue_size = queue_size
        self.max_message_length = max_message_length
        self.seed = seed

        # Validate upon initialization
        self.validate()

    def validate(self):
        """Validate configuration parameters, raising ValueError on failure."""
        if type(self.messages) is not int or self.messages < 0:
            raise ValueError("messages must be a non-negative integer (>= 0).")

        if type(self.senders) is not int or self.senders <= 0:
            raise ValueError("senders must be a positive integer (> 0).")

        if not isinstance(self.mean_delay, (int, float)) or not math.isfinite(self.mean_delay) or self.mean_delay <= 0:
            raise ValueError("mean_delay must be a finite positive number.")

        if not isinstance(self.failure_rate, (int, float)) or not math.isfinite(self.failure_rate) or not (0.0 <= self.failure_rate <= 1.0):
            raise ValueError("failure_rate must be between 0.0 and 1.0 inclusive.")

        if not isinstance(self.interval, (int, float)) or not math.isfinite(self.interval) or self.interval <= 0:
            raise ValueError("interval must be a finite positive number.")

        if type(self.queue_size) is not int or self.queue_size <= 0:
            raise ValueError("queue_size must be a positive integer (> 0).")

        if type(self.max_message_length) is not int or self.max_message_length <= 0:
            raise ValueError("max_message_length must be a positive integer (> 0).")

        if self.seed is not None and type(self.seed) is not int:
            raise ValueError("seed must be an integer or None.")