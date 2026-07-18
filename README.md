<img src="assets/tofu.png" width="100">

# Tofu's Paladins Loadout Importer

Bulk Paladins loadout importer from a source account with GUI. It'll automate your mouse clicks to import selected champion loadouts from a target account.

## Prerequisites

- Windows
- Monitor 1920x1080 resolution
- Paladins on primary monitor, at Home Screen

## Installation

### Easiest
Download **`PaladinsLoadout.exe`**; double-click to run, edit `config.yml` to change the timings.

> On first run Windows may show a blue "Windows protected your PC" screen (the
> app isn't code-signed). Click **More info -> Run anyway**.

### Manual

Use `run.bat`
> Double-click **`run.bat`**. It will install `uv` if you don't have it and then launch the app.

Use CLI: three ways to install: via `uv`, `conda`, `pip`.

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

1. Monitor resolution 1920x1080
2. Paladins fullscreen or borderless windowed
3. Paladins @ the home screen
2. Click "import" or hit F1 (default hotkey)

## Import messes up?
If imports mess up, then delay time between clicks is too short. Edit these in config.yml to be longer to ensure that menus load ingame before you click.