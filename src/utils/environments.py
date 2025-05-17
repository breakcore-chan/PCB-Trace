from pathlib import Path

CONFIGS_DIR = Path("./data/configs").resolve()
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path("./data/plots").resolve()
PLOT_DIR.mkdir(parents=True, exist_ok=True)
