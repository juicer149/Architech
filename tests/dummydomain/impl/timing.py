import time

def micro_sleep(x, micros: int = 1000):
    # Sleep for a small amount to exercise measurement paths if enabled
    time.sleep(micros / 1_000_000.0)
    return x
