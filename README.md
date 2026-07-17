<img src="assets/tofu.png" width="100">

# Tofu's Paladins Loadout Importer

Bulk Paladins loadout importer from a source account with GUI.

## Prerequisites

- Windows
- Python 3.13+
- Paladins running in **borderless windowed mode** on your primary monitor

## Installation

### uv (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh # if uv not installed
uv sync
```

Run with:

```bash
uv run python main.py
```

### pip

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e .
```

Then run:

```bash
python main.py
```

### conda

```bash
conda create -n paladins-loadout python=3.13
conda activate paladins-loadout
pip install -e .
```

Then run:

```bash
python main.py
```

## Usage

1. Be in the Paladins homescreen. Configure settings in GUI and hit F1.
2. Wait for things to load.
3. If imports mess up, then delay time between clicks is too short. Edit these in config.yml to be longer to ensure that menus load ingame before you click.