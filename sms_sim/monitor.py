def run_monitor(stats, interval, stop_event, output=print):
    """
    Monitor the statistics at regular intervals and output them.
    Accept an output function for testing purposes (default is print).
    """

    if interval <= 0:
        raise ValueError("interval must be a positive number")
    
    while not stop_event.wait(interval):
        snapshot = stats.snapshot()
        output(f"Sent: {snapshot['sent']}, Failed: {snapshot['failed']}, Avg Time: {snapshot['avg_time']:.4f} seconds")
    stats_snapshot = stats.snapshot()
    output(f"Final Stats - Sent: {stats_snapshot['sent']}, Failed: {stats_snapshot['failed']}, Avg Time: {stats_snapshot['avg_time']:.4f} seconds")