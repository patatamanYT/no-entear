"""
Tests for the CV engine refinements in app/cv/*: ball trajectory resolution
(kinematic gating + interpolation + possession anchoring), bottom-center
foot-point projection, homography boundary clamping, and the jersey-color
team classifier's torso ROI / referee-cluster isolation.

These exercise pure-numpy logic only (no cv2/ultralytics/sklearn needed for
the ball_tracker/detector-dataclass tests); the homography and
team_classifier tests do need cv2/sklearn, matching the rest of the CV
dependency set already required for backend/requirements.txt.
"""
from __future__ import annotations

import numpy as np
import pytest

from app.cv.ball_tracker import BallTracker, BallTrackerConfig, ConstantVelocityKalman2D
from app.cv.detector import Detection


# ---------------------------------------------------------------------------
# Bottom-center foot-point coordinate calculation
# ---------------------------------------------------------------------------


def test_foot_point_is_bottom_center_not_centroid():
    det = Detection(track_id=1, class_name="person", x1=10.0, y1=20.0, x2=30.0, y2=100.0, confidence=0.9)
    assert det.foot_point == (20.0, 100.0)  # bottom-center: mid-x, y2
    assert det.center == (20.0, 60.0)  # centroid, for contrast — must differ
    assert det.foot_point != det.center


def test_foot_point_handles_asymmetric_box():
    det = Detection(track_id=2, class_name="person", x1=0.0, y1=0.0, x2=50.0, y2=200.0, confidence=0.5)
    x, y = det.foot_point
    assert x == pytest.approx(25.0)
    assert y == pytest.approx(200.0)


# ---------------------------------------------------------------------------
# Ball kinematic velocity gating (reject impossible teleports)
# ---------------------------------------------------------------------------


def test_kinematic_gate_rejects_impossible_jump():
    # Ball confirmed at (0, 20). Next frame (dt=0.1s) offers two candidates:
    # a plausible one 1m away (10 m/s) and an impossible one 10m away (100 m/s).
    candidates = [
        [(0.0, 20.0, 0.9)],
        [(1.0, 20.0, 0.9)],
        [(11.0, 20.5, 0.95), (1.6, 20.0, 0.5)],  # far outlier + plausible continuation
    ]
    times = [0.0, 0.1, 0.2]
    tracker = BallTracker(BallTrackerConfig(max_speed_ms=35.0))
    resolved = tracker.resolve(candidates, times)

    assert resolved[0] == pytest.approx((0.0, 20.0), abs=1e-6)
    # Frame 2 must NOT snap to the 100 m/s outlier; the plausible candidate wins.
    assert resolved[2][0] < 5.0


def test_kinematic_gate_all_candidates_rejected_leaves_frame_unresolved_or_interpolated():
    # A single implausible candidate right after a confirmed observation,
    # followed by a plausible re-acquisition — the impossible one must never
    # be accepted as the observed position for its frame.
    candidates = [
        [(0.0, 20.0, 0.9)],
        [(50.0, 20.0, 0.9)],  # 500 m/s over dt=0.1s -> impossible, must be rejected
        [(2.0, 20.0, 0.9)],  # plausible relative to frame 0
    ]
    times = [0.0, 0.1, 0.2]
    tracker = BallTracker()
    resolved = tracker.resolve(candidates, times)

    assert resolved[0] == pytest.approx((0.0, 20.0), abs=1e-6)
    # Frame 1's outlier must not appear verbatim as the resolved position.
    assert resolved[1] is None or resolved[1][0] < 10.0
    assert resolved[2][0] == pytest.approx(2.0, abs=0.5)


# ---------------------------------------------------------------------------
# Temporal interpolation over occlusions (<= 5 consecutive missing frames)
# ---------------------------------------------------------------------------


