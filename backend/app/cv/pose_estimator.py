"""
Player pose estimation via Ultralytics YOLO-Pose (17 COCO keypoints per
person), plus pure-geometry helpers derived from those keypoints: joint
angles, torso lean, and a simple posture classification (standing / leaning
/ fallen) — the building blocks for things like "is this player on the
ground" or "how bent is their knee at contact."

`ultralytics` is imported lazily inside PoseEstimator methods only, so
importing this module (and therefore app.main / the mock-data flow) never
requires it to be installed or reachable. The geometry functions are pure
numpy and have no model dependency at all.

Model weights are swappable via app.config.YOLO_POSE_WEIGHTS_PATH (env var
YOLO_POSE_WEIGHTS_PATH) with zero code changes — point it at a stock
Ultralytics pose checkpoint or a fine-tuned one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from app.config import YOLO_POSE_WEIGHTS_PATH

DEFAULT_POSE_MODEL_WEIGHTS = YOLO_POSE_WEIGHTS_PATH

# Standard COCO 17-keypoint layout, as produced by Ultralytics YOLO-Pose.
KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]
KP = {name: i for i, name in enumerate(KEYPOINT_NAMES)}

MIN_KEYPOINT_CONFIDENCE = 0.3
IOU_MATCH_THRESHOLD = 0.3  # min overlap to associate a pose detection with a tracked player box

Box = Tuple[float, float, float, float]


@dataclass
class PoseResult:
    """One person's pose in a single frame: 17 (x, y, confidence) keypoints
    plus the detection box YOLO-Pose found them in."""

    box: Box
    keypoints: np.ndarray  # shape (17, 3): x, y, confidence

    def get(self, name: str) -> Optional[Tuple[float, float]]:
        """Keypoint (x, y) by name, or None if below MIN_KEYPOINT_CONFIDENCE."""
        i = KP[name]
        x, y, conf = self.keypoints[i]
        if conf < MIN_KEYPOINT_CONFIDENCE:
            return None
        return float(x), float(y)


# ---------------------------------------------------------------------------
# Pure geometry — no model dependency, fully unit-testable
# ---------------------------------------------------------------------------


def joint_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """Angle in degrees at vertex `b`, formed by segments b->a and b->c.
    180° is a fully straight joint (e.g. a locked knee); smaller is more bent."""
    v1 = np.array([a[0] - b[0], a[1] - b[1]], dtype=np.float64)
    v2 = np.array([c[0] - b[0], c[1] - b[1]], dtype=np.float64)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-9 or n2 < 1e-9:
        return 0.0
    cos_theta = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
    return float(math.degrees(math.acos(cos_theta)))


def knee_angle(pose: PoseResult, side: str = "left") -> Optional[float]:
    hip, knee, ankle = pose.get(f"{side}_hip"), pose.get(f"{side}_knee"), pose.get(f"{side}_ankle")
    if hip is None or knee is None or ankle is None:
        return None
    return joint_angle(hip, knee, ankle)


def torso_lean_degrees(pose: PoseResult) -> Optional[float]:
    """Angle of the shoulder-midpoint -> hip-midpoint line from vertical.
    ~0° is upright; larger means leaning/falling."""
    ls, rs = pose.get("left_shoulder"), pose.get("right_shoulder")
    lh, rh = pose.get("left_hip"), pose.get("right_hip")
    if not all((ls, rs, lh, rh)):
        return None
    shoulder_mid = ((ls[0] + rs[0]) / 2.0, (ls[1] + rs[1]) / 2.0)
    hip_mid = ((lh[0] + rh[0]) / 2.0, (lh[1] + rh[1]) / 2.0)
    dx = hip_mid[0] - shoulder_mid[0]
    dy = hip_mid[1] - shoulder_mid[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return 0.0
    # atan2(dx, dy): dy is the "vertical" (image-down) component, so this is
    # the deviation from a perfectly vertical torso, in [0, 180).
    return float(abs(math.degrees(math.atan2(dx, dy))))


Posture = str  # "standing" | "leaning" | "fallen" | "unknown"

FALLEN_LEAN_DEGREES = 60.0
LEANING_LEAN_DEGREES = 25.0


def classify_posture(pose: PoseResult) -> Posture:
    """Single-frame posture heuristic from torso lean alone. This is
    necessarily approximate (a real "fallen" vs. "diving header" distinction
    needs temporal context — vertical velocity across frames — which is the
    caller's job to track using the raw keypoints this module returns, not
    something a single frame can decide on its own)."""
    lean = torso_lean_degrees(pose)
    if lean is None:
        return "unknown"
    if lean >= FALLEN_LEAN_DEGREES:
        return "fallen"
    if lean >= LEANING_LEAN_DEGREES:
        return "leaning"
    return "standing"


def _box_iou(a: Box, b: Box) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def match_poses_to_boxes(
    poses: Sequence[PoseResult], tracked_boxes: Sequence[Box], min_iou: float = IOU_MATCH_THRESHOLD
) -> dict:
    """Associates each tracked player box (by its index in `tracked_boxes`)
    with the best-overlapping pose detection, since YOLO-Pose runs its own
    independent person detector rather than sharing track IDs with
    PlayerBallDetector. Returns {tracked_box_index: PoseResult}; a tracked
    box with no sufficiently-overlapping pose detection is omitted."""
    result: dict = {}
    for i, box in enumerate(tracked_boxes):
        best_pose, best_iou = None, min_iou
        for pose in poses:
            iou = _box_iou(box, pose.box)
            if iou >= best_iou:
                best_iou = iou
                best_pose = pose
        if best_pose is not None:
            result[i] = best_pose
    return result


# ---------------------------------------------------------------------------
# Model wrapper — lazy ultralytics import
# ---------------------------------------------------------------------------


class PoseEstimator:
    """Wraps a YOLO-Pose model. Constructed lazily on first use, so simply
    instantiating this class has no heavy import or network cost."""

    def __init__(self, weights_path: str = DEFAULT_POSE_MODEL_WEIGHTS, confidence: float = 0.3) -> None:
        self.weights_path = weights_path
        self.confidence = confidence
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            from ultralytics import YOLO  # lazy import

            self._model = YOLO(self.weights_path)
        return self._model

    def estimate(self, frame_bgr: np.ndarray) -> List[PoseResult]:
        """Run pose estimation on one BGR frame, returning one PoseResult
        per detected person."""
        model = self._ensure_model()
        results = model(frame_bgr, verbose=False, conf=self.confidence)[0]

        out: List[PoseResult] = []
        if results.keypoints is None or results.boxes is None:
            return out

        boxes_xyxy = results.boxes.xyxy.cpu().numpy()
        kpts = results.keypoints.data.cpu().numpy()  # (N, 17, 3)
        for box, kp in zip(boxes_xyxy, kpts):
            out.append(PoseResult(box=tuple(float(v) for v in box), keypoints=kp))
        return out
