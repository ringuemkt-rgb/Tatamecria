from neurojitsu.analysis.motion_quality import MotionQualityInput, assess_motion_quality


def test_good_body_data_is_reportable() -> None:
    result = assess_motion_quality(
        MotionQualityInput(
            body_valid_ratio=0.92,
            hand_valid_ratio=0.80,
            foot_valid_ratio=0.85,
            detector_confidence=0.94,
            occlusion_ratio=0.08,
            identity_confidence=0.95,
            dropped_frame_ratio=0.02,
        )
    )
    assert result.usable_for_body_kinematics
    assert result.usable_for_fine_hand_analysis
    assert result.usable_for_individual_report


def test_occlusion_blocks_fine_hand_analysis() -> None:
    result = assess_motion_quality(
        MotionQualityInput(
            body_valid_ratio=0.85,
            hand_valid_ratio=0.80,
            foot_valid_ratio=0.80,
            detector_confidence=0.90,
            occlusion_ratio=0.40,
            identity_confidence=0.95,
            dropped_frame_ratio=0.02,
        )
    )
    assert not result.usable_for_fine_hand_analysis
    assert "high_occlusion" in result.limitations
