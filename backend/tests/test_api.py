from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_match_data_auto_mocks_on_first_call():
    resp = client.get("/api/match-data")
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["source"] == "mock"
    assert len(data["frames"]) > 0
    assert "heatmaps" in data
    assert len(data["heatmaps"]) > 0


def test_process_mock():
    resp = client.post("/api/process", json={"mock": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "mock"
    assert data["status"] == "completed"


def test_process_missing_video_id_errors():
    resp = client.post("/api/process", json={"mock": False, "video_id": "does-not-exist"})
    assert resp.status_code == 404
