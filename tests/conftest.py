from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import get_settings  # noqa: E402
from src.data.bundle import build_data_bundle  # noqa: E402
from src.data.seed import seed_database  # noqa: E402
from src.pipeline.run import CopilotPipeline  # noqa: E402


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    get_settings.cache_clear()

    bundle = build_data_bundle(use_cache=False)
    seed_database(bundle)

    p = CopilotPipeline()
    yield p
    p.close()
    get_settings.cache_clear()
