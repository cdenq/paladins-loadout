"""Phase 2: traffic director.

Given a target class (Frontline / Damage / Flank / Support), clicks that
class's tab so only its champions are displayed, then can click a specific
champion's tile within that class's grid. Since the 4 classes live at
different tab positions, this is the single place that knows how to route
to each one -- import scripts assume they start here.

Coordinates recorded in recordings/menu.json (one click per class tab):
  click 1 -> Damage tab
  click 2 -> Flank tab
  click 3 -> Frontline tab
  click 4 -> Support tab

Coordinates recorded in recordings/champions.json: 19 click slots (a
class's champion grid, in reading order) covering the max possible roster
size for any one class. A champion's slot is its position (1-based) within
its class's full roster as listed in config.yml -- NOT its position among
currently-selected champions. Classes with fewer than 19 champions simply
never reach the later slots.
"""

from __future__ import annotations

from src.config import load_config
from src.scripts.actions import SHORT_LOAD, MED_LOAD, click

_CLASS_TAB: dict[str, tuple[int, int]] = {
    "Damage": (182, 211),
    "Flank": (252, 209),
    "Frontline": (322, 210),
    "Support": (398, 210),
}

# 19 champion-tile slots, in reading order (left-to-right, top-to-bottom),
# from recordings/champions.json.
_CHAMPION_SLOTS: list[tuple[int, int]] = [
    (125, 304), (228, 302), (341, 303), (445, 303), (554, 302), (670, 310), (776, 305), (894, 302),
    (115, 419), (234, 424), (337, 421), (447, 422), (564, 421), (669, 420), (774, 426), (887, 426),
    (117, 542), (228, 544), (337, 539),
]


def go_to_class(cls: str) -> None:
    coords = _CLASS_TAB.get(cls)
    if coords is None:
        raise ValueError(f"Unknown class: {cls}")
    click(*coords, delay=SHORT_LOAD)  # champion grid re-renders for the new class


def _champion_slot_index(cls: str, champion_name: str) -> int:
    """0-based slot index for champion_name within cls's full config.yml roster."""
    roster = [c.name for c in load_config().by_class(cls)]
    try:
        return roster.index(champion_name)
    except ValueError:
        raise ValueError(f"'{champion_name}' is not listed under class '{cls}' in config.yml")


def go_to_champion(cls: str, champion_name: str) -> None:
    """Click a specific champion's tile within an already-routed class menu."""
    index = _champion_slot_index(cls, champion_name)
    if index >= len(_CHAMPION_SLOTS):
        raise ValueError(
            f"'{champion_name}' is slot {index + 1} in class '{cls}', "
            f"but only {len(_CHAMPION_SLOTS)} champion slots are recorded"
        )
    click(*_CHAMPION_SLOTS[index], delay=MED_LOAD)  # champion screen loads after selection
