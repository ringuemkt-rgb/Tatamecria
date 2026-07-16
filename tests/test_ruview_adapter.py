from datetime import UTC, datetime, timedelta

from neurojitsu.wifi.ruview_adapter import parse_ruview_payload


def _payload(quality: float) -> dict[str, object]:
    start = datetime(2026, 7, 16, tzinfo=UTC)
    return {
        "session_id": "NJ-1",
        "sensor_cluster_id": "RF-1",
        "timestamp_start": start,
        "timestamp_end": start + timedelta(seconds=10),
        "presence_detected": True,
        "movement_index": 0.4,
        "signal_quality": quality,
        "breathing_rate_bpm": 18.0,
        "breathing_confidence": 0.8,
        "heart_rate_bpm": 90.0,
        "heart_rate_confidence": 0.7,
        "person_count_estimate": 1,
        "calibration_profile": "room-a-v1",
        "environment_profile": "room-a",
        "usability": "valid",
    }


def test_low_quality_removes_vitals() -> None:
    result = parse_ruview_payload(_payload(0.3))
    assert result.usability == "invalid"
    assert result.heart_rate_bpm is None


def test_high_quality_preserves_vitals() -> None:
    result = parse_ruview_payload(_payload(0.9))
    assert result.usability == "valid"
    assert result.heart_rate_bpm == 90.0
