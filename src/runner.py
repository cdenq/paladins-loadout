"""Orchestrates a full import run over whichever champions are toggled on.

Sequence: focus the Paladins window -> setup (if needed) -> for each
selected champion, route to its class menu (only re-routing when the
class changes) -> click the champion tile -> open the Loadouts tab -> for
each of the 9 loadout slots, click that slot's tile then run the import
dialog for it (Next Loadout clicked slot_index times, since the dialog
always resets to loadout #1). Only the very first loadout-import of the
ENTIRE run types the source account name -- every other loadout-import
just re-searches with the name already cached in-game.
"""

from __future__ import annotations

from typing import Callable

from src.config import Champion
from src.interrupt import check as check_stop
from src.scripts.loadout_import import import_loadout_slot
from src.scripts.loadout_menu import go_to_loadout_slot, go_to_loadouts_tab, finish_loadouts
from src.scripts.loadout_wipe import build_wipe_loadout
from src.scripts.mass_report import report_position
from src.scripts.setup import run_setup, click_champions
from src.scripts.traffic_director import go_to_champion, go_to_class
from src.state import ToggleState
from src.window import focus_paladins

NUM_LOADOUT_SLOTS = 9


def run_import(
    state: ToggleState,
    account_name: str,
    setup_needed: bool = True,
    on_progress: Callable[[Champion], None] | None = None,
    slot_indices: list[int] | None = None,
) -> None:
    """Run the full import sequence for all currently toggled-on champions.

    account_name: the source account's name, typed once for the very first
        loadout-import of the entire run only.
    setup_needed: whether to run the one-time in-game setup phase first
        (skip if you've already run it and just want to re-run imports).
    on_progress: optional callback invoked with each Champion as it's processed
        (useful for updating the GUI).
    slot_indices: which 0-based loadout slots (0..8) to import per champion.
        Defaults to all 9 slots in order. In "specific loadout" mode this is a
        chosen subset (e.g. [0, 2, 3, 4, 7] for loadouts 1, 3-5, 8).
    """
    champions = state.selected_champions()
    if not champions:
        return

    if slot_indices is None:
        slot_indices = list(range(NUM_LOADOUT_SLOTS))

    check_stop()
    focus_paladins()

    click_champions()
    if setup_needed:
        run_setup()

    # The account name is typed once, on the first loadout-import of a setup
    # run, then stays cached in-game. If setup is off it was already entered on
    # an earlier run, so skip typing and just re-search.
    is_first_loadout_of_run = setup_needed
    current_class = None
    for champ in champions:
        check_stop()

        if champ.cls != current_class:
            go_to_class(champ.cls)
            current_class = champ.cls

        go_to_champion(champ.cls, champ.name)
        go_to_loadouts_tab()

        for slot_index in slot_indices:
            check_stop()
            go_to_loadout_slot(slot_index)
            import_loadout_slot(
                slot_index,
                account_name=account_name if is_first_loadout_of_run else None,
            )
            is_first_loadout_of_run = False
        finish_loadouts()

        if on_progress:
            on_progress(champ)


def run_wipe() -> None:
    """Rebuild the loadout that's already open on screen.

    Unlike run_import this does no navigating and touches no champion
    selection: it assumes the user has already opened the loadout slot they
    want wiped, then clears it and lays down the fixed card set (see
    src/scripts/loadout_wipe.py). Saving and renaming are left to the user,
    since the "Change Loadout Name" button isn't at a fixed position.
    """
    check_stop()
    focus_paladins()
    build_wipe_loadout()


def run_mass_report(
    position: int,
    on_progress: Callable[[int], None] | None = None,
) -> None:
    """Repeatedly report the player in scoreboard `position` (1-based, 1..5).

    Loops until the interrupt key is pressed -- there's no natural stopping
    point, so the only exit is RunStopped raised out of a check_stop() (see
    src/interrupt.py). Like run_wipe it does no navigating: it assumes the
    scoreboard is already open in-game.

    on_progress: optional callback invoked with the completed pass count.
    """
    check_stop()
    focus_paladins()

    passes = 0
    while True:
        check_stop()
        report_position(position)
        passes += 1
        if on_progress:
            on_progress(passes)
