"""Runtime toggle state for champions, kept separate from config.yml.

config.yml's `enabled` flag controls whether a champion CAN be toggled at
all (grey/locked vs. interactive). This module tracks whether an eligible
champion is currently toggled ON or OFF for the next run -- this state is
in-memory only and resets each session.
"""

from __future__ import annotations

from src.config import CLASS_ORDER, Champion, Config


NUM_LOADOUT_SLOTS = 9


class ToggleState:
    def __init__(self, config: Config):
        self.config = config
        # Tracks every champion, since wipe mode can make config-disabled ones
        # selectable too; is_eligible() gates who may actually be toggled.
        self._on: dict[str, bool] = {c.name: False for c in config.champions}

        # "Specific loadout" mode: import a chosen subset of the 9 loadout slots
        # for a single champion, instead of all 9 for any number of champions.
        # `_slots` holds the 0-based slot indices to import.
        self.specific_mode: bool = False
        self._slots: set[int] = set()

        # "Loadout wipe" mode: the run wipes whichever loadout is already open
        # in-game instead of importing. It's purely a choice of action -- it
        # doesn't affect which champions are selectable.
        self.wipe_mode: bool = False

        # "Mass report" mode: the run reports the player in a chosen
        # scoreboard position instead of importing. Also purely a choice of
        # action; mutually exclusive with the other modes.
        self.report_mode: bool = False

    def is_eligible(self, champ: Champion) -> bool:
        return champ.enabled

    def is_on(self, champ: Champion) -> bool:
        return self._on.get(champ.name, False)

    def toggle(self, champ: Champion) -> bool:
        """Flip a single champion's state. Returns the new state.

        In specific-loadout mode, toggling a champion ON first clears any other
        selection, so only one champion is ever selected at a time.
        """
        if not self.is_eligible(champ):
            return False
        new_state = not self._on.get(champ.name, False)
        if self.specific_mode and new_state:
            for name in self._on:
                self._on[name] = False
        self._on[champ.name] = new_state
        return new_state

    def set_all(self, on: bool) -> None:
        for champ in self.config.champions:
            if self.is_eligible(champ):
                self._on[champ.name] = on

    def set_section(self, cls: str, on: bool) -> None:
        for champ in self.config.by_class(cls):
            if self.is_eligible(champ):
                self._on[champ.name] = on

    def selected_champions(self) -> list[Champion]:
        """All champions currently toggled on, ordered by CLASS_ORDER so each
        class's tab only needs to be clicked once during a run."""
        selected = [c for c in self.config.champions if self.is_eligible(c) and self.is_on(c)]
        return sorted(selected, key=lambda c: CLASS_ORDER.index(c.cls))

    # ---- specific-loadout mode --------------------------------------

    def set_specific_mode(self, on: bool) -> None:
        """Enter/leave specific-loadout mode. Entering the mode clears every
        champion selection (only one may be picked in this mode) and starts with
        all loadout slots deselected; leaving it keeps whatever single champion
        was selected."""
        self.specific_mode = on
        if on:
            self.set_all(False)
            self._slots.clear()

    # ---- loadout-wipe mode -------------------------------------------

    def set_wipe_mode(self, on: bool) -> None:
        """Enter/leave loadout-wipe mode. Champion selections are left alone --
        a wipe ignores them entirely, so toggling the mode shouldn't discard an
        import roster the user already picked."""
        self.wipe_mode = on

    # ---- mass-report mode --------------------------------------------

    def set_report_mode(self, on: bool) -> None:
        """Enter/leave mass-report mode. Like wipe mode this only changes what
        the run key does, so champion selections are left untouched."""
        self.report_mode = on

    def toggle_slot(self, slot_index: int) -> bool:
        """Flip a loadout slot (0-based) on/off for specific mode. Returns the
        new state."""
        if slot_index in self._slots:
            self._slots.discard(slot_index)
            return False
        self._slots.add(slot_index)
        return True

    def is_slot_on(self, slot_index: int) -> bool:
        return slot_index in self._slots

    def selected_slots(self) -> list[int]:
        """The chosen loadout slot indices (0-based), in ascending order."""
        return sorted(self._slots)
