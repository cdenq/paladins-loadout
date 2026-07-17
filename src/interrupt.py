"""Cooperative stop signal for an in-progress import run.

The run happens on a background thread doing blocking clicks/sleeps, so it
can't be killed outright -- instead, request_stop() sets a flag that the
run checks between steps (see runner.py's per-champion loop and
actions.wait()) and unwinds via RunStopped as soon as it's next observed.
"""

from __future__ import annotations

import threading

_stop_event = threading.Event()


class RunStopped(Exception):
    """Raised to unwind out of an in-progress run once a stop was requested."""


def request_stop() -> None:
    _stop_event.set()


def reset() -> None:
    _stop_event.clear()


def is_stop_requested() -> bool:
    return _stop_event.is_set()


def check() -> None:
    """Raise RunStopped if a stop has been requested. Call this between
    discrete steps (e.g. per champion, per loadout slot, during long waits)."""
    if _stop_event.is_set():
        raise RunStopped()
