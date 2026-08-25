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
        from app.cv.detector import PlayerBallDetector
        from app.cv.homography import PitchHomography, default_pitch_corners
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

    homography = PitchHomography()
    if homography_src_points and homography_dst_points:
        homography.fit(homography_src_points, homography_dst_points)
    else:
        # Coarse fallback: map the whole video frame to the whole pitch.
        # Accurate results require real calibration points from the caller.
        src = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]
        dst = default_pitch_corners(PITCH_LENGTH_M, PITCH_WIDTH_M)
        homography.fit(src, dst)

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
    classifier = TeamClassifier(n_clusters=2)
    labels = classifier.fit_predict([mean_colors[tid] for tid in track_ids])
    track_to_cluster = dict(zip(track_ids, labels))

    # Canonical team labeling: cluster with the lower average projected X at
    # first appearance is called "A" (mirrors the mock-data convention).
    cluster_x_sum: Dict[int, float] = defaultdict(float)
    cluster_x_count: Dict[int, int] = defaultdict(int)
    for fd in raw_frames:
        if fd.frame_bgr is None and not fd.detections:
            continue
        for det in fd.detections:
            if det.class_name != "person" or det.track_id not in track_to_cluster:
                continue
            pitch_xy = homography.transform([det.foot_point])[0]
            cluster = int(track_to_cluster[det.track_id])
            cluster_x_sum[cluster] += float(pitch_xy[0])
            cluster_x_count[cluster] += 1
    cluster_avg_x = {
        c: (cluster_x_sum[c] / cluster_x_count[c] if cluster_x_count[c] else PITCH_LENGTH_M / 2)
        for c in (0, 1)
    }
    sorted_clusters = sorted(cluster_avg_x, key=lambda c: cluster_avg_x[c])
    cluster_to_team = {sorted_clusters[0]: "A", sorted_clusters[1]: "B"}
    track_to_team = {tid: cluster_to_team[int(c)] for tid, c in track_to_cluster.items()}

    jersey_counter = {"A": 0, "B": 0}
    track_to_player_id: Dict[int, str] = {}
    players_meta: List[dict] = []
    for tid in track_ids:
        team = track_to_team[tid]
        jersey_counter[team] += 1
        pid = f"{team}{jersey_counter[team]}"
        track_to_player_id[tid] = pid
        players_meta.append(
            {"id": pid, "team": team, "jersey_number": jersey_counter[team], "name": f"Player {pid}"}
        )

    # --- Build per-frame pitch-coordinate frames ----------------------------
    frames: List[dict] = []
    last_positions: Dict[str, Tuple[float, float]] = {}
    last_ball: Tuple[float, float] = (PITCH_LENGTH_M / 2, PITCH_WIDTH_M / 2)

    for fd in raw_frames:
        players_frame = []
        ball_xy = None
        best_ball_conf = -1.0

        person_dets = [d for d in fd.detections if d.class_name == "person" and d.track_id in track_to_player_id]
        ball_dets = [d for d in fd.detections if d.class_name == "ball"]

        if person_dets:
            pts = [d.foot_point for d in person_dets]
            pitch_pts = homography.transform(pts)
            for det, (px, py) in zip(person_dets, pitch_pts):
                pid = track_to_player_id[det.track_id]
                x = float(np.clip(px, 0.0, PITCH_LENGTH_M))
                y = float(np.clip(py, 0.0, PITCH_WIDTH_M))
                prev = last_positions.get(pid, (x, y))
                v = math.hypot(x - prev[0], y - prev[1]) * fps
                players_frame.append({"id": pid, "x": x, "y": y, "v": float(v)})
                last_positions[pid] = (x, y)

        for det in ball_dets:
            if det.confidence > best_ball_conf:
                best_ball_conf = det.confidence
                pitch_pt = homography.transform([det.center])[0]
                ball_xy = (
                    float(np.clip(pitch_pt[0], 0.0, PITCH_LENGTH_M)),
                    float(np.clip(pitch_pt[1], 0.0, PITCH_WIDTH_M)),
                )

        if ball_xy is None:
            ball_xy = last_ball
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
