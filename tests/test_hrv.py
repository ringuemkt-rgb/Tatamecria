from neurojitsu.physiology.hrv import hrv_from_rr_intervals


def test_hrv_valid_intervals() -> None:
    result = hrv_from_rr_intervals([800, 810, 790, 805, 795, 800, 810, 790, 805, 795, 800])
    assert result.valid
    assert result.rmssd_ms is not None


def test_hrv_rejects_too_few_intervals() -> None:
    result = hrv_from_rr_intervals([800, 810, 790])
    assert not result.valid


def test_hrv_rejects_out_of_range_intervals() -> None:
    result = hrv_from_rr_intervals([800] * 10 + [250])
    assert not result.valid
