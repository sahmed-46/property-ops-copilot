from __future__ import annotations

from pathlib import Path

from src.config import get_settings
from src.data.bundle import build_data_bundle
from src.data.seed import seed_database


def ensure_database(*, sample_only: bool = True) -> Path:
    """Create SQLite from seed data when missing (e.g. Streamlit Cloud cold start)."""
    db_path = get_settings().db_path
    if db_path.exists():
        return db_path

    bundle = build_data_bundle(use_cache=not sample_only)
    seed_database(bundle)
    return db_path
