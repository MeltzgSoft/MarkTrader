import time


def safe_sleep(seconds: int) -> None:
    """a call to sleep that can be easily mocked"""
    time.sleep(seconds)
