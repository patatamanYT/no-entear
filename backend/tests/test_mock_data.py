from app.mock_data import generate_mock_match
from app.schemas import MatchData


def test_mock_match_validates_against_schema():
    match = generate_mock_match(n_frames=50, fps=10.0, seed=1)
    assert isinstance(match, MatchData)

    # Round-trips cleanly through the schema.
    data = match.model_dump(mode="json")
    revalidated = MatchData(**data)
    assert revalidated.meta.match_id == match.meta.match_id
    assert len(revalidated.frames) == len(match.frames)


def test_mock_match_shape():
    match = generate_mock_match(n_frames=50, fps=10.0, seed=1)

    assert len(match.players) == 15  # 7 + 7 + 1 referee (futbol 7)
    assert len(match.frames) == 50
    assert match.frames[0].frame == 0
    assert match.frames[-1].frame == 49

    team_a = [p for p in match.players if p.team == "A"]
    team_b = [p for p in match.players if p.team == "B"]
    refs = [p for p in match.players if p.team == "REF"]
    assert len(team_a) == 7
    assert len(team_b) == 7
    assert len(refs) == 1

    # heatmaps: one per player + team_A + team_B
    assert len(match.heatmaps) == 15 + 2
    for key, matrix in match.heatmaps.items():
        assert len(matrix) == 40
        assert len(matrix[0]) == 60
        assert all(0.0 <= v <= 1.0 for row in matrix for v in row)


def test_mock_match_events_are_plausible():
    match = generate_mock_match(n_frames=300, fps=10.0, seed=42)

    assert 0 <= len(match.shots) <= 30
    assert 0 <= len(match.passes) <= 200

    for p in match.passes:
        assert p.status in ("completed", "intercepted")
        assert p.from_player != p.to_player

    for s in match.shots:
        assert s.outcome in ("goal", "on_target", "off_target", "blocked")
        assert s.velocity > 12.0
