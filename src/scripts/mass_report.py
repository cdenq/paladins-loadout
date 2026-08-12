"""Phase: mass report.

Reports the player sitting in a chosen scoreboard position (1-5). Like the
wipe phase this does no navigation -- it assumes the scoreboard is already
open on screen.

Coordinates recorded in recordings/mass report.json (4 clicks):
  1. Open the scoreboard entry   (784, 331)
  2. [the position right-click -- see below]
  3. Confirm report              (959, 837)
  4. Close                       (1808, 145)

The 2nd click in that recording landed on whichever position happened to be
under the cursor, so it isn't reusable as-is. It's replaced with the chosen
entry from recordings/mass report positions.json, which visits each of the 5
scoreboard rows in turn (recorded as right-clicks, but left-clicked here):
  1. (707, 634)   2. (705, 703)   3. (705, 765)
  4. (710, 828)   5. (707, 888)
"""

from __future__ import annotations

from src.scripts.actions import MED_LOAD, SHORT_LOAD, click

OPEN_ENTRY = (784, 331)
CONFIRM_REPORT = (959, 837)
CLOSE = (1808, 145)

# The 5 scoreboard rows, top to bottom. Right-clicked to open a player's menu.
REPORT_POSITIONS: list[tuple[int, int]] = [
    (707, 634),
    (705, 703),
    (705, 765),
    (710, 828),
    (707, 888),
]

NUM_POSITIONS = len(REPORT_POSITIONS)


def report_position(position: int) -> None:
    """Report the player in `position` (1-based, 1..5).

    Assumes the scoreboard is already open in-game.
    """
    if not 1 <= position <= NUM_POSITIONS:
        raise ValueError(f"position must be 1..{NUM_POSITIONS}, got {position}")

    click(*OPEN_ENTRY, delay=MED_LOAD)
    click(*REPORT_POSITIONS[position - 1], delay=SHORT_LOAD)
    click(*CONFIRM_REPORT, delay=SHORT_LOAD)
    click(*CLOSE, delay=SHORT_LOAD)
