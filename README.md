<img src="assets/tofu.png" width="100">

# Tofu's Paladins Loadout Importer

Bulk Paladins loadout importer from a source account with GUI.

## Prerequisites

- Windows
- Paladins running in **borderless windowed mode** on your primary monitor

## Installation

### Download the app (easiest, no setup)

Download **`PaladinsLoadout.exe`** and double-click it. Nothing else to install —
no Python, no internet, no terminal. On first launch it creates a `config.yml`
next to the `.exe` that you can edit (champion roster, timings, username).

> On first run Windows may show a blue "Windows protected your PC" screen (the
> app isn't code-signed). Click **More info -> Run anyway**.

### run.bat (runs from source)

Double-click **`run.bat`**. It will install `uv` if you don't have it and then launch the app.

### Manual via CLI

Three ways to install: via `uv`, `conda`, `pip`.

```bash
# uv + gitbash (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh # if uv not installed
uv sync
uv run python main.py
```

```bash
# conda
conda create -n paladins-loadout python=3.13
conda activate paladins-loadout
pip install -e .
python main.py
```

```bash
# pip
python -m venv .venv
source .venv/Scripts/activate
pip install -e .
python main.py
```

## Usage

1. Be in the Paladins homescreen + configure settings in GUI.
2. Click "import" or hit F1.

## Building the .exe (for maintainers)

Double-click **`build.bat`** (needs `uv`). It syncs deps, generates the window
icon from `assets/tofu.png`, and produces a single-file `dist/PaladinsLoadout.exe`.
Ship that one file.

## Import messes up?
If imports mess up, then delay time between clicks is too short. Edit these in config.yml to be longer to ensure that menus load ingame before you click.