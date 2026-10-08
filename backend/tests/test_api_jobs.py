"""
Upload -> process -> status lifecycle tests.

The real CV pipeline is never run: app.main.run_real_pipeline is replaced with
a fake, and uploads/cache writes go to pytest's tmp_path so nothing lands in
app/storage and no state is shared between tests.
"""
import pytest
from fastapi.testclient import TestClient

from app import main
from app.mock_data import generate_mock_match
from app.storage.store import MatchStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.main.store", MatchStore(cache_path=tmp_path / "match.json"))
    return TestClient(main.app)


@pytest.fixture
def fake_pipeline(monkeypatch):
    def _install(fn):
        monkeypatch.setattr("app.main.run_real_pipeline", fn)

    return _install


def _upload_video(client, name="clip.mp4", content=b"fake"):
    return client.post("/api/upload", files={"file": (name, content, "video/mp4")})


def test_status_unknown_video_is_404(client):
    resp = client.get("/api/process/abcdef012345/status")
    assert resp.status_code == 404


def test_upload_rejects_non_video_extension(client):
    resp = client.post("/api/upload", files={"file": ("notes.txt", b"x", "text/plain")})
    assert resp.status_code == 415


def test_upload_process_status_success(client, fake_pipeline, tmp_path):
    calls = []

    def fake_run(video_path, match_id=None, **kwargs):
        calls.append((video_path, match_id))
        return generate_mock_match()

    fake_pipeline(fake_run)

    resp = _upload_video(client)
    assert resp.status_code == 200
    upload = resp.json()
    video_id = upload["video_id"]
    assert upload["filename"] == "clip.mp4"

    resp = client.post("/api/process", json={"video_id": video_id, "mock": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "cv_pipeline"
    assert body["status"] == "processing"
    assert body["match_id"] == f"cv-{video_id}"

    # BackgroundTasks run before TestClient returns, so status is final here.
    resp = client.get(f"/api/process/{video_id}/status")
    assert resp.status_code == 200
    status = resp.json()
    assert status["status"] == "completed"
    assert status["match_id"] == f"cv-{video_id}"
    assert status["error"] is None

    assert len(calls) == 1
    assert calls[0][1] == f"cv-{video_id}"
    assert calls[0][0].parent == tmp_path


def test_failing_pipeline_marks_job_failed(client, fake_pipeline):
    def fake_run(video_path, match_id=None, **kwargs):
        raise RuntimeError("boom")

    fake_pipeline(fake_run)

    video_id = _upload_video(client).json()["video_id"]
    resp = client.post("/api/process", json={"video_id": video_id, "mock": False})
    assert resp.status_code == 200
    assert resp.json()["status"] == "processing"

    resp = client.get(f"/api/process/{video_id}/status")
    assert resp.status_code == 200
    status = resp.json()
    assert status["status"] == "failed"
    assert "boom" in status["error"]


def test_oversized_upload_is_rejected_and_removed(client, monkeypatch, tmp_path):
    monkeypatch.setattr("app.main.MAX_UPLOAD_SIZE_BYTES", 10)

    resp = _upload_video(client, content=b"x" * 20)
    assert resp.status_code == 413

    leftover = [p for p in tmp_path.iterdir() if p.name != "match.json"]
    assert leftover == []
