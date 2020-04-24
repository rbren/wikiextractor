import signal
from contextlib import contextmanager
import time


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError as e:
        raise e
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


def sample_usage():
    # Add a timeout block.
    with timeout(1):
        print('entering block')
        time.sleep(3)
        print('This should never get printed because the line before timed out')