def test_interpolates_short_occlusion_gap():
    # Ball observed at frame 0 (x=0) and frame 6 (x=6), missing frames 1-5
    # (5 consecutive gaps, at the configured max). Midpoint should land near
    # the linear path.
    candidates = [[(float(i), 10.0, 0.9)] if i in (0, 6) else [] for i in range(7)]
    times = [i * 0.1 for i in range(7)]
    tracker = BallTracker(BallTrackerConfig(max_interp_gap=5))
    resolved = tracker.resolve(candidates, times)

    assert resolved[0] == pytest.approx((0.0, 10.0), abs=1e-6)
    # The endpoint has passed through the Kalman filter's measurement update
    # (a deliberate small smoothing step, not raw passthrough), so allow a
    # little slack rather than requiring bit-exact equality.
    assert resolved[6] == pytest.approx((6.0, 10.0), abs=0.02)
    for i in range(1, 6):
        assert resolved[i] is not None
        assert resolved[i][0] == pytest.approx(float(i), abs=0.05)
        assert resolved[i][1] == pytest.approx(10.0, abs=1e-6)


def test_does_not_bridge_gap_longer_than_max_without_possession_anchor():
    # 7 missing frames between two observations exceeds max_interp_gap=5 and
    # there's no player data to anchor to, so the middle frames must stay
    # unresolved (None) rather than silently interpolating anyway.
    n = 9
    candidates = [[(0.0, 10.0, 0.9)] if i == 0 else ([(8.0, 10.0, 0.9)] if i == n - 1 else []) for i in range(n)]
    times = [i * 0.1 for i in range(n)]
    tracker = BallTracker(BallTrackerConfig(max_interp_gap=5))
    resolved = tracker.resolve(candidates, times)

    assert resolved[0] is not None
    assert resolved[-1] is not None
    assert all(resolved[i] is None for i in range(1, n - 1))


def test_gap_at_start_of_clip_is_unresolved_not_extrapolated():
    # No observation before frame 3 -> nothing to interpolate from; frames
    # 0-2 must stay None rather than guessing backwards.
    candidates = [[] , [], [], [(5.0, 5.0, 0.9)]]
    times = [0.0, 0.1, 0.2, 0.3]
    tracker = BallTracker()
    resolved = tracker.resolve(candidates, times)
    assert resolved[0] is None and resolved[1] is None and resolved[2] is None
    assert resolved[3] == pytest.approx((5.0, 5.0), abs=1e-6)


# ---------------------------------------------------------------------------
# Possession anchoring: anchor to the carrier's foot point during occlusion
# ---------------------------------------------------------------------------


def test_possession_anchor_overrides_plain_interpolation():
    # Ball confirmed glued to player "A1" at frame 0, then occluded for 3
    # frames while A1 keeps moving in a straight line the ball's own linear
    # interpolation would NOT follow (a turn), then reacquired near A1 again.
    candidates = [
        [(0.0, 20.0, 0.9)],
        [],
        [],
        [],
        [(3.0, 23.0, 0.9)],
    ]
    times = [0.0, 0.1, 0.2, 0.3, 0.4]
    # A1 possesses the ball at frame 0 (within 1.2m) and turns upward through
    # the gap — a path a straight-line interpolation from (0,20) to (3,23)
    # would NOT reproduce exactly at every intermediate frame.
    player_frames = [
        {"A1": (0.0, 20.0)},
        {"A1": (0.5, 22.5)},
        {"A1": (1.5, 22.6)},
        {"A1": (2.5, 22.8)},
        {"A1": (3.0, 23.0)},
    ]
    tracker = BallTracker()
    resolved = tracker.resolve(candidates, times, player_frames)

    # The occluded frames should track the carrier, not the straight line.
    assert resolved[1] == pytest.approx((0.5, 22.5), abs=1e-6)
    assert resolved[2] == pytest.approx((1.5, 22.6), abs=1e-6)
    assert resolved[3] == pytest.approx((2.5, 22.8), abs=1e-6)


