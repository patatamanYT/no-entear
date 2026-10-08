from fastapi.testclient import TestClient

from app.config import _env_list
from app.main import app

client = TestClient(app)


def test_cors_allows_configured_origin():
    resp = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_rejects_unlisted_origin():
    resp = client.get("/api/health", headers={"Origin": "http://evil.example"})
    assert resp.status_code == 200
    assert "access-control-allow-origin" not in resp.headers


def test_env_list_splits_and_strips(monkeypatch):
    monkeypatch.setenv("TEST_CORS_LIST", " a , b ,, ")
    assert _env_list("TEST_CORS_LIST", ["x"]) == ["a", "b"]


def test_env_list_unset_returns_default_copy(monkeypatch):
    monkeypatch.delenv("TEST_CORS_LIST", raising=False)
    default = ["x", "y"]
    result = _env_list("TEST_CORS_LIST", default)
    assert result == ["x", "y"]
    assert result is not default


def test_env_list_blank_returns_default(monkeypatch):
    monkeypatch.setenv("TEST_CORS_LIST", "   ")
    assert _env_list("TEST_CORS_LIST", ["x"]) == ["x"]
