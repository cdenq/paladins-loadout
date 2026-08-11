"""Low-level input primitives shared by every script phase.

Named delay tiers (short_load, med_load, long_load, click_load, special_load)
come from config.yml's `timings` section. Coordinates are in Windows'
virtual-screen space, where the primary monitor's top-left is (0, 0); since
Paladins runs borderless-windowed on the primary monitor, recorded
coordinates are correct as-is with no per-monitor offset.
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


_STOP_POLL_INTERVAL = 0.05


def _sleep(seconds: float) -> None:
    """Sleep in small increments, raising RunStopped promptly if a stop is
    requested partway through. Every post-action delay goes through here so a
    stop interrupts almost immediately rather than at the next step boundary."""
    check_stop()
    remaining = seconds
    while remaining > 0:
        chunk = min(_STOP_POLL_INTERVAL, remaining)
        time.sleep(chunk)
        remaining -= chunk
        check_stop()


def click(x: int, y: int, button: Button = Button.left, delay: float = CLICK_LOAD) -> None:
    check_stop()  # don't even move the mouse if a stop is already pending
    _mouse.position = (x, y)
    _sleep(0.05)  # let the OS/game register the move before clicking
    _mouse.click(button)
    _sleep(delay)


def type_text(text: str, delay: float = SPECIAL_LOAD, char_delay: float = 0.02) -> None:
    for char in text:
        _keyboard.type(char)
        _sleep(char_delay)
    _sleep(delay)


def press_key(key, delay: float = CLICK_LOAD) -> None:
    check_stop()
    _keyboard.press(key)
    _keyboard.release(key)
    _sleep(delay)


def hold_key(key, duration: float, delay: float = CLICK_LOAD) -> None:
    """Hold a key down for `duration` seconds.

    Note this only produces ONE keystroke in games that read raw key state
    instead of the OS's auto-repeat (Paladins among them) -- use tap_key()
    when you need N discrete presses, e.g. clearing a text field.
    """
    check_stop()
    _keyboard.press(key)
    try:
        _sleep(duration)
    finally:
        # Release even if a stop unwinds mid-hold, so the key isn't left stuck.
        _keyboard.release(key)
    _sleep(delay)


def tap_key(key, times: int, interval: float = 0.03, delay: float = CLICK_LOAD) -> None:
    """Press and release a key `times` times, as discrete keystrokes.

    Preferred over hold_key() for repeat input: the game registers each
    press/release pair, whereas a held key relies on OS auto-repeat that
    Paladins ignores.
    """
    for _ in range(times):
        check_stop()
        _keyboard.press(key)
        _sleep(interval)
        _keyboard.release(key)
        _sleep(interval)
    _sleep(delay)


def wait(seconds: float) -> None:
    """Sleep in small increments so a stop request during a long wait (e.g.
    LONG_LOAD) is noticed promptly instead of only after it fully elapses."""
    _sleep(seconds)
