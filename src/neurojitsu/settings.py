"""Configuration loading with environment overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class PhaseConfig(BaseModel):
    name: str
    start_minute: float = Field(ge=0)
    end_minute: float = Field(gt=0)


class Settings(BaseModel):
    """Application settings used by all processes."""

    project: dict[str, Any]
    runtime: dict[str, Any]
    session: dict[str, Any]
    quality: dict[str, Any]
    privacy: dict[str, Any]
    reports: dict[str, Any]
    config_path: Path
    db_path: Path
    db_key: str | None
    allow_unencrypted_synthetic_only: bool

    def phase_configs(self) -> list[PhaseConfig]:
        return [PhaseConfig.model_validate(item) for item in self.session["phases"]]


def _as_bool(value: str | bool | None, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(path: str | Path | None = None) -> Settings:
    """Load YAML configuration and security-relevant environment overrides."""
    raw_path: str | Path = path if path is not None else os.getenv(
        "NEUROJITSU_CONFIG", "config/settings.yaml"
    )
    config_path = Path(raw_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a mapping")

    return Settings(
        **raw,
        config_path=config_path,
        db_path=Path(os.getenv("NEUROJITSU_DB_PATH", "data/neurojitsu.db")),
        db_key=os.getenv("NEUROJITSU_DB_KEY") or None,
        allow_unencrypted_synthetic_only=_as_bool(
            os.getenv("NEUROJITSU_ALLOW_UNENCRYPTED_SYNTHETIC_ONLY"), True
        ),
    )
