from app.analytics.events import compute_events


def _player(pid, x, y, v=0.0):
    return {"id": pid, "x": x, "y": y, "v": v}


def test_completed_pass_same_team():
    players_meta = [
        {"id": "A1", "team": "A", "jersey_number": 1, "name": "A1"},
        {"id": "A2", "team": "A", "jersey_number": 2, "name": "A2"},
    ]
    frames = [
        {"frame": 0, "t": 0.0, "ball": {"x": 10, "y": 34}, "players": [_player("A1", 10, 34), _player("A2", 20, 34)]},
        {"frame": 1, "t": 0.1, "ball": {"x": 10, "y": 34}, "players": [_player("A1", 10, 34), _player("A2", 20, 34)]},
        {"frame": 2, "t": 0.2, "ball": {"x": 16, "y": 34}, "players": [_player("A1", 10, 34), _player("A2", 20, 34)]},
        {"frame": 3, "t": 0.3, "ball": {"x": 20, "y": 34}, "players": [_player("A1", 10, 34), _player("A2", 20, 34)]},
    ]

    passes, shots = compute_events(frames, players_meta)

    assert shots == []
    assert len(passes) == 1
    p = passes[0]
    assert p["from_player"] == "A1"
    assert p["to_player"] == "A2"
    assert p["status"] == "completed"
    assert p["team"] == "A"


def test_intercepted_pass_opposing_team():
    players_meta = [
        {"id": "A1", "team": "A", "jersey_number": 1, "name": "A1"},
        {"id": "B1", "team": "B", "jersey_number": 1, "name": "B1"},
    ]
    frames = [
        {"frame": 0, "t": 0.0, "ball": {"x": 10, "y": 34}, "players": [_player("A1", 10, 34), _player("B1", 20, 34)]},
        {"frame": 1, "t": 0.1, "ball": {"x": 10, "y": 34}, "players": [_player("A1", 10, 34), _player("B1", 20, 34)]},
        {"frame": 2, "t": 0.2, "ball": {"x": 16, "y": 34}, "players": [_player("A1", 10, 34), _player("B1", 20, 34)]},
        {"frame": 3, "t": 0.3, "ball": {"x": 20, "y": 34}, "players": [_player("A1", 10, 34), _player("B1", 20, 34)]},
    ]

    passes, shots = compute_events(frames, players_meta)

    assert shots == []
    assert len(passes) == 1
    p = passes[0]
    assert p["from_player"] == "A1"
    assert p["to_player"] == "B1"
    assert p["status"] == "intercepted"


def test_shot_toward_goal_scores():
    # Fútbol 7 pitch: 60x40m, goal mouth Y in [17, 23], goal line at X=60.
    players_meta = [
        {"id": "A9", "team": "A", "jersey_number": 9, "name": "A9"},
        {"id": "B1", "team": "B", "jersey_number": 1, "name": "B1"},
    ]
    frames = [
        {"frame": 0, "t": 0.0, "ball": {"x": 50, "y": 20}, "players": [_player("A9", 50, 20), _player("B1", 55, 5)]},
        {"frame": 1, "t": 0.1, "ball": {"x": 50, "y": 20}, "players": [_player("A9", 50, 20), _player("B1", 55, 5)]},
        {"frame": 2, "t": 0.2, "ball": {"x": 54, "y": 20}, "players": [_player("A9", 50, 20), _player("B1", 55, 5)]},
        {"frame": 3, "t": 0.3, "ball": {"x": 58, "y": 20}, "players": [_player("A9", 50, 20), _player("B1", 55, 5)]},
    ]

    passes, shots = compute_events(frames, players_meta)

    assert len(shots) == 1
    shot = shots[0]
    assert shot["player"] == "A9"
    assert shot["team"] == "A"
    assert shot["outcome"] == "goal"
    assert shot["velocity"] > 12.0


def test_no_events_on_static_ball():
    players_meta = [
        {"id": "A1", "team": "A", "jersey_number": 1, "name": "A1"},
    ]
    frames = [
        {"frame": i, "t": i * 0.1, "ball": {"x": 50, "y": 34}, "players": [_player("A1", 50, 34)]}
        for i in range(5)
    ]
    passes, shots = compute_events(frames, players_meta)
    assert passes == []
    assert shots == []
