"""
Ball-specific trajectory resolution: kinematic outlier rejection, multi-
candidate disambiguation, short-gap interpolation, and possession-anchored
fallback — operating on already-homographed pitch coordinates (meters) so
velocity gating is physically meaningful (m/s) rather than pixel-space.

Pure numpy, zero cv2/ultralytics/sklearn dependency — trivially unit
testable and free to import at module load time.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

MAX_BALL_SPEED_MS = 35.0  # kinematic gate: reject impossible teleports
MAX_INTERP_GAP_FRAMES = 5  # bridge occlusions up to this many consecutive frames
POSSESSION_RADIUS_M = 1.2  # matches app.analytics.events.POSSESSION_RADIUS_M

Point = Tuple[float, float]
Candidate = Tuple[float, float, float]  # (x, y, confidence)


class ConstantVelocityKalman2D:
    """Minimal constant-velocity Kalman filter over state [x, y, vx, vy].

    Used to predict where the ball should be on frames with no accepted
    observation, and to disambiguate between multiple ball candidates in a
    frame by preferring the one closest to the prediction.
    """

    def __init__(self, process_var: float = 4.0, measurement_var: float = 0.35) -> None:
        self.process_var = process_var
        self.measurement_var = measurement_var
        self.x = np.zeros(4, dtype=np.float64)  # [x, y, vx, vy]
        self.P = np.eye(4, dtype=np.float64) * 1e3
        self._initialized = False

    @property
    def position(self) -> Point:
        return float(self.x[0]), float(self.x[1])

    def initialize(self, x: float, y: float) -> None:
        self.x = np.array([x, y, 0.0, 0.0], dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64) * 1e2
        self._initialized = True

    def predict(self, dt: float) -> Optional[Point]:
        if not self._initialized:
            return None
        F = np.array(
            [[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float64
        )
        q = self.process_var * max(dt, 1e-3)
        Q = np.diag([q * dt, q * dt, q, q])
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        return self.position

    def update(self, x: float, y: float) -> Point:
        if not self._initialized:
            self.initialize(x, y)
            return self.position
        H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=np.float64)
        R = np.eye(2, dtype=np.float64) * self.measurement_var
        z = np.array([x, y], dtype=np.float64)
        y_resid = z - H @ self.x
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y_resid
        self.P = (np.eye(4) - K @ H) @ self.P
        return self.position


@dataclass
class BallTrackerConfig:
    max_speed_ms: float = MAX_BALL_SPEED_MS
    max_interp_gap: int = MAX_INTERP_GAP_FRAMES
    possession_radius_m: float = POSSESSION_RADIUS_M


@dataclass
class _Resolved:
    frame: int
    pos: Optional[Point]
    source: str  # "observed" | "interpolated" | "anchored" | "unresolved"


def _hypot(dx: float, dy: float) -> float:
    return float(np.hypot(dx, dy))


def _nearest_player_within(point: Point, players: Dict[str, Point], radius: float) -> Optional[str]:
    best_id, best_d = None, radius
    for pid, (px, py) in players.items():
        d = _hypot(px - point[0], py - point[1])
        if d <= best_d:
            best_d = d
            best_id = pid
    return best_id


class BallTracker:
    """Resolves one ball position per frame from noisy, possibly-multi-
    candidate per-frame detections, in pitch-meter coordinates.

    Usage:
        tracker = BallTracker()
        resolved = tracker.resolve(candidates_per_frame, frame_times, player_frames)
        # resolved[i] is (x, y) or None if the gap could not be bridged
        # (occlusion at the very start/end of the clip, or longer than
        # config.max_interp_gap with no possession anchor available) —
        # callers typically hold the last known position in that case.
    """

    def __init__(self, config: Optional[BallTrackerConfig] = None) -> None:
        self.config = config or BallTrackerConfig()
        self.kalman = ConstantVelocityKalman2D()

    def resolve(
        self,
        candidates_per_frame: Sequence[Sequence[Candidate]],
        frame_times: Sequence[float],
        player_frames: Optional[Sequence[Dict[str, Point]]] = None,
    ) -> List[Optional[Point]]:
        if len(candidates_per_frame) != len(frame_times):
            raise ValueError("candidates_per_frame and frame_times must be the same length")

        self.kalman = ConstantVelocityKalman2D()
        observed = self._select_observations(candidates_per_frame, frame_times)
        resolved = self._bridge_gaps(observed, frame_times, player_frames)
        return [r.pos for r in resolved]

    # -- step 1: per-frame candidate selection with kinematic + KF gating ----
    def _select_observations(
        self,
        candidates_per_frame: Sequence[Sequence[Candidate]],
        frame_times: Sequence[float],
    ) -> List[Optional[Point]]:
        observed: List[Optional[Point]] = [None] * len(candidates_per_frame)
        last_confirmed: Optional[Point] = None
        last_t: Optional[float] = None

        for i, candidates in enumerate(candidates_per_frame):
            t = frame_times[i]
            dt = (t - last_t) if last_t is not None else 0.0
            predicted = self.kalman.predict(dt)

            if not candidates:
                continue

            valid: List[Candidate] = []
            for cand in candidates:
                if last_confirmed is not None and dt > 0:
                    dist = _hypot(cand[0] - last_confirmed[0], cand[1] - last_confirmed[1])
                    if dist / dt > self.config.max_speed_ms:
                        continue  # kinematically impossible jump -> reject
                valid.append(cand)

            if not valid:
                continue

            if predicted is not None:
                best = min(valid, key=lambda c: _hypot(c[0] - predicted[0], c[1] - predicted[1]))
            else:
                best = max(valid, key=lambda c: c[2])  # highest confidence

            pos = self.kalman.update(best[0], best[1])
            observed[i] = pos
            last_confirmed = pos
            last_t = t

        return observed

    # -- step 2: bridge gaps via interpolation, preferring possession anchor -
    def _bridge_gaps(
        self,
        observed: List[Optional[Point]],
        frame_times: Sequence[float],
        player_frames: Optional[Sequence[Dict[str, Point]]],
    ) -> List[_Resolved]:
        n = len(observed)
        resolved: List[_Resolved] = [
            _Resolved(i, observed[i], "observed" if observed[i] is not None else "unresolved")
            for i in range(n)
        ]

        i = 0
        while i < n:
            if observed[i] is not None:
                i += 1
                continue

            gap_start = i
            while i < n and observed[i] is None:
                i += 1
            gap_end = i  # exclusive
            gap_len = gap_end - gap_start
            prev_i = gap_start - 1
            next_i = gap_end if gap_end < n else None

            # Possession anchor: if a player was within range of the ball at
            # the last confirmed frame, prefer tracking them through the gap
            # over pure interpolation (matches real occlusion behavior — the
            # ball is usually still at the carrier's feet).
            carrier_id = None
            if player_frames and prev_i >= 0 and observed[prev_i] is not None and prev_i < len(player_frames):
                carrier_id = _nearest_player_within(
                    observed[prev_i], player_frames[prev_i], self.config.possession_radius_m
                )

            bounded = prev_i >= 0 and next_i is not None and gap_len <= self.config.max_interp_gap
            p0 = observed[prev_i] if prev_i >= 0 else None
            p1 = observed[next_i] if next_i is not None else None
            t0 = frame_times[prev_i] if prev_i >= 0 else None
            t1 = frame_times[next_i] if next_i is not None else None
            span = (t1 - t0) if bounded else 0.0

            for j in range(gap_start, gap_end):
                carrier_pos = carrier_id and player_frames and j < len(player_frames) and player_frames[j].get(carrier_id)
                if carrier_pos:
                    resolved[j] = _Resolved(j, carrier_pos, "anchored")
                elif bounded:
                    k = (frame_times[j] - t0) / span if span > 0 else 0.0
                    interp = (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
                    resolved[j] = _Resolved(j, interp, "interpolated")
                # else: stays "unresolved" (None) — the gap is unbounded
                # (clip start/end) or longer than max_interp_gap and no
                # carrier was in range; caller decides the fallback (e.g.
                # hold last known position).

        return resolved
