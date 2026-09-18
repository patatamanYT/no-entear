"""
Tests for the pure-geometry half of app/cv/pose_estimator.py (joint angles,
torso lean, posture classification, box IoU matching) — none of this needs
YOLO-Pose weights, only numpy.
"""
from __future__ import annotations

import numpy as np
import pytest

from app.cv.pose_estimator import (
    KP,
    PoseResult,
    classify_posture,
    joint_angle,
    knee_angle,
    match_poses_to_boxes,
    torso_lean_degrees,
)


def _make_pose(points: dict, box=(0.0, 0.0, 10.0, 10.0)) -> PoseResult:
    """Builds a 17-keypoint array with the given {name: (x, y)} set at full
    confidence and everything else at zero confidence (unset)."""
    kpts = np.zeros((17, 3), dtype=np.float64)
    for name, (x, y) in points.items():
        kpts[KP[name]] = (x, y, 0.9)
    return PoseResult(box=box, keypoints=kpts)


# ---------------------------------------------------------------------------
# joint_angle
# ---------------------------------------------------------------------------


def test_joint_angle_straight_line_is_180():
    angle = joint_angle((0, 0), (1, 0), (2, 0))
    assert angle == pytest.approx(180.0, abs=1e-6)


def test_joint_angle_right_angle_is_90():
    angle = joint_angle((0, 1), (0, 0), (1, 0))
    assert angle == pytest.approx(90.0, abs=1e-6)


def test_joint_angle_degenerate_zero_length_vector_is_zero():
    assert joint_angle((0, 0), (0, 0), (1, 0)) == 0.0


# ---------------------------------------------------------------------------
# knee_angle: missing keypoints -> None, present -> real angle
# ---------------------------------------------------------------------------


def test_knee_angle_bent_knee():
    # Hip above knee, ankle out to the side -> a clearly bent (< 180) knee.
    pose = _make_pose({"left_hip": (5, 0), "left_knee": (5, 5), "left_ankle": (8, 5)})
    angle = knee_angle(pose, side="left")
    assert angle is not None
    assert 0 < angle < 180


def test_knee_angle_straight_leg_near_180():
    pose = _make_pose({"left_hip": (5, 0), "left_knee": (5, 5), "left_ankle": (5, 10)})
    angle = knee_angle(pose, side="left")
    assert angle == pytest.approx(180.0, abs=1e-3)


def test_knee_angle_missing_keypoint_returns_none():
    pose = _make_pose({"left_hip": (5, 0), "left_knee": (5, 5)})  # no ankle
    assert knee_angle(pose, side="left") is None


def test_knee_angle_low_confidence_keypoint_treated_as_missing():
    kpts = np.zeros((17, 3))
    kpts[KP["left_hip"]] = (5, 0, 0.9)
    kpts[KP["left_knee"]] = (5, 5, 0.9)
    kpts[KP["left_ankle"]] = (5, 10, 0.05)  # below MIN_KEYPOINT_CONFIDENCE
    pose = PoseResult(box=(0, 0, 10, 10), keypoints=kpts)
    assert knee_angle(pose, side="left") is None


# ---------------------------------------------------------------------------
# torso_lean_degrees + classify_posture
# ---------------------------------------------------------------------------


def test_torso_lean_upright_is_near_zero():
    pose = _make_pose(
        {
            "left_shoulder": (4, 0), "right_shoulder": (6, 0),
            "left_hip": (4, 5), "right_hip": (6, 5),
        }
    )
    lean = torso_lean_degrees(pose)
    assert lean == pytest.approx(0.0, abs=1e-6)
    assert classify_posture(pose) == "standing"


def test_torso_lean_fallen_is_near_90():
    # Hips displaced almost entirely horizontally from the shoulders ->
    # a torso lying flat, i.e. "fallen".
    pose = _make_pose(
        {
            "left_shoulder": (0, 5), "right_shoulder": (2, 5),
            "left_hip": (10, 5.2), "right_hip": (12, 5.2),
        }
    )
    lean = torso_lean_degrees(pose)
    assert lean > 60.0
    assert classify_posture(pose) == "fallen"


def test_torso_lean_missing_keypoints_returns_none_and_unknown():
    pose = _make_pose({"left_shoulder": (4, 0)})  # everything else unset
    assert torso_lean_degrees(pose) is None
    assert classify_posture(pose) == "unknown"


def test_classify_posture_leaning_between_thresholds():
    # ~40 degrees of lean: past LEANING_LEAN_DEGREES (25) but under
    # FALLEN_LEAN_DEGREES (60).
    import math

    dx, dy = math.sin(math.radians(40)) * 5, math.cos(math.radians(40)) * 5
    pose = _make_pose(
        {
            "left_shoulder": (0, 0), "right_shoulder": (2, 0),
            "left_hip": (dx, dy), "right_hip": (dx + 2, dy),
        }
    )
    assert classify_posture(pose) == "leaning"


# ---------------------------------------------------------------------------
# Pose <-> tracked-box association via IoU
# ---------------------------------------------------------------------------


def test_match_poses_to_boxes_picks_best_overlap():
    pose_a = _make_pose({}, box=(0, 0, 10, 10))
    pose_b = _make_pose({}, box=(100, 100, 110, 110))
    tracked_boxes = [(0, 0, 10, 10), (100, 100, 110, 110), (500, 500, 510, 510)]

    matches = match_poses_to_boxes([pose_a, pose_b], tracked_boxes)

    assert matches[0] is pose_a
    assert matches[1] is pose_b
    assert 2 not in matches  # no pose overlaps this tracked box at all


def test_match_poses_to_boxes_respects_min_iou():
    # Poses that barely clip the tracked box shouldn't count as a match.
    pose = _make_pose({}, box=(9.9, 9.9, 20, 20))
    tracked_boxes = [(0, 0, 10, 10)]
    matches = match_poses_to_boxes([pose], tracked_boxes, min_iou=0.3)
    assert matches == {}
