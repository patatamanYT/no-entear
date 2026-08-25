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

from typing import Optional, Sequence, Tuple

import numpy as np


class PitchHomography:
    """Fits and applies a planar homography from image pixels to pitch meters.

    Usage:
        h = PitchHomography()
        h.fit(src_points, dst_points)   # >= 4 point correspondences
        pitch_xy = h.transform(pixel_points)
    """

    def __init__(self) -> None:
        self._matrix: Optional[np.ndarray] = None

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
    ) -> "PitchHomography":
        """Compute the homography mapping src_points (pixels) -> dst_points (pitch meters).

        Exactly 4 correspondences uses cv2.getPerspectiveTransform (exact fit).
        More than 4 uses cv2.findHomography with RANSAC for robustness against
        noisy/manual point picking.
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
        return self

    def transform(self, points: Sequence[Tuple[float, float]]) -> np.ndarray:
        """Transform pixel points (N, 2) -> pitch coordinates (N, 2) in meters."""
        import cv2  # lazy import

        if self._matrix is None:
            raise RuntimeError("PitchHomography must be fit() before transform()")

        pts = np.asarray(points, dtype=np.float32).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, self._matrix)
        return transformed.reshape(-1, 2)

    def transform_point(self, x: float, y: float) -> Tuple[float, float]:
        result = self.transform([(x, y)])
        return float(result[0, 0]), float(result[0, 1])


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
