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
