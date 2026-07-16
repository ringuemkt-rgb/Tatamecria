"""Deterministic enter, dwell, and exit events for tracked participants."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ZoneEventKind(StrEnum):
    """Canonical events emitted by the zone state machine."""

    ENTER = "enter"
    DWELL = "dwell"
    EXIT = "exit"


@dataclass(frozen=True, slots=True)
class ZoneEvent:
    """One auditable transition for a temporary visual track."""

    track_id: int
    zone_name: str
    kind: ZoneEventKind
    timestamp_ms: int
    dwell_ms: int = 0

    def __post_init__(self) -> None:
        if self.track_id < 0:
            raise ValueError("track_id must be non-negative")
        if not self.zone_name:
            raise ValueError("zone_name is required")
        if self.timestamp_ms < 0:
            raise ValueError("timestamp_ms must be non-negative")
        if self.dwell_ms < 0:
            raise ValueError("dwell_ms must be non-negative")


class ZoneEventEngine:
    """Convert per-frame zone membership into stable temporal events.

    The engine is independent of Supervision. A vision adapter may use
    ``sv.PolygonZone.trigger`` to produce ``{zone_name: {tracker_ids}}`` and then
    pass that mapping here. This separation keeps temporal logic deterministic,
    testable, and usable in synthetic research runs without OpenCV.
    """

    def __init__(self, dwell_threshold_ms: dict[str, int] | None = None) -> None:
        thresholds = dwell_threshold_ms or {}
        if any(value < 0 for value in thresholds.values()):
            raise ValueError("dwell thresholds must be non-negative")
        self._dwell_threshold_ms = dict(thresholds)
        self._inside: set[tuple[int, str]] = set()
        self._entered_at: dict[tuple[int, str], int] = {}
        self._dwell_emitted: set[tuple[int, str]] = set()

    def update(
        self,
        timestamp_ms: int,
        memberships: dict[str, set[int]],
    ) -> tuple[ZoneEvent, ...]:
        """Update state and return all transitions emitted at this timestamp."""

        if timestamp_ms < 0:
            raise ValueError("timestamp_ms must be non-negative")
        if any(track_id < 0 for track_ids in memberships.values() for track_id in track_ids):
            raise ValueError("track ids must be non-negative")

        current = {
            (track_id, zone_name)
            for zone_name, track_ids in memberships.items()
            for track_id in track_ids
        }
        entered = current - self._inside
        remained = current & self._inside
        exited = self._inside - current
        events: list[ZoneEvent] = []

        for pair in sorted(entered):
            track_id, zone_name = pair
            self._entered_at[pair] = timestamp_ms
            self._dwell_emitted.discard(pair)
            events.append(
                ZoneEvent(
                    track_id=track_id,
                    zone_name=zone_name,
                    kind=ZoneEventKind.ENTER,
                    timestamp_ms=timestamp_ms,
                )
            )

        for pair in sorted(remained):
            threshold = self._dwell_threshold_ms.get(pair[1], 0)
            entered_at = self._entered_at[pair]
            dwell_ms = timestamp_ms - entered_at
            if threshold > 0 and dwell_ms >= threshold and pair not in self._dwell_emitted:
                self._dwell_emitted.add(pair)
                events.append(
                    ZoneEvent(
                        track_id=pair[0],
                        zone_name=pair[1],
                        kind=ZoneEventKind.DWELL,
                        timestamp_ms=timestamp_ms,
                        dwell_ms=dwell_ms,
                    )
                )

        for pair in sorted(exited):
            entered_at = self._entered_at.pop(pair, timestamp_ms)
            dwell_ms = max(0, timestamp_ms - entered_at)
            self._dwell_emitted.discard(pair)
            events.append(
                ZoneEvent(
                    track_id=pair[0],
                    zone_name=pair[1],
                    kind=ZoneEventKind.EXIT,
                    timestamp_ms=timestamp_ms,
                    dwell_ms=dwell_ms,
                )
            )

        self._inside = current
        return tuple(events)

    def reset(self) -> None:
        """Clear state between sessions or camera sources."""

        self._inside.clear()
        self._entered_at.clear()
        self._dwell_emitted.clear()
