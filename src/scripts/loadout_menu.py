"""Phase: loadout menu navigation.

Runs once already inside a specific champion (after traffic_director has
clicked the class tab and the champion tile). go_to_loadouts_tab() opens
the Loadouts tab once per champion; go_to_loadout_slot(i) then selects
loadout slot i (0-based) for viewing/editing before the import dialog
(src/scripts/loadout_import.py) is opened on top of it -- the import
dialog always defaults back to loadout #1 internally regardless of which
slot tile was clicked here, which is why loadout_import separately clicks
"Next Loadout" i times once inside the dialog.

Coordinates recorded in recordings/loadouts.json:
  click 1     -> Loadouts tab
  clicks 2-10 -> loadout slots 1-9 (3x3 grid, reading order)
"""

from __future__ import annotations

from src.scripts.actions import SHORT_LOAD, MED_LOAD, click

LOADOUTS_TAB = (1156, 79)
BACK = (43, 46)

# 9 loadout slots, in reading order (left-to-right, top-to-bottom), from
# recordings/loadouts.json.
LOADOUT_SLOTS: list[tuple[int, int]] = [
    (537, 363), (968, 354), (1408, 362),
    (536, 604), (965, 602), (1415, 603),
    (519, 850), (962, 846), (1404, 848),
]


def go_to_loadouts_tab() -> None:
    click(*LOADOUTS_TAB, delay=SHORT_LOAD)  # loadout list re-renders


def go_to_loadout_slot(slot_index: int) -> None:
    """Click loadout slot slot_index (0-based, 0..8)."""
    if not 0 <= slot_index < len(LOADOUT_SLOTS):
        raise ValueError(f"slot_index must be 0..{len(LOADOUT_SLOTS) - 1}, got {slot_index}")
    click(*LOADOUT_SLOTS[slot_index], delay=SHORT_LOAD)

def finish_loadouts() -> None:
    """Click back out of loadouts."""
    click(*BACK, delay=MED_LOAD)