"""
FastAPI application for the football tactical analytics backend.

Endpoints:
  GET  /api/health              -> simple liveness check
  POST /api/upload               -> multipart video upload (size/type validated)
  POST /api/process              -> mock (synchronous) or real-CV-pipeline (async) processing
  GET  /api/process/{video_id}/status -> poll a real-pipeline job's status
  GET  /api/match-data           -> the current MatchData (auto-mocks on first call)

Boots and serves mock data with zero network/model dependency: ultralytics,
supervision, and opencv are only imported lazily inside app/cv/* when the
real pipeline actually runs, never at import time.

The real CV pipeline supports clips up to app.config.MAX_VIDEO_DURATION_SECONDS
(20 minutes by default) and can take minutes to run, so POST /api/process
returns immediately with status "processing" and runs the pipeline on a
background thread (FastAPI's BackgroundTasks, which offloads a sync callable
to a thread pool) rather than blocking the request — a client polls
GET /api/process/{video_id}/status for completion.
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    ALLOWED_VIDEO_CONTENT_TYPES,
    ALLOWED_VIDEO_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
)
from app.mock_data import generate_mock_match
from app.pipeline import run_real_pipeline
from app.schemas import (
    JobStatusResponse,
    MatchData,
    ProcessRequest,
    ProcessResponse,
    UploadResponse,
)
from app.storage.store import UPLOADS_DIR, store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Football Tactical Analytics API",
    description="Backend API serving tactical match data (mocked or CV-derived) for the frontend dashboard.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    # Explicitly allow the Next.js dev server; "*" is included too since this
    # is a dev-stage project with no auth/cookies on these endpoints.
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MiB, streamed to disk — never buffers the whole file in memory


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext or '(none)'}'. Allowed: {sorted(ALLOWED_VIDEO_EXTENSIONS)}",
        )
    # Some clients send a generic/absent content-type for video files (e.g.
    # application/octet-stream); the extension check above is the primary
    # gate, this only rejects a content-type that's confidently non-video.
    if (
        file.content_type
        and file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES
        and not file.content_type.startswith("video/")
        and file.content_type != "application/octet-stream"
    ):
        raise HTTPException(status_code=415, detail=f"Unsupported content-type '{file.content_type}'.")

    video_id = uuid.uuid4().hex[:12]
    safe_name = Path(file.filename).name  # strip any path components
    dest_path = UPLOADS_DIR / f"{video_id}_{safe_name}"

    size = 0
    try:
        with dest_path.open("wb") as out:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB upload limit.",
                    )
                out.write(chunk)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {exc}") from exc
    finally:
        await file.close()

    logger.info("Uploaded video video_id=%s filename=%s size_bytes=%d", video_id, safe_name, size)
    return store.register_upload(video_id, safe_name, dest_path)


@app.post("/api/process", response_model=ProcessResponse)
async def process_video(req: ProcessRequest, background_tasks: BackgroundTasks) -> ProcessResponse:
    if req.mock or not req.video_id:
        match = generate_mock_match()
        store.set(match)
        return ProcessResponse(match_id=match.meta.match_id, source="mock", status="completed")

    video_path = store.get_upload_path(req.video_id)
    if video_path is None or not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"video_id '{req.video_id}' not found. Upload it first via POST /api/upload.",
        )

    match_id = f"cv-{req.video_id}"
    store.set_job_status(req.video_id, match_id=match_id, status="processing")
    background_tasks.add_task(_run_pipeline_job, video_path, match_id, req.video_id)
    return ProcessResponse(match_id=match_id, source="cv_pipeline", status="processing")


def _run_pipeline_job(video_path: Path, match_id: str, video_id: str) -> None:
    """Runs on a background thread (via BackgroundTasks) so a long clip
    doesn't hold the request open for minutes. Never raises — failures are
    recorded in the job store for the client to observe via the status
    endpoint, mirroring the "never silently fall back to mock data" rule
    that already applied to the synchronous path."""
    try:
        match = run_real_pipeline(video_path, match_id=match_id)
        store.set(match)
        store.set_job_status(video_id, match_id=match_id, status="completed")
        logger.info("CV pipeline completed video_id=%s match_id=%s", video_id, match_id)
    except Exception as exc:
        logger.exception("CV pipeline failed video_id=%s", video_id)
        store.set_job_status(video_id, match_id=match_id, status="failed", error=str(exc))


@app.get("/api/process/{video_id}/status", response_model=JobStatusResponse)
async def process_status(video_id: str) -> JobStatusResponse:
    job = store.get_job_status(video_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"No processing job found for video_id '{video_id}'. Call POST /api/process first.",
        )
    return job


@app.get("/api/match-data", response_model=MatchData)
async def get_match_data() -> MatchData:
    match = store.get()
    if match is None:
        # First request with nothing processed yet: auto-generate mock data
        # so the frontend works out of the box with zero setup.
        match = generate_mock_match()
        store.set(match)
    return match
