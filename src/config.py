from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "configs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    use_llm: bool = False
    database_path: str = "data/runtime/property_ops.db"

    @property
    def db_path(self) -> Path:
        p = Path(self.database_path)
        return p if p.is_absolute() else ROOT / p

    @property
    def llm_enabled(self) -> bool:
        return self.use_llm and bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_yaml(name: str) -> dict:
    path = CONFIG_DIR / name
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_app_config() -> dict:
    return load_yaml("settings.yaml")


def load_escalation_rules() -> dict:
    return load_yaml("escalation_rules.yaml")
