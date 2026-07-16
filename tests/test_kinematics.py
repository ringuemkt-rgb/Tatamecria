import pytest

from neurojitsu.analysis.kinematics import joint_angle, path_length, symmetry_difference_percent


def test_joint_angle_right_angle() -> None:
    assert joint_angle((1, 0), (0, 0), (0, 1)) == pytest.approx(90.0)


def test_symmetry_difference() -> None:
    assert symmetry_difference_percent(90, 110) == pytest.approx(20.0)


def test_path_length() -> None:
    assert path_length([(0, 0), (3, 4), (6, 8)]) == pytest.approx(10.0)