def test_no_anchor_when_no_player_within_possession_radius():
    candidates = [[(0.0, 20.0, 0.9)], [], [(2.0, 20.0, 0.9)]]
    times = [0.0, 0.1, 0.2]
    # Nearest player is 5m away — well outside the 1.2m possession radius.
    player_frames = [{"A1": (5.0, 20.0)}, {"A1": (5.0, 20.0)}, {"A1": (5.0, 20.0)}]
    tracker = BallTracker()
    resolved = tracker.resolve(candidates, times, player_frames)
    # Falls back to plain interpolation, not the distant player's position.
    assert resolved[1] == pytest.approx((1.0, 20.0), abs=0.02)


# ---------------------------------------------------------------------------
# Multi-candidate disambiguation (prefer the Kalman-predicted position)
# ---------------------------------------------------------------------------


def test_multi_candidate_frame_prefers_prediction_over_raw_confidence():
    # Ball moving steadily along y=20 at ~10 m/s. On frame 2 two candidates
    # appear: a low-confidence one that continues the trajectory, and a
    # high-confidence one that's actually a spurious detection elsewhere.
    # Selection should follow the motion model, not just raw confidence.
    candidates = [
        [(0.0, 20.0, 0.9)],
        [(1.0, 20.0, 0.9)],
        [(2.0, 20.0, 0.2), (2.0, 35.0, 0.99)],
    ]
    times = [0.0, 0.1, 0.2]
    tracker = BallTracker()
    resolved = tracker.resolve(candidates, times)
    assert resolved[2][1] == pytest.approx(20.0, abs=1.0)


def test_constant_velocity_kalman_predicts_along_motion():
    kf = ConstantVelocityKalman2D()
    kf.update(0.0, 0.0)
    kf.predict(0.1)
    kf.update(1.0, 0.0)
    predicted = kf.predict(0.1)
    assert predicted is not None
    # Moving at ~10 m/s in +x; predicted x should continue forward, not stay put.
    assert predicted[0] > 1.0


def test_kalman_predict_before_any_update_returns_none():
    kf = ConstantVelocityKalman2D()
    assert kf.predict(0.1) is None


# ---------------------------------------------------------------------------
# Homography: boundary clamping + jitter smoothing
# ---------------------------------------------------------------------------


def test_homography_clamps_projected_points_to_bounds():
    from app.cv.homography import PitchHomography

    h = PitchHomography()
    # Identity-ish mapping over a 100x100 image -> 60x40 pitch, so a corner
    # detection slightly outside the fitted quad still projects sanely.
    src = [(0, 0), (100, 0), (100, 100), (0, 100)]
    dst = [(0, 0), (60, 0), (60, 40), (0, 40)]
    h.fit(src, dst, bounds=(0.0, 0.0, 60.0, 40.0))

    # A point far outside the source quad extrapolates to a wildly
    # out-of-bounds pitch coordinate without clamping.
    result = h.transform([(500.0, 500.0)])
    x, y = result[0]
    assert 0.0 <= x <= 60.0
    assert 0.0 <= y <= 40.0


def test_homography_without_bounds_does_not_clamp():
    from app.cv.homography import PitchHomography

    h = PitchHomography()
    src = [(0, 0), (100, 0), (100, 100), (0, 100)]
    dst = [(0, 0), (60, 0), (60, 40), (0, 40)]
    h.fit(src, dst)  # no bounds given
    result = h.transform([(500.0, 500.0)])
    x, y = result[0]
    assert x > 60.0 or y > 40.0  # unclamped extrapolation goes out of pitch range


def test_position_smoother_reduces_frame_to_frame_jitter():
    from app.cv.homography import PositionSmoother

    smoother = PositionSmoother(window=4)
    noisy = [(10.0, 10.0), (10.3, 9.8), (9.8, 10.2), (10.2, 9.9), (9.9, 10.1)]
    outputs = [smoother.smooth(1, x, y) for x, y in noisy]
    # The smoothed output should vary less than the raw noisy input.
    raw_spread = max(p[0] for p in noisy) - min(p[0] for p in noisy)
    smoothed_spread = max(p[0] for p in outputs) - min(p[0] for p in outputs)
    assert smoothed_spread < raw_spread


