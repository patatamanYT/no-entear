"""
FastAPI application for the football tactical analytics backend.

Endpoints:
  GET  /api/health       -> simple liveness check
  POST /api/upload        -> multipart video upload
  POST /api/process       -> mock or real-CV-pipeline processing
  GET  /api/match-data    -> the current MatchData (auto-mocks on first call)

Boots and serves mock data with zero network/model dependency: ultralytics,
supervision, and opencv are only imported lazily inside app/cv/* when the
real pipeline actually runs, never at import time.
"""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.mock_data import generate_mock_match
from app.pipeline import run_real_pipeline
from app.schemas import MatchData, ProcessRequest, ProcessResponse, UploadResponse
from app.storage.store import UPLOADS_DIR, store

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


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    video_id = uuid.uuid4().hex[:12]
    safe_name = Path(file.filename).name  # strip any path components
    dest_path = UPLOADS_DIR / f"{video_id}_{safe_name}"

    try:
        with dest_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        await file.close()

    return store.register_upload(video_id, safe_name, dest_path)


@app.post("/api/process", response_model=ProcessResponse)
async def process_video(req: ProcessRequest) -> ProcessResponse:
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

    try:
        match = run_real_pipeline(video_path, match_id=f"cv-{req.video_id}")
    except RuntimeError as exc:
        # Clear, structured failure -- never silently fall back to mock data.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - last-resort guard against a crash
        raise HTTPException(
            status_code=500, detail=f"Unexpected error running the CV pipeline: {exc}"
        ) from exc

    store.set(match)
    return ProcessResponse(match_id=match.meta.match_id, source="cv_pipeline", status="completed")


@app.get("/api/match-data", response_model=MatchData)
async def get_match_data() -> MatchData:
    match = store.get()
    if match is None:
        # First request with nothing processed yet: auto-generate mock data
        # so the frontend works out of the box with zero setup.
        match = generate_mock_match()
        store.set(match)
    return match
