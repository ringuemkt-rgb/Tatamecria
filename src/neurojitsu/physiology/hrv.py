"""HRV processing with quality-first failure semantics."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class HrvResult:
    rmssd_ms: float | None
    sdnn_ms: float | None
    valid: bool
    quality_reason: str | None


def hrv_from_rr_intervals(rr_intervals_ms: Sequence[float]) -> HrvResult:
    """Calculate basic time-domain HRV from artifact-screened RR intervals.

    This function deliberately excludes LF/HF from the core dashboard.
    """
    rr = np.asarray(rr_intervals_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    if rr.size < 10:
        return HrvResult(None, None, False, "At least 10 valid RR intervals are required")
    if np.any((rr < 300) | (rr > 2000)):
        return HrvResult(None, None, False, "RR intervals failed the configured physiological range")

    differences = np.diff(rr)
    rmssd = float(np.sqrt(np.mean(differences**2)))
    sdnn = float(np.std(rr, ddof=1))
    return HrvResult(rmssd, sdnn, True, None)


def neurokit_hrv_from_ppg(ppg_signal: Sequence[float], sampling_rate: int) -> dict[str, float]:
    """Optional NeuroKit2 pipeline for controlled validation studies."""
    try:
        import neurokit2 as nk
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the physiology extra to use NeuroKit2") from exc

    cleaned = nk.ppg_clean(ppg_signal, sampling_rate=sampling_rate)
    peaks, info = nk.ppg_peaks(cleaned, sampling_rate=sampling_rate)
    quality = nk.ppg_quality(cleaned, sampling_rate=sampling_rate)
    if float(np.nanmean(quality)) < 0.5:
        raise ValueError("PPG signal quality was insufficient for HRV estimation")
    metrics = nk.hrv_time(peaks, sampling_rate=sampling_rate, show=False)
    return {
        "rmssd_ms": float(metrics.iloc[0]["HRV_RMSSD"]),
        "sdnn_ms": float(metrics.iloc[0]["HRV_SDNN"]),
        "mean_signal_quality": float(np.nanmean(quality)),
        "peak_count": float(len(info.get("PPG_Peaks", []))),
    }
