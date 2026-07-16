"""Experimental RuView/WiFi-CSI adapter kept outside the required core."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WifiSensingWindow(BaseModel):
    session_id: str
    sensor_cluster_id: str
    timestamp_start: datetime
    timestamp_end: datetime
    presence_detected: bool
    movement_index: float = Field(ge=0.0)
    signal_quality: float = Field(ge=0.0, le=1.0)
    breathing_rate_bpm: float | None = Field(default=None, ge=0.0)
    breathing_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    heart_rate_bpm: float | None = Field(default=None, ge=0.0)
    heart_rate_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    person_count_estimate: int | None = Field(default=None, ge=0)
    calibration_profile: str
    environment_profile: str
    usability: Literal["valid", "exploratory", "invalid"]
    invalid_reason: str | None = None


def parse_ruview_payload(payload: dict[str, object]) -> WifiSensingWindow:
    """Validate one RuView event and downgrade vitals when quality is insufficient."""
    window = WifiSensingWindow.model_validate(payload)
    if window.signal_quality < 0.70:
        window.breathing_rate_bpm = None
        window.breathing_confidence = None
        window.heart_rate_bpm = None
        window.heart_rate_confidence = None
        window.usability = "exploratory" if window.signal_quality >= 0.40 else "invalid"
        window.invalid_reason = "WiFi-CSI signal quality was insufficient for vital estimates"
    return window
