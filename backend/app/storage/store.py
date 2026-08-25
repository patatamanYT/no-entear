"""
Tiny in-memory (+ JSON-file-backed) store for the "current" processed match
and for uploaded-video bookkeeping. No database needed for this project.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, Optional

from app.schemas import JobStatusResponse, MatchData, UploadResponse

STORAGE_DIR = Path(__file__).parent
UPLOADS_DIR = STORAGE_DIR / "uploads"
CURRENT_MATCH_PATH = STORAGE_DIR / "current_match.json"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


class MatchStore:
    """Holds the most recently processed/mocked MatchData, in memory, with a
    JSON-file cache so it survives a process restart."""

    def __init__(self, cache_path: Path = CURRENT_MATCH_PATH) -> None:
        self._cache_path = cache_path
        self._match: Optional[MatchData] = None
        self._lock = threading.Lock()
        # Upload bookkeeping: video_id -> {filename, path}
        self._uploads: Dict[str, dict] = {}
        # Background-processing job bookkeeping: video_id -> JobStatusResponse.
        # Real-pipeline runs can take minutes on a 20-minute clip, so
        # POST /api/process returns immediately and the caller polls this.
        self._jobs: Dict[str, JobStatusResponse] = {}

    def get(self) -> Optional[MatchData]:
        with self._lock:
            if self._match is not None:
                return self._match
            if self._cache_path.exists():
                try:
                    data = self._cache_path.read_text()
                    self._match = MatchData.model_validate_json(data)
                except Exception:
                    self._match = None
            return self._match

    def set(self, match: MatchData) -> None:
        with self._lock:
            self._match = match
            try:
                self._cache_path.parent.mkdir(parents=True, exist_ok=True)
                self._cache_path.write_text(match.model_dump_json(indent=2))
            except OSError:
                # Cache write failures shouldn't break serving the in-memory match.
                pass

    def register_upload(self, video_id: str, filename: str, path: Path) -> UploadResponse:
        with self._lock:
            self._uploads[video_id] = {"filename": filename, "path": str(path)}
        return UploadResponse(video_id=video_id, filename=filename)

    def get_upload_path(self, video_id: str) -> Optional[Path]:
        with self._lock:
            entry = self._uploads.get(video_id)
        return Path(entry["path"]) if entry else None

    def set_job_status(
        self, video_id: str, match_id: str, status: str, error: Optional[str] = None
    ) -> JobStatusResponse:
        job = JobStatusResponse(video_id=video_id, match_id=match_id, status=status, error=error)
        with self._lock:
            self._jobs[video_id] = job
        return job

    def get_job_status(self, video_id: str) -> Optional[JobStatusResponse]:
        with self._lock:
            return self._jobs.get(video_id)


# Process-wide singleton used by app.main.
store = MatchStore()
