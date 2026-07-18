<img src="assets/tofu.png" width="100">

# Tofu's Paladins Loadout Importer

Bulk Paladins loadout importer from a source account with GUI.

## Prerequisites

- Windows
- Paladins running in **borderless windowed mode** on your primary monitor

The **`run.bat`** method below needs nothing else pre-installed. The manual CLI
methods additionally require Python 3.13+.

## Installation

### run.bat (easiest)

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

## Import messes up?
If imports mess up, then delay time between clicks is too short. Edit these in config.yml to be longer to ensure that menus load ingame before you click.