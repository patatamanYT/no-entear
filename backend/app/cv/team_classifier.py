"""
Jersey-color based team classification.

Pipeline:
  1. `extract_jersey_color` crops the upper-torso region of a player bounding
     box, converts to HSV, masks out grass-green pixels, and returns a
     dominant-color feature vector (mean color of the remaining pixels).
  2. `TeamClassifier` clusters those feature vectors across all players in a
     frame (or a sample of frames) into 2 clusters via KMeans, and predicts
     a 0/1 team label for new color vectors.

`cv2` and `sklearn` are imported lazily inside functions/methods so this
module can be imported with zero heavy dependencies installed.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

# Grass hue range in OpenCV HSV (H: 0-179, S: 0-255, V: 0-255).
GRASS_HUE_MIN = 35
GRASS_HUE_MAX = 85
GRASS_SAT_MIN = 40
GRASS_VAL_MIN = 30  # extra robustness beyond a pure H/S gate: drops near-black
# shadowed-grass pixels that would otherwise pass the hue/saturation test.

# Upper-torso ROI as a fraction of the player bounding box: skips the head,
# shorts/legs, and trims the sides so a neighboring player or grass bleeding
# in from the box edges doesn't contaminate the jersey-color sample.
TORSO_Y_MIN_FRAC = 0.15
TORSO_Y_MAX_FRAC = 0.45
TORSO_X_MIN_FRAC = 0.20
TORSO_X_MAX_FRAC = 0.80


def extract_jersey_color(crop_bgr: np.ndarray) -> np.ndarray:
    """Extract a dominant-color feature vector (BGR, 3-float) from a player
    bounding-box crop, focusing on the upper-torso (jersey) region and
    filtering out grass-green pixels.

    Returns a zero vector if the crop is empty or entirely grass/background.
    """
    import cv2  # lazy import

    if crop_bgr is None or crop_bgr.size == 0:
        return np.zeros(3, dtype=np.float32)

    h, w = crop_bgr.shape[:2]
    if h < 2 or w < 2:
        return np.zeros(3, dtype=np.float32)

    # Upper-torso ROI: skip the head and shorts/legs, trim the sides to
    # avoid neighboring players/background (see TORSO_*_FRAC above).
    top = int(h * TORSO_Y_MIN_FRAC)
    bottom = int(h * TORSO_Y_MAX_FRAC)
    left = int(w * TORSO_X_MIN_FRAC)
    right = int(w * TORSO_X_MAX_FRAC)
    top, bottom = min(top, h - 1), max(bottom, top + 1)
    left, right = min(left, w - 1), max(right, left + 1)

    torso = crop_bgr[top:bottom, left:right]
    if torso.size == 0:
        torso = crop_bgr

    hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    grass_mask = (
        (hue >= GRASS_HUE_MIN)
        & (hue <= GRASS_HUE_MAX)
        & (sat >= GRASS_SAT_MIN)
        & (val >= GRASS_VAL_MIN)
    )
    keep_mask = ~grass_mask

    pixels = torso.reshape(-1, 3).astype(np.float32)
    keep_flat = keep_mask.reshape(-1)

    if keep_flat.sum() < max(4, 0.05 * keep_flat.size):
        # Too little non-grass signal; fall back to using all pixels.
        selected = pixels
    else:
        selected = pixels[keep_flat]

    if selected.size == 0:
        return np.zeros(3, dtype=np.float32)

    return selected.mean(axis=0).astype(np.float32)


class TeamClassifier:
    """Clusters player jersey-color feature vectors into team clusters.

    `n_clusters=2` is the simple two-team case. `n_clusters=3` additionally
    separates out a third, minority cluster intended to catch referees and
    goalkeepers, who typically wear a kit visually distinct from both
    outfield teams — see `referee_cluster()`. This is a heuristic (it
    assumes officials are a color-distinct minority, not e.g. a goalkeeper
    who happens to share a team's exact jersey color) rather than a
    guarantee, appropriate for the "best-effort without manual labeling"
    scope of this pipeline.
    """

    def __init__(self, n_clusters: int = 2, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._model = None
        self._cluster_to_label: dict[int, int] = {}
        self.labels_: Optional[np.ndarray] = None

    def fit(self, color_features: Sequence[Sequence[float]]) -> "TeamClassifier":
        from sklearn.cluster import KMeans  # lazy import

        X = np.asarray(color_features, dtype=np.float32)
        if X.ndim != 2 or X.shape[0] < self.n_clusters:
            raise ValueError(
                f"Need at least {self.n_clusters} color feature rows to fit"
            )

        model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        model.fit(X)
        self._model = model
        # Identity mapping by default; cluster ids are already 0..n_clusters-1.
        self._cluster_to_label = {i: i for i in range(self.n_clusters)}
        self.labels_ = model.labels_
        return self

    def referee_cluster(self) -> Optional[int]:
        """With n_clusters=3, returns the cluster id most likely to be
        referees/goalkeepers: the smallest of the three groups, since a
        match has far more outfield players than officials. Returns None
        if not fit with exactly 3 clusters."""
        if self._model is None or self.n_clusters != 3 or self.labels_ is None:
            return None
        counts: Dict[int, int] = {}
        for label in self.labels_:
            counts[int(label)] = counts.get(int(label), 0) + 1
        return min(counts, key=lambda c: counts[c])

    def predict(self, color_features: Sequence[Sequence[float]]) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("TeamClassifier must be fit() before predict()")
        X = np.asarray(color_features, dtype=np.float32)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        raw = self._model.predict(X)
        return np.array([self._cluster_to_label[int(c)] for c in raw], dtype=int)

    def fit_predict(self, color_features: Sequence[Sequence[float]]) -> np.ndarray:
        self.fit(color_features)
        return self.predict(color_features)

    @property
    def cluster_centers(self) -> Optional[np.ndarray]:
        if self._model is None:
            return None
        return self._model.cluster_centers_
