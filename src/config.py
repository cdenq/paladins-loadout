"""Load and save config.yml: hotkey setting + champion roster by class."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def _app_dir() -> Path:
    """Directory the app runs from: the folder containing the .exe when frozen
    by PyInstaller, otherwise the project root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _bundled_default_config() -> Path:
    """The read-only config.yml packed inside the frozen bundle, used to seed an
    external one on first launch. Only meaningful when frozen."""
    base = getattr(sys, "_MEIPASS", None)
    if base is not None:
        return Path(base) / "config.yml"
    return Path(__file__).resolve().parent.parent / "config.yml"


# config.yml lives next to the .exe (or at the project root) so it stays
# user-editable and writable, rather than being baked into the frozen bundle.
CONFIG_PATH = _app_dir() / "config.yml"


def _ensure_config_exists(path: Path) -> None:
    """On a fresh install the external config.yml won't exist yet; copy the
    bundled default out next to the .exe so the user has an editable copy."""
    if path.exists():
        return
    default = _bundled_default_config()
    if default.exists() and default != path:
        path.write_text(default.read_text(encoding="utf-8"), encoding="utf-8")

# Also the in-game tab click order (see recordings/menu.json) and the order
# a run processes classes in, so a class's tab is only ever clicked once.
CLASS_ORDER = ["Damage", "Flank", "Frontline", "Support"]

DEFAULT_TIMINGS = {
    "short_load": 0.15,
    "med_load": 0.5,
    "long_load": 1.5,
    "click_load": 0.15,
    "special_load": 0.3,
}


@dataclass
class Champion:
    name: str
    cls: str
    enabled: bool  # whether this champion is eligible to be toggled at all


@dataclass
class Config:
    hotkey: str
    default_username: str = ""
    timings: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_TIMINGS))
    champions: list[Champion] = field(default_factory=list)

    def by_class(self, cls: str) -> list[Champion]:
        return [c for c in self.champions if c.cls == cls]


def load_config(path: Path = CONFIG_PATH) -> Config:
    _ensure_config_exists(path)
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    champions = []
    for cls, entries in raw.get("classes", {}).items():
        for entry in entries:
            champions.append(
                Champion(name=entry["name"], cls=cls, enabled=bool(entry.get("enabled", False)))
            )

    timings = dict(DEFAULT_TIMINGS)
    timings.update(raw.get("timings", {}))

    return Config(
        hotkey=raw.get("hotkey", "f1"),
        default_username=raw.get("default_username", ""),
        timings=timings,
        champions=champions,
    )


def save_config(config: Config, path: Path = CONFIG_PATH) -> None:
    classes: dict[str, list[dict]] = {cls: [] for cls in CLASS_ORDER}
    for champ in config.champions:
        classes.setdefault(champ.cls, []).append({"name": champ.name, "enabled": champ.enabled})

    raw = {
        "hotkey": config.hotkey,
        "default_username": config.default_username,
        "timings": config.timings,
        "classes": classes,
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(raw, f, sort_keys=False, allow_unicode=True)
