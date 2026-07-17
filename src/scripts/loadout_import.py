"""Phase: import a single loadout slot.

Runs once per loadout slot (9 times per champion, for every champion in the
run). Only the very first loadout-import of the ENTIRE run (the first
champion's first slot) types the source account name -- every other
loadout-import for the rest of the run (remaining slots of that champion,
and every slot of every later champion) just re-searches without retyping,
since the game keeps the searched name cached.

Coordinates recorded in recordings/subloadouts_first.json (7 clicks -- the
full sequence, used only for the very first loadout-import of the run):
  1. Import button          (616, 933)
  2. Search by Name         (955, 618)
  3. Search textbox         (765, 544)   -- skipped on every import after the first
  [type account_name here]                -- skipped on every import after the first
  4. Search button          (1137, 619)
  5. Pick user from results (749, 391)
  [long_load wait -- loadout menu appears, defaulted to loadout #1]
  [click "Next Loadout" 0..8 times -- see subloadouts_second.json]
  6. Import (finalize)      (839, 845)
  7. Save / overwrite       (854, 941)

Coordinates recorded in recordings/subloadouts_second.json:
  Next Loadout button -> (1030, 738), clicked N times where N is the
  0-based index of the loadout slot currently being imported (0 for the
  1st loadout, 1 for the 2nd, ... 8 for the 9th).
"""

from __future__ import annotations

from src.scripts.actions import CLICK_LOAD, SHORT_LOAD, MED_LOAD, LONG_LOAD, click, type_text, wait

CLEAR_ALL = (1079, 935)
IMPORT_BUTTON = (616, 933)
SEARCH_BY_NAME = (955, 618)
SEARCH_TEXTBOX = (765, 544)
SEARCH_CONFIRM = (1137, 619)
USER_RESULT = (749, 391)
FINALIZE_IMPORT = (839, 845)
SAVE_OVERWRITE = (854, 941)

NEXT_LOADOUT_BUTTON = (1030, 738)


def _search_account(account_name: str | None) -> None:
    """Search for the source account. If account_name is given, type it in
    first (the very first loadout-import of the run); otherwise just
    re-confirm the search with the name already cached from before."""
    click(*CLEAR_ALL, delay=CLICK_LOAD)
    click(*IMPORT_BUTTON, delay=CLICK_LOAD)
    click(*SEARCH_BY_NAME, delay=CLICK_LOAD)
    if account_name is not None:
        click(*SEARCH_TEXTBOX)
        type_text(account_name, delay=SHORT_LOAD)
    click(*SEARCH_CONFIRM, delay=MED_LOAD)
    click(*USER_RESULT, delay=CLICK_LOAD)
    wait(LONG_LOAD)

def _advance_to_loadout(slot_index: int) -> None:
    """Click "Next Loadout" slot_index times to reach the target slot
    (the menu always opens on loadout #1, i.e. slot_index 0)."""
    for _ in range(slot_index):
        click(*NEXT_LOADOUT_BUTTON, delay=CLICK_LOAD)


def import_loadout_slot(slot_index: int, account_name: str | None = None) -> None:
    """Import one loadout slot (0-based, 0..8).

    account_name: pass the source account name only for the very first
    loadout-import of the entire run (types it in); pass None for every
    other call so it just re-searches with the cached name.
    """
    _search_account(account_name)
    _advance_to_loadout(slot_index)
    click(*FINALIZE_IMPORT, delay=SHORT_LOAD)
    click(*SAVE_OVERWRITE, delay=SHORT_LOAD)
