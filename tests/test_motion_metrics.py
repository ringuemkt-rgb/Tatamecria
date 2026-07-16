from math import isclose

from neurojitsu.biomechanics.motion_metrics import (
    bilateral_difference,
    joint_angle,
    path_length,
    range_of_motion,
)


def test_joint_angle_right_angle() -> None:
    result = joint_angle((1.0, 0.0), (0.0, 0.0), (0.0, 1.0))
    assert result.valid
    assert result.value is not None
    assert isclose(result.value, 90.0, abs_tol=1e-6)


def test_range_and_path_length() -> None:
    assert range_of_motion([10.0, 25.0, 15.0]).value == 15.0
    assert path_length([[0.0, 0.0], [3.0, 4.0]]).value == 5.0


def test_bilateral_difference_zero() -> None:
    assert bilateral_difference([1.0, 2.0], [1.0, 2.0]).value == 0.0
