"""Low-level input primitives shared by every script phase.

Named delay tiers (short_load, med_load, long_load, click_load, special_load)
come from config.yml's `timings` section -- see src/config.py. Coordinates
recorded in recordings/*.json are for x/y positions only; their recorded
timestamps are NOT used for playback timing.

Coordinate space: pynput reports/uses positions in Windows' virtual-screen
space, where the PRIMARY monitor's top-left corner is always (0, 0) --
this holds regardless of how many monitors are connected or how they're
arranged. Since Paladins runs borderless-windowed on the primary monitor,
every recorded coordinate is already correct as-is; no per-monitor offset
is needed. (This would only break if a recording were made while the
mouse was actually over a *different* monitor than the game window.)
"""

from __future__ import annotations

import time

from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

from src.config import load_config
from src.interrupt import check as check_stop

_mouse = MouseController()
_keyboard = KeyboardController()

TIMINGS = load_config().timings

SHORT_LOAD = TIMINGS["short_load"]
MED_LOAD = TIMINGS["med_load"]
LONG_LOAD = TIMINGS["long_load"]
CLICK_LOAD = TIMINGS["click_load"]
SPECIAL_LOAD = TIMINGS["special_load"]


def click(x: int, y: int, button: Button = Button.left, delay: float = CLICK_LOAD) -> None:
    _mouse.position = (x, y)
    time.sleep(0.05)  # let the OS/game register the move before clicking
    _mouse.click(button)
    time.sleep(delay)


def type_text(text: str, delay: float = SPECIAL_LOAD, char_delay: float = 0.02) -> None:
    for char in text:
        _keyboard.type(char)
        time.sleep(char_delay)
    time.sleep(delay)


def press_key(key, delay: float = CLICK_LOAD) -> None:
    _keyboard.press(key)
    _keyboard.release(key)
    time.sleep(delay)


_STOP_POLL_INTERVAL = 0.1


def wait(seconds: float) -> None:
    """Sleep in small increments so a stop request during a long wait (e.g.
    LONG_LOAD) is noticed promptly instead of only after it fully elapses."""
    remaining = seconds
    while remaining > 0:
        check_stop()
        chunk = min(_STOP_POLL_INTERVAL, remaining)
        time.sleep(chunk)
        remaining -= chunk
    check_stop()
