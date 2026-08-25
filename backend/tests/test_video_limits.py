"""
Tests for the "accept up to 20-minute videos" hardening: upload validation
(type/size), the duration ceiling + auto frame-stride in app.pipeline, and
the async background-job wiring for real-pipeline processing (POST
/api/process returns immediately; a client polls the status endpoint).

None of these need a real video file or model weights: the duration/stride
math is pure functions, and the async-job test exercises the failure path
(an invalid "video" file) which fails fast in app.pipeline before any
ultralytics/network dependency would be touched.
"""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.pipeline import recommended_frame_stride, validate_video_duration

client = TestClient(app)


# ---------------------------------------------------------------------------
# Duration ceiling + auto frame-stride (pure functions, no video needed)
# ---------------------------------------------------------------------------


def test_validate_video_duration_allows_up_to_20_minutes():
    validate_video_duration(20 * 60, max_seconds=20 * 60)  # exactly at the limit: OK
    validate_video_duration(5 * 60, max_seconds=20 * 60)  # well under: OK


def test_validate_video_duration_rejects_over_20_minutes():
    with pytest.raises(RuntimeError, match=r"20 min"):
        validate_video_duration(20 * 60 + 1, max_seconds=20 * 60)


def test_recommended_frame_stride_is_1_for_short_clips():
    # 30s at 25fps = 750 frames, well under the target -> process every frame.
    assert recommended_frame_stride(fps=25.0, duration_seconds=30.0, target_max_frames=9000) == 1


def test_recommended_frame_stride_scales_up_for_a_full_20_minute_clip():
    # 20 min at 30fps = 36000 frames; with a 9000-frame target that's a 4x stride.
    stride = recommended_frame_stride(fps=30.0, duration_seconds=20 * 60, target_max_frames=9000)
    assert stride == 4
    total_processed = (30.0 * 20 * 60) / stride
    assert total_processed <= 9000


def test_recommended_frame_stride_never_goes_below_1():
    assert recommended_frame_stride(fps=1.0, duration_seconds=0.0, target_max_frames=9000) == 1


# ---------------------------------------------------------------------------
# Upload validation: file type + size
# ---------------------------------------------------------------------------


def test_upload_rejects_non_video_extension():
    resp = client.post(
        "/api/upload",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 415


def test_upload_accepts_video_extension_and_registers_it():
    resp = client.post(
        "/api/upload",
        files={"file": ("clip.mp4", io.BytesIO(b"not a real video, just bytes"), "video/mp4")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "clip.mp4"
    assert data["video_id"]


def test_upload_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr("app.main.MAX_UPLOAD_SIZE_BYTES", 10)  # 10 bytes, trivially exceeded
    resp = client.post(
        "/api/upload",
        files={"file": ("clip.mp4", io.BytesIO(b"x" * 1000), "video/mp4")},
    )
    assert resp.status_code == 413


# ---------------------------------------------------------------------------
# Async processing: POST /api/process returns immediately, status is pollable
# ---------------------------------------------------------------------------


def test_process_real_pipeline_is_async_and_status_is_pollable():
    upload = client.post(
        "/api/upload",
        files={"file": ("clip.mp4", io.BytesIO(b"not a real video"), "video/mp4")},
    )
    video_id = upload.json()["video_id"]

    resp = client.post("/api/process", json={"video_id": video_id, "mock": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "processing"
    assert body["source"] == "cv_pipeline"

    # TestClient runs BackgroundTasks synchronously as part of the request
    # lifecycle, so by the time the POST above returned, the job has already
    # run to completion (here: failed fast, since the "video" isn't real).
    status_resp = client.get(f"/api/process/{video_id}/status")
    assert status_resp.status_code == 200
    status = status_resp.json()
    assert status["video_id"] == video_id
    assert status["status"] == "failed"
    assert status["error"]  # non-empty message explaining the failure


def test_process_status_404_for_unknown_video_id():
    resp = client.get("/api/process/does-not-exist/status")
    assert resp.status_code == 404


def test_process_mock_stays_synchronous():
    resp = client.post("/api/process", json={"mock": True})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
