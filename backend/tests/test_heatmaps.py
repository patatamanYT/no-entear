from app.analytics.heatmaps import compute_all_heatmaps, compute_heatmap
from app.schemas import HEATMAP_COLS, HEATMAP_ROWS


def test_compute_heatmap_shape_and_range():
    points = [(10.0, 15.0), (10.5, 15.5), (11.0, 14.5), (30.0, 20.0)]
    matrix = compute_heatmap(points)
    assert len(matrix) == HEATMAP_ROWS == 40
    assert all(len(row) == HEATMAP_COLS == 60 for row in matrix)
    flat = [v for row in matrix for v in row]
    assert max(flat) == 1.0  # normalized
    assert all(0.0 <= v <= 1.0 for v in flat)


def test_compute_heatmap_empty_points():
    matrix = compute_heatmap([])
    assert len(matrix) == 40
    assert len(matrix[0]) == 60
    assert all(v == 0.0 for row in matrix for v in row)


def test_compute_all_heatmaps_keys_and_shapes():
    players = [
        {"id": "A1", "team": "A", "jersey_number": 1, "name": "Player A1"},
        {"id": "B1", "team": "B", "jersey_number": 1, "name": "Player B1"},
    ]
    frames = [
        {
            "frame": i,
            "t": i * 0.1,
            "ball": {"x": 30.0, "y": 20.0},
            "players": [
                {"id": "A1", "x": 10.0 + i, "y": 12.0, "v": 1.0},
                {"id": "B1", "x": 50.0 - i, "y": 25.0, "v": 1.0},
            ],
        }
        for i in range(5)
    ]

    heatmaps = compute_all_heatmaps(frames, players)

    assert set(heatmaps.keys()) == {"player_A1", "player_B1", "team_A", "team_B"}
    for matrix in heatmaps.values():
        assert len(matrix) == 40
        assert len(matrix[0]) == 60
        for row in matrix:
            for v in row:
                assert 0.0 <= v <= 1.0
