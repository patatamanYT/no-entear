"""
Pitch calibration via 4-point (or N-point) homography.

Maps pixel coordinates (u, v) from a broadcast/tactical camera view to
real-world pitch coordinates (X in [0, 60], Y in [0, 40] for a fútbol 7
pitch) in meters.

`cv2` is imported lazily inside methods so that importing this module (and
therefore `app.main` / the mock-data flow) never requires OpenCV to be
installed or any weights/network access.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Sequence, Tuple

import numpy as np

Bounds = Tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)


class PitchHomography:
    """Fits and applies a planar homography from image pixels to pitch meters.

    Usage:
        h = PitchHomography()
        h.fit(src_points, dst_points, bounds=(0, 0, 60, 40))
        pitch_xy = h.transform(pixel_points)   # already clamped to bounds
    """

    def __init__(self) -> None:
        self._matrix: Optional[np.ndarray] = None
        self._bounds: Optional[Bounds] = None

    @property
    def matrix(self) -> Optional[np.ndarray]:
        return self._matrix

    @property
    def is_fitted(self) -> bool:
        return self._matrix is not None

    def fit(
        self,
        src_points: Sequence[Tuple[float, float]],
        dst_points: Sequence[Tuple[float, float]],
        bounds: Optional[Bounds] = None,
    ) -> "PitchHomography":
        """Compute the homography mapping src_points (pixels) -> dst_points (pitch meters).

        Exactly 4 correspondences uses cv2.getPerspectiveTransform (exact fit).
        More than 4 uses cv2.findHomography with RANSAC for robustness against
        noisy/manual point picking.

        `bounds`, when given as (x_min, y_min, x_max, y_max), is stored and
        applied by every subsequent transform() call — projected points are
        clamped to it. A perspective transform is unbounded and a slightly
        mis-clicked calibration corner or a player near the touchline can
        easily project a few centimeters outside the real pitch; without
        clamping that shows up downstream as an out-of-bounds dot on the 2D
        pitch or a skewed heatmap/convex-hull edge.
        """
        import cv2  # lazy import

        src = np.asarray(src_points, dtype=np.float32)
        dst = np.asarray(dst_points, dtype=np.float32)

        if src.shape[0] != dst.shape[0]:
            raise ValueError("src_points and dst_points must have the same length")
        if src.shape[0] < 4:
            raise ValueError("At least 4 point correspondences are required")

        if src.shape[0] == 4:
            matrix = cv2.getPerspectiveTransform(src, dst)
        else:
            matrix, _mask = cv2.findHomography(src, dst, method=cv2.RANSAC)
            if matrix is None:
                raise ValueError("Homography estimation failed (degenerate points?)")

        self._matrix = matrix
        self._bounds = bounds
        return self

    def transform(self, points: Sequence[Tuple[float, float]]) -> np.ndarray:
        """Transform pixel points (N, 2) -> pitch coordinates (N, 2) in
        meters, clamped to `bounds` if it was set on fit()."""
        import cv2  # lazy import

        if self._matrix is None:
            raise RuntimeError("PitchHomography must be fit() before transform()")

        pts = np.asarray(points, dtype=np.float32).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, self._matrix).reshape(-1, 2)

        if self._bounds is not None:
            x_min, y_min, x_max, y_max = self._bounds
            transformed[:, 0] = np.clip(transformed[:, 0], x_min, x_max)
            transformed[:, 1] = np.clip(transformed[:, 1], y_min, y_max)

        return transformed

    def transform_point(self, x: float, y: float) -> Tuple[float, float]:
        result = self.transform([(x, y)])
        return float(result[0, 0]), float(result[0, 1])


class PositionSmoother:
    """Lightweight per-track moving-average filter over projected pitch
    coordinates, to absorb frame-to-frame homography jitter (sub-pixel noise
    in the detected foot point gets amplified by the perspective transform,
    especially far from the camera) without the lag a larger filter would
    add to genuinely fast movement.

    Usage:
        smoother = PositionSmoother(window=4)
        x, y = smoother.smooth(track_id, raw_x, raw_y)   # call once per frame per track
    """

    def __init__(self, window: int = 4) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window
        self._history: Dict[int, Deque[Tuple[float, float]]] = defaultdict(
            lambda: deque(maxlen=self.window)
        )

    def smooth(self, track_id: int, x: float, y: float) -> Tuple[float, float]:
        hist = self._history[track_id]
        hist.append((x, y))
        n = len(hist)
        sx = sum(p[0] for p in hist) / n
        sy = sum(p[1] for p in hist) / n
        return sx, sy

    def reset(self, track_id: Optional[int] = None) -> None:
        """Drop history for one track (e.g. its ID was lost/reassigned) or
        all tracks when `track_id` is None."""
        if track_id is None:
            self._history.clear()
        else:
            self._history.pop(track_id, None)


def default_pitch_corners(pitch_length: float = 60.0, pitch_width: float = 40.0):
    """Convenience: the 4 pitch-coordinate corners in a fixed order
    (top-left, top-right, bottom-right, bottom-left) matching a typical
    manual 4-point pixel calibration click order.
    """
    return [
        (0.0, 0.0),
        (pitch_length, 0.0),
        (pitch_length, pitch_width),
        (0.0, pitch_width),
    ]
