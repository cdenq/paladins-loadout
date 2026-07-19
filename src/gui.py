"""Tkinter GUI with two pages: a tutorial/requirements page shown on launch,
and the main page -- a menu of toggleable champion buttons grouped by class
plus an Import button (also triggerable via a global hotkey).

Button colors:
  - light green: eligible and toggled ON
  - light red:   eligible and toggled OFF
  - light gray:  not eligible (config.yml enabled: false) -- not clickable
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from src.config import CLASS_ORDER, Config, load_config, save_config
from src.hotkey import GlobalHotkey
from src.interrupt import RunStopped
from src.interrupt import reset as reset_stop
from src.interrupt import request_stop
from src.runner import run_import
from src.state import NUM_LOADOUT_SLOTS, ToggleState

COLOR_ON = "#a6e3a1"
COLOR_OFF = "#f2a6a6"
COLOR_DISABLED = "#d3d3d3"


def _resource_dir() -> Path:
    """Directory bundled read-only assets live in: PyInstaller's extraction
    dir when frozen, otherwise the project root."""
    base = getattr(sys, "_MEIPASS", None)
    if base is not None:
        return Path(base)
    return Path(__file__).resolve().parent.parent


LOGO_PATH = _resource_dir() / "assets" / "tofu.png"
TUTORIAL_IMAGE_PATH = _resource_dir() / "assets" / "image.png"

# When True, Import prints "clicked" instead of driving the game window.
DEV_MODE = False


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Paladins Loadout Importer")

        self.config: Config = load_config()
        self.state = ToggleState(self.config)

        self._buttons: dict[str, tk.Button] = {}
        self._running = False

        # Two pages live under root; only one is packed at a time (see
        # _show_tutorial / _show_main). The tutorial shows on launch unless the
        # user previously ticked "never show again".
        self.tutorial_page = tk.Frame(self.root)
        self.main_page = tk.Frame(self.root)
        self._build_tutorial_page(self.tutorial_page)
        self._build_main_page(self.main_page)

        if self.config.skip_tutorial:
            self._show_main()
        else:
            self._show_tutorial()

        self.hotkey = GlobalHotkey(self.config.hotkey, self._handle_hotkey_threadsafe)
        self.hotkey.start()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---- page switching --------------------------------------------

    def _show_tutorial(self) -> None:
        self.main_page.pack_forget()
        self.tutorial_page.pack(fill="both", expand=True)

    def _show_main(self) -> None:
        self.tutorial_page.pack_forget()
        self.main_page.pack(fill="both", expand=True)

    # ---- tutorial page ---------------------------------------------

    def _build_tutorial_page(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent)
        header.pack(fill="x", padx=12, pady=(12, 4))
        self._load_logo(header)
        tk.Label(
            header, text="Setup & Requirements", font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=(4, 0))

        steps = tk.Label(
            parent,
            justify="left",
            anchor="w",
            font=("Segoe UI", 10),
            text=(
                "Before importing, make sure:\n\n"
                "  1. Paladins is launched and sitting on the HOME screen (Champions selection is visible; shown below).\n\n"
                "  2. Your display resolution is 1920 x 1080. Change this in Paladins Settings.\n\n"
                "  3. The display mode is Fullscreen, OR Borderless Window with the\n"
                "     window sized to fill the whole screen."
            ),
        )
        steps.pack(fill="x", padx=16, pady=(4, 8))

        self._load_tutorial_image(parent)

        controls = tk.Frame(parent)
        controls.pack(fill="x", padx=12, pady=12)
        tk.Button(
            controls,
            text="Never show again",
            command=self._tutorial_never_show_again,
        ).pack(side="left")
        tk.Button(
            controls,
            text="Got it",
            bg=COLOR_ON,
            font=("Segoe UI", 10, "bold"),
            command=self._show_main,
        ).pack(side="right")

    def _load_tutorial_image(self, parent: tk.Widget) -> None:
        """Show assets/image.png (the Paladins home screen) on the tutorial
        page, scaled to fit. Skips silently if missing/unreadable."""
        try:
            img = tk.PhotoImage(file=str(TUTORIAL_IMAGE_PATH))
        except Exception:
            return
        # Scale down to ~560px wide so it fits the window. Integer subsample.
        factor = max(1, img.width() // 560)
        self._tutorial_image = img.subsample(factor, factor)  # keep a ref
        tk.Label(parent, image=self._tutorial_image).pack(padx=12, pady=(0, 8))

    def _tutorial_never_show_again(self) -> None:
        self.config.skip_tutorial = True
        try:
            save_config(self.config)
        except Exception as exc:  # don't block the app if the write fails
            print(f"Could not save skip_tutorial preference: {exc}")
        self._show_main()

    # ---- main page -------------------------------------------------

    def _build_main_page(self, parent: tk.Frame) -> None:
        top = tk.Frame(parent)
        top.pack(fill="x", padx=8, pady=(8, 4))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)

        left = tk.Frame(top)
        left.grid(row=0, column=0, sticky="nw", padx=(0, 4))
        right = tk.Frame(top)
        right.grid(row=0, column=1, sticky="nw", padx=(4, 0))

        self._load_logo(left)

        account_row = tk.Frame(left)
        account_row.pack(fill="x", pady=(6, 0))
        tk.Label(account_row, text="Source Username:").pack(side="left")
        self.account_var = tk.StringVar(value=self.config.default_username)
        tk.Entry(account_row, textvariable=self.account_var, width=24).pack(side="left", padx=(4, 0))

        global_controls = tk.Frame(left)
        global_controls.pack(fill="x", pady=(6, 0))
        tk.Button(global_controls, text="Toggle All On", command=lambda: self._set_all(True)).pack(side="left")
        tk.Button(global_controls, text="Toggle All Off", command=lambda: self._set_all(False)).pack(side="left", padx=(4, 0))

        # Shown only in specific-loadout mode; empty (hidden) otherwise.
        self.banner_var = tk.StringVar(value="")
        self.banner_label = tk.Label(
            right,
            textvariable=self.banner_var,
            fg="#b45309",
            font=("Segoe UI", 9, "bold"),
            wraplength=380,
            justify="left",
        )
        self.banner_label.pack(fill="x", pady=(0, 2))

        # When on, only one champion may be selected and only the chosen
        # loadout slots (below) are imported.
        self.specific_mode_button = tk.Button(
            right,
            text="Specific Loadouts Only: OFF",
            bg=COLOR_OFF,
            command=self._toggle_specific_mode,
        )
        self.specific_mode_button.pack(fill="x", pady=(0, 4))

        # 3x3 grid of loadout-slot chips (1-3 / 4-6 / 7-9). The inner frame
        # keeps the grid centered under the toggle rather than left-aligned.
        self.slots_frame = tk.Frame(right)
        self.slots_frame.pack(fill="x", pady=(0, 4))
        slots_grid = tk.Frame(self.slots_frame)
        slots_grid.pack(anchor="center")
        slot_columns = 3
        self._slot_buttons: list[tk.Button] = []
        for slot_index in range(NUM_LOADOUT_SLOTS):
            btn = tk.Button(
                slots_grid,
                text=str(slot_index + 1),
                width=3,
                command=lambda i=slot_index: self._toggle_slot(i),
            )
            btn.grid(
                row=slot_index // slot_columns,
                column=slot_index % slot_columns,
                padx=1,
                pady=1,
            )
            self._slot_buttons.append(btn)
        self._refresh_slots()

        classes_frame = tk.Frame(parent)
        classes_frame.pack(fill="both", expand=True, padx=8, pady=4)
        columns = 2
        for col in range(columns):
            classes_frame.columnconfigure(col, weight=1)

        for i, cls in enumerate(CLASS_ORDER):
            self._build_class_section(classes_frame, cls, row=i // columns, column=i % columns)

        run_frame = tk.Frame(parent)
        run_frame.pack(fill="x", padx=8, pady=8)

        tk.Button(
            run_frame,
            text="How to setup?",
            command=self._show_tutorial,
        ).pack(fill="x", pady=(0, 4))

        # "Setup Needed" toggle: on (default) runs the one-time in-game
        # setup phase before importing; off skips straight to imports.
        self.setup_needed = True
        self.setup_needed_button = tk.Button(
            run_frame,
            text="First time running THIS SESSION: Yes",
            bg=COLOR_ON,
            command=self._toggle_setup_needed,
        )
        self.setup_needed_button.pack(fill="x", pady=(0, 4))

        self.import_button = tk.Button(
            run_frame,
            text=f"Import ({self.config.hotkey.upper()})",
            bg="#89b4fa",
            font=("Segoe UI", 12, "bold"),
            command=self._handle_hotkey_threadsafe,
        )
        self.import_button.pack(fill="x")

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(parent, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(0, 8))

    def _load_logo(self, parent: tk.Widget) -> None:
        """Show assets/tofu.png as a logo in the top bar and as the window icon.
        Skips silently if the file is missing or unreadable."""
        try:
            img = tk.PhotoImage(file=str(LOGO_PATH))
        except Exception:
            return

        # Shrink to ~70px wide. subsample divides by an integer factor.
        factor = max(1, img.width() // 70)
        self._logo_image = img.subsample(factor, factor)  # keep a ref so Tk doesn't GC it
        tk.Label(parent, image=self._logo_image).pack(side="left", padx=(0, 8))

        try:
            self.root.iconphoto(True, self._logo_image)
        except Exception:
            pass

    def _build_class_section(self, parent: tk.Widget, cls: str, row: int, column: int) -> None:
        section = tk.LabelFrame(parent, text=cls, padx=6, pady=6)
        section.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")

        section_controls = tk.Frame(section)
        section_controls.pack(fill="x", pady=(0, 4))
        tk.Button(section_controls, text="Section On", command=lambda: self._set_section(cls, True)).pack(side="left")
        tk.Button(section_controls, text="Section Off", command=lambda: self._set_section(cls, False)).pack(side="left", padx=(4, 0))

        grid = tk.Frame(section)
        grid.pack(fill="x")

        champs = self.config.by_class(cls)
        columns = 3
        for i, champ in enumerate(champs):
            btn = tk.Button(grid, text=champ.name, width=16)
            if champ.enabled:
                btn.configure(command=lambda c=champ: self._toggle(c))
            self._buttons[champ.name] = btn
            btn.grid(row=i // columns, column=i % columns, padx=2, pady=2)

        self._refresh_class(cls)

    # ---- button state ----------------------------------------------

    def _refresh_class(self, cls: str) -> None:
        for champ in self.config.by_class(cls):
            self._refresh_button(champ.name)

    def _refresh_all(self) -> None:
        for name in self._buttons:
            self._refresh_button(name)

    def _refresh_button(self, name: str) -> None:
        champ = next(c for c in self.config.champions if c.name == name)
        btn = self._buttons[name]
        if not champ.enabled:
            btn.configure(bg=COLOR_DISABLED, state="disabled")
        else:
            btn.configure(state="normal")
            btn.configure(bg=COLOR_ON if self.state.is_on(champ) else COLOR_OFF)

    def _toggle(self, champ) -> None:
        self.state.toggle(champ)
        # In specific mode, selecting a champion deselects any previous one, so
        # refresh every button rather than just the one clicked.
        if self.state.specific_mode:
            self._refresh_all()
        else:
            self._refresh_button(champ.name)

    def _set_all(self, on: bool) -> None:
        self.state.set_all(on)
        self._refresh_all()

    def _set_section(self, cls: str, on: bool) -> None:
        self.state.set_section(cls, on)
        self._refresh_class(cls)

    def _set_setup_needed(self, on: bool) -> None:
        self.setup_needed = on
        if on:
            self.setup_needed_button.configure(text="First time running THIS SESSION: Yes", bg=COLOR_ON)
        else:
            self.setup_needed_button.configure(text="First time running THIS SESSION: No", bg=COLOR_OFF)

    def _toggle_setup_needed(self) -> None:
        self._set_setup_needed(not self.setup_needed)

    def _toggle_specific_mode(self) -> None:
        on = not self.state.specific_mode
        # Entering the mode clears all champion selections (only one allowed).
        self.state.set_specific_mode(on)
        if on:
            self.specific_mode_button.configure(text="Specific Loadouts Only: ON", bg=COLOR_ON)
            self.banner_var.set(
                "For this mode, only ONE champion can be imported at a time."
            )
        else:
            self.specific_mode_button.configure(text="Specific Loadouts Only: OFF", bg=COLOR_OFF)
            self.banner_var.set("")
        self._refresh_all()
        self._refresh_slots()

    def _toggle_slot(self, slot_index: int) -> None:
        self.state.toggle_slot(slot_index)
        self._refresh_slots()

    def _refresh_slots(self) -> None:
        """Color the 9 slot chips; disable them entirely outside specific mode."""
        enabled = self.state.specific_mode
        for slot_index, btn in enumerate(self._slot_buttons):
            if not enabled:
                btn.configure(state="disabled", bg=COLOR_DISABLED)
            else:
                btn.configure(state="normal")
                btn.configure(bg=COLOR_ON if self.state.is_slot_on(slot_index) else COLOR_OFF)

    # ---- import run --------------------------------------------------

    def _handle_hotkey_threadsafe(self) -> None:
        # Hotkey fires on pynput's listener thread; hop back to the Tk
        # main thread before touching any widgets. F1 (or the button)
        # starts a run when idle, or requests a stop when one is running.
        self.root.after(0, self._handle_hotkey)

    def _handle_hotkey(self) -> None:
        if self._running:
            self._stop_import()
        else:
            self._start_import()

    def _start_import(self) -> None:
        if DEV_MODE:
            print("clicked")
            return

        selected = self.state.selected_champions()
        if not selected:
            messagebox.showinfo("Nothing to import", "No champions are toggled on.")
            return
        if not self.account_var.get().strip():
            messagebox.showwarning("Missing account name", "Enter the source account name first.")
            return

        # In specific mode, run only the chosen loadout slots (default: all 9).
        slot_indices = self.state.selected_slots() if self.state.specific_mode else None
        if self.state.specific_mode and not slot_indices:
            messagebox.showwarning("No loadouts selected", "Pick at least one loadout slot to import.")
            return

        reset_stop()
        self._running = True
        self.import_button.configure(text=f"Stop ({self.config.hotkey.upper()})", bg=COLOR_OFF)
        self.status_var.set(f"Importing 0/{len(selected)}...")

        thread = threading.Thread(
            target=self._run_import_worker, args=(selected, slot_indices), daemon=True
        )
        thread.start()

    def _stop_import(self) -> None:
        self.status_var.set("Stopping...")
        request_stop()

    def _run_import_worker(self, selected, slot_indices=None) -> None:
        account_name = self.account_var.get().strip()
        total = len(selected)
        count = {"done": 0}

        def on_progress(champ):
            count["done"] += 1
            print(f"Imported {champ.name}.")
            self.root.after(0, lambda: self.status_var.set(f"Importing {count['done']}/{total}... ({champ.name})"))

        try:
            run_import(
                self.state,
                account_name,
                setup_needed=self.setup_needed,
                on_progress=on_progress,
                slot_indices=slot_indices,
            )
            print(f"Done. Imported {total} champion(s).")
            self.root.after(0, lambda: self.status_var.set(f"Done. Imported {total} champion(s)."))
        except RunStopped:
            self.root.after(0, lambda: self.status_var.set(f"Stopped after {count['done']}/{total}."))
        except Exception as exc:  # surface script errors instead of failing silently
            self.root.after(0, lambda: self.status_var.set(f"Error: {exc}"))
        finally:
            self.root.after(0, self._finish_import)

    def _finish_import(self) -> None:
        self._running = False
        self.import_button.configure(text=f"Import ({self.config.hotkey.upper()})", bg="#89b4fa")
        # Setup runs once per session, so turn it off after the first run.
        if self.setup_needed:
            self._set_setup_needed(False)

    # ---- lifecycle ---------------------------------------------------

    def _on_close(self) -> None:
        self.hotkey.stop()
        self.root.destroy()


def launch() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()
