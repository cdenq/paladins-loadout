"""Runtime toggle state for champions, kept separate from config.yml.

config.yml's `enabled` flag controls whether a champion CAN be toggled at
all (grey/locked vs. interactive). This module tracks whether an eligible
champion is currently toggled ON or OFF for the next run -- this state is
in-memory only and resets each session.
"""

from __future__ import annotations

from src.config import CLASS_ORDER, Champion, Config


class ToggleState:
    def __init__(self, config: Config):
        self.config = config
        # Only eligible (enabled) champions can be toggled; default them off.
        self._on: dict[str, bool] = {c.name: False for c in config.champions if c.enabled}

    def is_eligible(self, champ: Champion) -> bool:
        return champ.enabled

    def is_on(self, champ: Champion) -> bool:
        return self._on.get(champ.name, False)

    def toggle(self, champ: Champion) -> bool:
        """Flip a single champion's state. Returns the new state."""
        if not self.is_eligible(champ):
            return False
        new_state = not self._on.get(champ.name, False)
        self._on[champ.name] = new_state
        return new_state

    def set_all(self, on: bool) -> None:
        for name in self._on:
            self._on[name] = on

    def set_section(self, cls: str, on: bool) -> None:
        for champ in self.config.by_class(cls):
            if champ.name in self._on:
                self._on[champ.name] = on

    def selected_champions(self) -> list[Champion]:
        """All champions currently toggled on, ordered by CLASS_ORDER so each
        class's tab only needs to be clicked once during a run."""
        selected = [c for c in self.config.champions if self.is_on(c)]
        return sorted(selected, key=lambda c: CLASS_ORDER.index(c.cls))
