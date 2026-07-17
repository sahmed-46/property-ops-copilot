from __future__ import annotations

from pathlib import Path

from src.config import ROOT, load_yaml

CACHE_DIR = ROOT / "data" / "cache"
SAMPLE_DIR = ROOT / "data" / "sample"
SAMPLE_SEED_PATH = SAMPLE_DIR / "seed.json"
RESIDENTIAL_CLAUSES_PATH = SAMPLE_DIR / "residential_clauses.json"


def datasets_config() -> dict:
    return load_yaml("datasets.yaml")


def cache_dir() -> Path:
    cfg = datasets_config()
    path = Path(cfg.get("cache_dir", "data/cache"))
    return path if path.is_absolute() else ROOT / path
