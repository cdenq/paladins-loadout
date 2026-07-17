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
from src.scripts.setup import run_setup
from src.scripts.traffic_director import go_to_champion, go_to_class
from src.state import ToggleState
from src.window import focus_paladins

NUM_LOADOUT_SLOTS = 9


def run_import(
    state: ToggleState,
    account_name: str,
    setup_needed: bool = True,
    on_progress: Callable[[Champion], None] | None = None,
) -> None:
    """Run the full import sequence for all currently toggled-on champions.

    account_name: the source account's name, typed once for the very first
        loadout-import of the entire run only.
    setup_needed: whether to run the one-time in-game setup phase first
        (skip if you've already run it and just want to re-run imports).
    on_progress: optional callback invoked with each Champion as it's processed
        (useful for updating the GUI).
    """
    champions = state.selected_champions()
    if not champions:
        return

    check_stop()
    focus_paladins()

    if setup_needed:
        run_setup()

    is_first_loadout_of_run = True
    current_class = None
    for champ in champions:
        check_stop()

        if champ.cls != current_class:
            go_to_class(champ.cls)
            current_class = champ.cls

        go_to_champion(champ.cls, champ.name)
        go_to_loadouts_tab()

        for slot_index in range(NUM_LOADOUT_SLOTS):
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
