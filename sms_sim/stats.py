import threading

class Stats:
    def __init__(self):
        self._sent = 0
        self._failed = 0
        self._total_elapsed = 0.0
        self._lock = threading.Lock()

    def record(self, success: bool, elapsed: float) -> None:
        with self._lock:
            if success:
                self._sent += 1
            else:
                self._failed += 1
            self._total_elapsed += elapsed

    def snapshot(self) -> dict:
        """
        Return a snapshot of the current statistics.
        """
        with self._lock:
            sent = self._sent
            failed = self._failed
            total_elapsed = self._total_elapsed
        attempts = sent + failed
        return {
                "sent": sent,
                "failed": failed,
                "avg_time": total_elapsed/attempts if attempts > 0 else 0.0,
            }