def test_position_smoother_tracks_are_independent():
    from app.cv.homography import PositionSmoother

    smoother = PositionSmoother(window=3)
    smoother.smooth(1, 0.0, 0.0)
    smoother.smooth(1, 0.0, 0.0)
    a = smoother.smooth(2, 100.0, 100.0)
    assert a == pytest.approx((100.0, 100.0))


# ---------------------------------------------------------------------------
# Team classifier: torso ROI cropping + grass masking + referee isolation
# ---------------------------------------------------------------------------


def test_extract_jersey_color_ignores_pure_grass_crop():
    from app.cv.team_classifier import extract_jersey_color

    # Pure saturated green (BGR) crop -> should be filtered as grass, and
    # since nothing remains, the fallback path returns the (grass) mean —
    # so instead we assert the specific torso-region crop excludes a red
    # jersey band placed OUTSIDE the torso ROI (in the "legs" region).
    crop = np.zeros((100, 60, 3), dtype=np.uint8)
    crop[:, :] = (60, 200, 60)  # BGR green, grass-like
    crop[70:90, :] = (0, 0, 255)  # bright red band in the leg region (below torso ROI)

    color = extract_jersey_color(crop)
    # Torso ROI is Y in [0.15h, 0.45h] = rows 15-45, which is still all-green
    # here, so the red leg band must NOT leak into the dominant color.
    assert color[2] < 100  # red channel (BGR index 2) stays low


def test_extract_jersey_color_picks_up_torso_band():
    from app.cv.team_classifier import extract_jersey_color

    crop = np.zeros((100, 60, 3), dtype=np.uint8)
    crop[:, :] = (60, 200, 60)  # grass-green background
    crop[15:45, 12:48] = (255, 0, 0)  # blue jersey inside the torso ROI

    color = extract_jersey_color(crop)
    assert color[0] > 150  # blue channel dominant


def test_torso_roi_excludes_head_and_legs():
    import app.cv.team_classifier as tc

    h, w = 100, 60
    top = int(h * tc.TORSO_Y_MIN_FRAC)
    bottom = int(h * tc.TORSO_Y_MAX_FRAC)
    left = int(w * tc.TORSO_X_MIN_FRAC)
    right = int(w * tc.TORSO_X_MAX_FRAC)
    assert top == 15 and bottom == 45  # skips head (0-15) and legs (45-100)
    assert left == 12 and right == 48  # trims both sides


def test_referee_cluster_identifies_minority_group():
    from app.cv.team_classifier import TeamClassifier

    rng = np.random.default_rng(0)
    team_a = rng.normal(loc=[200, 20, 20], scale=3.0, size=(9, 3))  # red-ish, 9 players
    team_b = rng.normal(loc=[20, 20, 200], scale=3.0, size=(9, 3))  # blue-ish, 9 players
    refs = rng.normal(loc=[20, 200, 200], scale=3.0, size=(2, 3))  # yellow-ish, 2 officials
    features = np.vstack([team_a, team_b, refs])

    clf = TeamClassifier(n_clusters=3)
    clf.fit(features)
    ref_cluster = clf.referee_cluster()

    assert ref_cluster is not None
    ref_labels = clf.labels_[-2:]
    assert all(int(label) == ref_cluster for label in ref_labels)


def test_referee_cluster_none_when_not_three_way():
    from app.cv.team_classifier import TeamClassifier

    clf = TeamClassifier(n_clusters=2)
    clf.fit([[0, 0, 0], [255, 255, 255], [10, 10, 10], [240, 240, 240]])
    assert clf.referee_cluster() is None
