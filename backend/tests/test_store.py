from pathlib import Path

import pytest

from app.storage.store import MatchStore


def _store(tmp_path: Path) -> MatchStore:
    return MatchStore(cache_path=tmp_path / "m.json", uploads_dir=tmp_path)


def test_fresh_store_finds_preexisting_upload_on_disk(tmp_path):
    f = tmp_path / "abcdef012345_clip.mp4"
    f.write_bytes(b"fake video")

    store = _store(tmp_path)

    assert store.get_upload_path("abcdef012345") == f


def test_unknown_valid_id_returns_none(tmp_path):
    (tmp_path / "abcdef012345_clip.mp4").write_bytes(b"x")

    store = _store(tmp_path)

    assert store.get_upload_path("000000000000") is None


@pytest.mark.parametrize("bad_id", ["../etc", "*", "abc", "ABCDEF012345", "abcdef012345/x", ""])
def test_malicious_or_malformed_ids_return_none(tmp_path, bad_id):
    (tmp_path / "abcdef012345_clip.mp4").write_bytes(b"x")
    (tmp_path / "secret_file.txt").write_bytes(b"x")

    store = _store(tmp_path)

    assert store.get_upload_path(bad_id) is None


def test_in_memory_registration_still_works(tmp_path):
    path = tmp_path / "111111111111_match.mp4"
    path.write_bytes(b"x")

    store = _store(tmp_path)
    resp = store.register_upload("111111111111", "match.mp4", path)

    assert resp.video_id == "111111111111"
    assert resp.filename == "match.mp4"
    assert store.get_upload_path("111111111111") == path


def test_directory_entries_are_not_treated_as_uploads(tmp_path):
    (tmp_path / "bbbbbbbbbbbb_dir").mkdir()

    store = _store(tmp_path)

    assert store.get_upload_path("bbbbbbbbbbbb") is None
