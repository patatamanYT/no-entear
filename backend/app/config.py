"""
Centralized, environment-overridable tunables for video ingestion and
processing limits. Kept in one place instead of scattered magic numbers so
the actual limits this deployment enforces are visible at a glance and easy
to change without hunting through app/main.py and app/pipeline.py.
"""
from __future__ import annotations

import os


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _env_list(name: str, default: list[str]) -> list[str]:
    # Comma-separated list, e.g. "https://a.example, https://b.example".
    # Whitespace around items and empty items are dropped. An unset or
    # blank variable falls back to a copy of the default so callers can't
    # mutate the module-level default by accident.
    raw = os.environ.get(name)
    if not raw or not raw.strip():
        return list(default)
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


# Longest clip the real CV pipeline will accept. 20 minutes is the target
# use case for this deployment (a full fútbol 7 half plus stoppage time);
# processing time and memory both scale with video length, so this is an
# explicit, enforced ceiling rather than an implicit failure mode.
MAX_VIDEO_DURATION_SECONDS = _env_int("MAX_VIDEO_DURATION_SECONDS", 20 * 60)

# Upload size ceiling. 2 GiB comfortably covers a 20-minute 1080p H.264 clip
# (typically a few hundred MB) with headroom for less-compressed footage.
MAX_UPLOAD_SIZE_BYTES = _env_int("MAX_UPLOAD_SIZE_BYTES", 2 * 1024 * 1024 * 1024)

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv", ".m4v"}
ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/webm",
    "video/x-matroska",
    "video/x-m4v",
}

# The real pipeline runs YOLO inference per processed frame, so total
# runtime scales linearly with frame count. Rather than let a long video
# silently take hours at stride=1, the pipeline auto-picks a frame_stride
# that keeps the processed-frame count near this target (overridable by
# passing an explicit frame_stride to run_real_pipeline). ~9000 frames is a
# few minutes of inference on CPU for a small model, regardless of the
# source clip's raw length or fps.
TARGET_MAX_PROCESSED_FRAMES = _env_int("TARGET_MAX_PROCESSED_FRAMES", 9000)

# Swapping detection/pose models (e.g. a football-specific YOLO checkpoint
# fine-tuned on a Roboflow Universe dataset, or a newer Ultralytics release)
# is a config change, not a code change — point these at any Ultralytics-
# compatible .pt weights file or model name.
YOLO_WEIGHTS_PATH = _env_str("YOLO_WEIGHTS_PATH", "yolov8n.pt")
YOLO_POSE_WEIGHTS_PATH = _env_str("YOLO_POSE_WEIGHTS_PATH", "yolov8n-pose.pt")

# Multi-object tracker backend for app.cv.detector.PlayerBallDetector:
#   "bytetrack" (default) — supervision's ByteTrack, tuned via the
#     BYTETRACK_* constants in app.cv.detector.
#   "botsort"  — Ultralytics' native BoT-SORT (adds a camera-motion
#     compensation + appearance-embedding re-ID step on top of ByteTrack's
#     motion model; more robust through longer occlusions/collisions at
#     some extra compute cost).
TRACKER_BACKEND = _env_str("TRACKER_BACKEND", "bytetrack")

# Origins the browser frontend may call the API from (CORS allow-list).
# Override with a comma-separated CORS_ALLOWED_ORIGINS env var for
# deployment. A "*" entry allows any origin and is for local dev only.
CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS",
    ["http://localhost:3000", "http://127.0.0.1:3000"],
)
