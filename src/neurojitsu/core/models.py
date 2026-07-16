"""Validated contracts shared across the NeuroJitsu pipeline."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SessionPhase(StrEnum):
    """Canonical phases of one adapted BJJ session."""

    WARM_UP = "warm_up"
    TECHNICAL_DRILLS = "technical_drills"
    COOPERATIVE_GAMES = "cooperative_games"
    COOL_DOWN = "cool_down"
    SENSORY_PAUSE = "sensory_pause"
    UNASSIGNED = "unassigned"


class IdentityStatus(StrEnum):
    """Confidence that a track is assigned to the intended participant."""

    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"


class DataUsability(StrEnum):
    """Whether a measurement may be used for analysis."""

    VALID = "valid"
    EXPLORATORY = "exploratory"
    INVALID = "invalid"


class MetricValue(BaseModel):
    """One numeric metric with explicit quality metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    value: float | None
    unit: str = Field(min_length=1, max_length=40)
    confidence: float = Field(ge=0.0, le=1.0)
    valid: bool
    reason_invalid: str | None = None

    @model_validator(mode="after")
    def validate_invalid_reason(self) -> MetricValue:
        """Require a reason whenever a metric is marked invalid."""
        if not self.valid and not self.reason_invalid:
            raise ValueError("reason_invalid is required when valid is false")
        return self


class SessionWindow(BaseModel):
    """Time-bounded analytic unit passed between services."""

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=3, max_length=80)
    participant_id: str = Field(pattern=r"^[A-Z][A-Z0-9_-]{2,31}$")
    timestamp_start: datetime
    timestamp_end: datetime
    phase: SessionPhase
    identity_status: IdentityStatus
    metrics: list[MetricValue] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_time_order(self) -> SessionWindow:
        """Prevent negative or zero-duration windows."""
        if self.timestamp_end <= self.timestamp_start:
            raise ValueError("timestamp_end must be after timestamp_start")
        return self


class PhaseBoundary(BaseModel):
    """Absolute phase boundary for a session."""

    phase: SessionPhase
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_boundary(self) -> PhaseBoundary:
        if self.end <= self.start:
            raise ValueError("phase end must be after start")
        return self


class PoseFrame(BaseModel):
    """Landmark-only representation of one redacted video frame."""

    session_id: str
    participant_id: str
    timestamp: datetime
    frame_index: int = Field(ge=0)
    landmarks_xyzc: list[tuple[float, float, float, float]]
    valid_landmark_ratio: float = Field(ge=0.0, le=1.0)
    tracking_confidence: float = Field(ge=0.0, le=1.0)
    identity_status: IdentityStatus = IdentityStatus.UNCERTAIN


class FeedbackRecord(BaseModel):
    """Post-session micro-feedback entered by a professional."""

    session_id: str
    participant_id: str
    engagement: str = Field(pattern=r"^(high|medium|low)$")
    sensory_overload: str = Field(pattern=r"^(none|mild|intense)$")
    recorded_at: datetime
    recorded_by_role: str = "researcher"
    notes: str | None = Field(default=None, max_length=2000)


class QualitySummary(BaseModel):
    """Summary of measurement quality for one session."""

    session_id: str
    participant_id: str
    overall: DataUsability
    valid_window_ratio: float = Field(ge=0.0, le=1.0)
    mean_confidence: float = Field(ge=0.0, le=1.0)
    identity_uncertain_seconds: float = Field(ge=0.0)
    limitations: list[str] = Field(default_factory=list)


class ReportPayload(BaseModel):
    """Strict source of truth for report rendering."""

    session_id: str
    participant_id: str
    generated_at: datetime
    quality: QualitySummary
    phase_metrics: dict[str, dict[str, float | int | str | None]]
    observations: list[str]
    limitations: list[str]
    professional_review_required: bool = True
