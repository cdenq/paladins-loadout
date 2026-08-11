"""Phase: wipe the currently-open loadout.

Unlike the import phase, this does NO navigation: it assumes the user has
already opened the loadout slot they want wiped. It clicks "Clear All",
places 5 fixed cards, and bumps their strengths -- nothing else.

Renaming and "Save and Exit" are deliberately left out: the "Change Loadout
Name" button moves around on screen, so it can't be hit by fixed
coordinates. The user finishes those steps by hand.

Coordinates recorded in recordings/import-cards.json (10 clicks, read as 5
pairs -- pick a card from the picker, then click the slot it goes into):
  (295, 494) -> (219, 354)
  (635, 454) -> (415, 330)
  (934, 434) -> (626, 332)
  (1301, 443) -> (814, 360)
  (1605, 483) -> (1082, 353)

Coordinates recorded in recordings/click-cards-up.json (3 clicks -- the
"increase strength" arrows), each clicked a fixed number of times.
"""

from __future__ import annotations

from src.scripts.actions import CLICK_LOAD, SHORT_LOAD, click
from src.scripts.loadout_import import clear_loadout

# 5 (card, destination slot) pairs, left to right.
CARD_PLACEMENTS: list[tuple[tuple[int, int], tuple[int, int]]] = [
    ((295, 494), (219, 354)),
    ((635, 454), (415, 330)),
    ((934, 434), (626, 332)),
    ((1301, 443), (814, 360)),
    ((1605, 483), (1082, 353)),
]

# "Increase card strength" arrows, paired with how many times each is clicked.
CARD_UPGRADES: list[tuple[tuple[int, int], int]] = [
    ((388, 741), 4),
    ((707, 723), 4),
    ((1016, 708), 2),
]


def _place_cards() -> None:
    """Pick each of the 5 cards and drop it into its slot."""
    for card, slot in CARD_PLACEMENTS:
        click(*card, delay=SHORT_LOAD)
        click(*slot, delay=SHORT_LOAD)


def _upgrade_cards() -> None:
    """Bump card strengths by clicking each arrow its fixed number of times."""
    for (x, y), times in CARD_UPGRADES:
        for _ in range(times):
            click(x, y, delay=CLICK_LOAD)


def build_wipe_loadout() -> None:
    """Clear the open loadout and rebuild it from the fixed card set.

    Assumes the target loadout slot is already open on screen. Leaves the
    loadout unsaved and unrenamed -- the user does that by hand.
    """
    clear_loadout()
    _place_cards()
    _upgrade_cards()
