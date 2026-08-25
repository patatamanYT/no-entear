"""
End-to-end real CV pipeline: video -> MatchData.

Wires together app.cv.detector (YOLO + ByteTrack), app.cv.homography (pixel
-> pitch projection), app.cv.team_classifier (jersey-color team clustering),
and app.analytics.{events,heatmaps} (pass/shot detection + heatmaps) into a
single call that produces a schemas.MatchData for an uploaded video.

All heavy dependencies (ultralytics, supervision, opencv, sklearn) are only
imported inside this function / the modules it calls, at call time — nothing
here executes at import time, so importing this module has zero network or
GPU cost.

This is necessarily a best-effort pipeline: without real camera calibration
input (e.g. clicked pixel<->pitch correspondences for the penalty box), it
falls back to a coarse whole-frame-corners homography, and team assignment
uses unsupervised 2-cluster jersey-color KMeans (referees are not separately
distinguished from players by color alone). Callers needing high accuracy
should supply `homography_src_points` from a real calibration step.

Raises RuntimeError with a clear, descriptive message on any failure
(missing dependencies, unreadable video, no detections found) — callers
(app.main) are expected to catch this and return a clean error response
rather than letting it crash the request, and must NOT silently fall back to
mock data on failure.
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from app.schemas import PITCH_LENGTH_M, PITCH_WIDTH_M, MatchData

TEAM_COLORS = {"A": "#e63946", "B": "#1d3557"}
TEAM_NAMES = {"A": "Team A", "B": "Team B"}

# Sample every Nth processed frame for jersey-color team-clustering to keep
# the calibration pass fast on long videos.
TEAM_COLOR_SAMPLE_STRIDE = 5


def run_real_pipeline(
    video_path: str | Path,
    match_id: str = "cv-match-001",
    homography_src_points: Optional[Sequence[Tuple[float, float]]] = None,
    homography_dst_points: Optional[Sequence[Tuple[float, float]]] = None,
    frame_stride: int = 1,
) -> MatchData:
    video_path = str(video_path)

    try:
        import cv2  # noqa: F401  (validated early: real dependency check)
        from app.cv.ball_tracker import BallTracker
        from app.cv.detector import PlayerBallDetector
        from app.cv.homography import PitchHomography, PositionSmoother, default_pitch_corners
        from app.cv.team_classifier import TeamClassifier, extract_jersey_color
    except ImportError as exc:
        raise RuntimeError(
            "Real CV pipeline dependencies are not installed "
            "(ultralytics/supervision/opencv-python-headless/scikit-learn required): "
            f"{exc}"
        ) from exc

    import cv2  # local import, guaranteed available past the check above

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open uploaded video for reading: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
    cap.release()

    pitch_bounds = (0.0, 0.0, PITCH_LENGTH_M, PITCH_WIDTH_M)
    homography = PitchHomography()
    if homography_src_points and homography_dst_points:
        homography.fit(homography_src_points, homography_dst_points, bounds=pitch_bounds)
    else:
        # Coarse fallback: map the whole video frame to the whole pitch.
        # Accurate results require real calibration points from the caller.
        src = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]
        dst = default_pitch_corners(PITCH_LENGTH_M, PITCH_WIDTH_M)
        homography.fit(src, dst, bounds=pitch_bounds)

    try:
        detector = PlayerBallDetector()
        raw_frames = list(detector.process_video(video_path, stride=frame_stride))
    except Exception as exc:  # ultralytics/model load or decode failures
        raise RuntimeError(f"Detection/tracking failed: {exc}") from exc

    if not raw_frames:
        raise RuntimeError("No frames could be read/processed from the uploaded video.")

    # --- Team color sampling & clustering -----------------------------------
    track_color_samples: Dict[int, List] = defaultdict(list)
    for fd in raw_frames[::TEAM_COLOR_SAMPLE_STRIDE]:
        if fd.frame_bgr is None:
            continue
        for det in fd.detections:
            if det.class_name != "person":
                continue
            crop = detector.extract_crop(fd.frame_bgr, det)
            color = extract_jersey_color(crop)
            track_color_samples[det.track_id].append(color)

    track_ids = sorted(track_color_samples.keys())
    if len(track_ids) < 2:
        raise RuntimeError(
            "Not enough distinct player tracks detected to classify teams "
            f"(found {len(track_ids)}). Check the input video / model weights."
        )

    import numpy as np

    mean_colors = {tid: np.mean(samples, axis=0) for tid, samples in track_color_samples.items()}

    # 3-way clustering when there are enough distinct tracks to support it:
    # 2 outfield teams + a 3rd, minority cluster for referees/goalkeepers
    # (see TeamClassifier.referee_cluster). Falls back to a plain 2-way split
    # on very short/small clips where a 3rd cluster wouldn't be meaningful.
    use_three_way = len(track_ids) >= 6
    classifier = TeamClassifier(n_clusters=3 if use_three_way else 2)
    labels = classifier.fit_predict([mean_colors[tid] for tid in track_ids])
    track_to_cluster = dict(zip(track_ids, labels))
    referee_cluster = classifier.referee_cluster() if use_three_way else None

    # Canonical team labeling: of the two *outfield* clusters, the one with
    # the lower average projected X at first appearance is called "A"
    # (mirrors the mock-data convention). The referee cluster (if any) maps
    # straight to team "REF".
    outfield_clusters = [c for c in set(track_to_cluster.values()) if c != referee_cluster]
    cluster_x_sum: Dict[int, float] = defaultdict(float)
    cluster_x_count: Dict[int, int] = defaultdict(int)
    for fd in raw_frames:
        if fd.frame_bgr is None and not fd.detections:
            continue
        for det in fd.detections:
            if det.class_name != "person" or det.track_id not in track_to_cluster:
                continue
            cluster = int(track_to_cluster[det.track_id])
            if cluster not in outfield_clusters:
                continue
            pitch_xy = homography.transform([det.foot_point])[0]
            cluster_x_sum[cluster] += float(pitch_xy[0])
            cluster_x_count[cluster] += 1
    cluster_avg_x = {
        c: (cluster_x_sum[c] / cluster_x_count[c] if cluster_x_count[c] else PITCH_LENGTH_M / 2)
        for c in outfield_clusters
    }
    sorted_outfield = sorted(outfield_clusters, key=lambda c: cluster_avg_x[c])
    cluster_to_team = {sorted_outfield[0]: "A"}
    if len(sorted_outfield) > 1:
        cluster_to_team[sorted_outfield[-1]] = "B"
    if referee_cluster is not None:
        cluster_to_team[referee_cluster] = "REF"
    track_to_team = {tid: cluster_to_team[int(c)] for tid, c in track_to_cluster.items()}

    jersey_counter = {"A": 0, "B": 0, "REF": 0}
    track_to_player_id: Dict[int, str] = {}
    players_meta: List[dict] = []
    for tid in track_ids:
        team = track_to_team[tid]
        jersey_counter[team] += 1
        pid = f"{team}{jersey_counter[team]}"
        track_to_player_id[tid] = pid
        name = "Referee" if team == "REF" and jersey_counter[team] == 1 else f"Player {pid}"
        players_meta.append(
            {"id": pid, "team": team, "jersey_number": jersey_counter[team], "name": name}
        )

    # --- Pass 1: project players (smoothed) + collect raw ball candidates ---
    position_smoother = PositionSmoother(window=4)
    last_positions: Dict[str, Tuple[float, float]] = {}
    per_frame_players: List[List[dict]] = []
    per_frame_player_xy: List[Dict[str, Tuple[float, float]]] = []
    per_frame_ball_candidates: List[List[Tuple[float, float, float]]] = []
    frame_times: List[float] = []

    for fd in raw_frames:
        players_frame: List[dict] = []
        player_xy: Dict[str, Tuple[float, float]] = {}

        person_dets = [d for d in fd.detections if d.class_name == "person" and d.track_id in track_to_player_id]
        ball_dets = [d for d in fd.detections if d.class_name == "ball"]

        if person_dets:
            pts = [d.foot_point for d in person_dets]
            pitch_pts = homography.transform(pts)  # already clamped to pitch bounds
            for det, (px, py) in zip(person_dets, pitch_pts):
                pid = track_to_player_id[det.track_id]
                x, y = position_smoother.smooth(det.track_id, float(px), float(py))
                prev = last_positions.get(pid, (x, y))
                v = math.hypot(x - prev[0], y - prev[1]) * fps
                players_frame.append({"id": pid, "x": x, "y": y, "v": float(v)})
                last_positions[pid] = (x, y)
                player_xy[pid] = (x, y)

        ball_candidates: List[Tuple[float, float, float]] = []
        if ball_dets:
            centers = [d.center for d in ball_dets]
            ball_pts = homography.transform(centers)  # already clamped to pitch bounds
            for det, (bx, by) in zip(ball_dets, ball_pts):
                ball_candidates.append((float(bx), float(by), det.confidence))

        per_frame_players.append(players_frame)
        per_frame_player_xy.append(player_xy)
        per_frame_ball_candidates.append(ball_candidates)
        frame_times.append(fd.timestamp)

    # --- Pass 2: resolve one ball position per frame (kinematic gating +
    # short-gap interpolation + possession anchoring on occlusion) ----------
    ball_tracker = BallTracker()
    resolved_ball = ball_tracker.resolve(per_frame_ball_candidates, frame_times, per_frame_player_xy)

    last_ball: Tuple[float, float] = (PITCH_LENGTH_M / 2, PITCH_WIDTH_M / 2)
    frames: List[dict] = []
    for fd, players_frame, ball_xy in zip(raw_frames, per_frame_players, resolved_ball):
        if ball_xy is None:
            ball_xy = last_ball  # unresolved gap (clip start, or too long) -> hold
        else:
            last_ball = ball_xy
        frames.append(
            {
                "frame": fd.frame_index,
                "t": round(fd.timestamp, 3),
                "ball": {"x": ball_xy[0], "y": ball_xy[1]},
                "players": players_frame,
            }
        )

    from app.analytics.events import compute_events
    from app.analytics.heatmaps import compute_all_heatmaps

    passes, shots = compute_events(frames, players_meta)
    heatmaps = compute_all_heatmaps(frames, players_meta)

    duration = frames[-1]["t"] if frames else 0.0

    match_data = {
        "meta": {
            "match_id": match_id,
            "duration_seconds": duration,
            "fps": fps,
            "pitch_length": PITCH_LENGTH_M,
            "pitch_width": PITCH_WIDTH_M,
            "video_url": None,
            "source": "cv_pipeline",
        },
        "teams": {
            "A": {"name": TEAM_NAMES["A"], "color": TEAM_COLORS["A"]},
            "B": {"name": TEAM_NAMES["B"], "color": TEAM_COLORS["B"]},
        },
        "players": players_meta,
        "frames": frames,
        "passes": passes,
        "shots": shots,
        "heatmaps": heatmaps,
    }

    return MatchData(**match_data)
