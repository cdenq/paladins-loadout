"""Phase 1: setup.

Navigates to the right in-game menu and clicks whatever starting configs
are needed so every subsequent import runs from a standardized state.

Coordinates recorded in recordings/setup.json:
  1. click "Champions" selection
  2. click the "filter" box
  3. click the "by name" box
"""

from __future__ import annotations

from src.scripts.actions import CLICK_LOAD, SHORT_LOAD, click

CHAMPIONS_TAB = (177, 248)
FILTER_BOX = (661, 215)
BY_NAME_BOX = (644, 406)


def click_champions() -> None:
    """Open the Champions screen."""
    click(*CHAMPIONS_TAB, delay=SHORT_LOAD)

def run_setup() -> None:
    """Set the champion filter to search by name."""
    click(*FILTER_BOX, delay=CLICK_LOAD)
    click(*BY_NAME_BOX, delay=CLICK_LOAD)
