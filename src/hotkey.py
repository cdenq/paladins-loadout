"""Global hotkey listener, e.g. F1 anywhere triggers the Import action."""

from __future__ import annotations

from typing import Callable

from pynput import keyboard


def _normalize(hotkey: str) -> str:
    """Turn a config value like 'f1' into pynput GlobalHotKeys syntax '<f1>'."""
    hotkey = hotkey.strip().lower()
    if hotkey.startswith("<") and hotkey.endswith(">"):
        return hotkey
    return f"<{hotkey}>"


class GlobalHotkey:
    """Wraps pynput's GlobalHotKeys listener for a single trigger key."""

    def __init__(self, hotkey: str, on_trigger: Callable[[], None]):
        self.hotkey = hotkey
        self.on_trigger = on_trigger
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        combo = _normalize(self.hotkey)
        self._listener = keyboard.GlobalHotKeys({combo: self.on_trigger})
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def update_hotkey(self, hotkey: str) -> None:
        self.stop()
        self.hotkey = hotkey
        self.start()
