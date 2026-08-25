"""
Pure-function analytics: possession tracking, pass detection, and shot
detection over a sequence of per-frame player + ball pitch coordinates.

Operates on plain dicts shaped like `schemas.Frame` / `schemas.PlayerMeta`
(or their `.dict()` output) so it runs identically over synthetic mock
frames and real CV-pipeline output. No heavy dependencies required — only
the standard library and numpy.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from app.schemas import (
    GOAL_Y_MAX,
    GOAL_Y_MIN,
    PITCH_LENGTH_M,
    PITCH_WIDTH_M,
)

POSSESSION_RADIUS_M = 1.2
PASS_VELOCITY_THRESHOLD_MS = 4.0
SHOT_VELOCITY_THRESHOLD_MS = 12.0
SHOT_MAX_RANGE_M = 45.0
BLOCK_DISTANCE_M = 1.0
GOAL_Y_CENTER = (GOAL_Y_MIN + GOAL_Y_MAX) / 2.0
GOAL_MOUTH_WIDTH = GOAL_Y_MAX - GOAL_Y_MIN


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _point_segment_distance(
    p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]
) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return _dist(p, a)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return _dist(p, (cx, cy))


# ---------------------------------------------------------------------------
# Ball kinematics + possession
# ---------------------------------------------------------------------------

def compute_ball_kinematics(
    frames: Sequence[dict],
) -> List[Tuple[float, float, float]]:
    """Per-frame (vx, vy, speed) in m/s describing the ball's velocity moving
    FROM this frame's ball position to the next frame's. The final frame
    repeats the previous velocity (or is zero if fewer than 2 frames)."""
    n = len(frames)
    result: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)] * n
    for i in range(n - 1):
        f0, f1 = frames[i], frames[i + 1]
        dt = f1["t"] - f0["t"]
        if dt <= 0:
            continue
        dx = f1["ball"]["x"] - f0["ball"]["x"]
        dy = f1["ball"]["y"] - f0["ball"]["y"]
        vx, vy = dx / dt, dy / dt
        result[i] = (vx, vy, math.hypot(vx, vy))
    if n >= 2:
        result[-1] = result[-2]
    return result


def compute_possession(
    frames: Sequence[dict], radius: float = POSSESSION_RADIUS_M
) -> List[Optional[str]]:
    """For each frame, the id of the player within `radius` meters of the ball
    (closest such player), or None if no player is close enough."""
    possessors: List[Optional[str]] = []
    for f in frames:
        ball = (f["ball"]["x"], f["ball"]["y"])
        best_id: Optional[str] = None
        best_dist = radius
        for p in f["players"]:
            d = _dist((p["x"], p["y"]), ball)
            if d <= best_dist:
                best_dist = d
                best_id = p["id"]
        possessors.append(best_id)
    return possessors


def _runs(possessors: Sequence[Optional[str]]) -> List[Tuple[int, int, Optional[str]]]:
    """Collapse a possessor-per-frame sequence into (start_idx, end_idx, id) runs."""
    runs: List[Tuple[int, int, Optional[str]]] = []
    n = len(possessors)
    i = 0
    while i < n:
        pid = possessors[i]
        j = i
        while j + 1 < n and possessors[j + 1] == pid:
            j += 1
        runs.append((i, j, pid))
        i = j + 1
    return runs


# ---------------------------------------------------------------------------
# Attacking direction inference
# ---------------------------------------------------------------------------

def infer_attacking_directions(
    frames: Sequence[dict], team_of_player: Dict[str, str]
) -> Dict[str, int]:
    """Infer +1 (attacks toward X=105) or -1 (attacks toward X=0) per team,
    from which half of the pitch each team's players spend most time in."""
    sums: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for f in frames:
        for p in f["players"]:
            team = team_of_player.get(p["id"])
            if team not in ("A", "B"):
                continue
            sums[team] = sums.get(team, 0.0) + p["x"]
            counts[team] = counts.get(team, 0) + 1

    avg_a = sums.get("A", 0.0) / counts["A"] if counts.get("A") else PITCH_LENGTH_M / 4
    avg_b = sums.get("B", 0.0) / counts["B"] if counts.get("B") else 3 * PITCH_LENGTH_M / 4

    if avg_a <= avg_b:
        return {"A": 1, "B": -1}
    return {"A": -1, "B": 1}


# ---------------------------------------------------------------------------
# Blocking check
# ---------------------------------------------------------------------------

def _is_blocked(
    frame: dict,
    team_of_player: Dict[str, str],
    shooter_id: str,
    shooter_team: Optional[str],
    start: Tuple[float, float],
    end: Tuple[float, float],
) -> bool:
    for p in frame["players"]:
        pid = p["id"]
        if pid == shooter_id:
            continue
        team = team_of_player.get(pid)
        if team is None or team == shooter_team:
            continue  # only opposing-team players can block
        d = _point_segment_distance((p["x"], p["y"]), start, end)
        if d < BLOCK_DISTANCE_M:
            return True
    return False


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_events(
    frames: Sequence[dict], players_meta: Sequence[dict]
) -> Tuple[List[dict], List[dict]]:
    """Compute (pass_events, shot_events) from a match's frame sequence.

    `frames` — list of dicts shaped like schemas.Frame.
    `players_meta` — list of dicts shaped like schemas.PlayerMeta (needs at
    least "id" and "team").

    Returns dicts matching schemas.PassEvent / schemas.ShotEvent field shapes
    (JSON-serializable primitives / nested dicts for Point2D fields).
    """
    if len(frames) < 2:
        return [], []

    team_of_player = {p["id"]: p["team"] for p in players_meta}
    directions = infer_attacking_directions(frames, team_of_player)

    possessors = compute_possession(frames)
    ball_kin = compute_ball_kinematics(frames)
    runs = _runs(possessors)
    player_runs = [r for r in runs if r[2] is not None]

    passes: List[dict] = []
    shots: List[dict] = []
    pass_counter = 0
    shot_counter = 0

    for idx, (start_i, end_i, pid) in enumerate(player_runs):
        team = team_of_player.get(pid)
        release_idx = end_i
        vx, vy, speed = ball_kin[release_idx]
        release_frame = frames[release_idx]
        release_pos = (release_frame["ball"]["x"], release_frame["ball"]["y"])

        emitted_shot = False

        direction = directions.get(team) if team else None
        if direction is not None and speed > SHOT_VELOCITY_THRESHOLD_MS:
            moving_toward_goal = (direction == 1 and vx > 0) or (
                direction == -1 and vx < 0
            )
            if moving_toward_goal and abs(vx) > 1e-3:
                goal_line_x = PITCH_LENGTH_M if direction == 1 else 0.0
                t_to_line = (goal_line_x - release_pos[0]) / vx
                dist_to_goal = abs(goal_line_x - release_pos[0])
                if t_to_line > 0 and dist_to_goal <= SHOT_MAX_RANGE_M:
                    endpoint_y = release_pos[1] + vy * t_to_line
                    endpoint_y_clamped = max(0.0, min(PITCH_WIDTH_M, endpoint_y))
                    end_point = (goal_line_x, endpoint_y_clamped)

                    if _is_blocked(release_frame, team_of_player, pid, team, release_pos, end_point):
                        outcome = "blocked"
                    elif GOAL_Y_MIN <= endpoint_y <= GOAL_Y_MAX:
                        if abs(endpoint_y - GOAL_Y_CENTER) <= GOAL_MOUTH_WIDTH * 0.3:
                            outcome = "goal"
                        else:
                            outcome = "on_target"
                    else:
                        outcome = "off_target"

                    shot_counter += 1
                    shots.append(
                        {
                            "id": f"shot_{shot_counter}",
                            "frame": release_frame["frame"],
                            "t": release_frame["t"],
                            "player": pid,
                            "team": team,
                            "start": {"x": release_pos[0], "y": release_pos[1]},
                            "end": {"x": end_point[0], "y": end_point[1]},
                            "outcome": outcome,
                            "velocity": speed,
                        }
                    )
                    emitted_shot = True

        if emitted_shot:
            continue

        if speed > PASS_VELOCITY_THRESHOLD_MS and idx + 1 < len(player_runs):
            next_start_i, _next_end_i, next_pid = player_runs[idx + 1]
            if next_pid == pid:
                continue
            to_team = team_of_player.get(next_pid)
            status = "completed" if to_team == team else "intercepted"
            next_frame = frames[next_start_i]

            pass_counter += 1
            passes.append(
                {
                    "id": f"pass_{pass_counter}",
                    "frame_start": release_frame["frame"],
                    "frame_end": next_frame["frame"],
                    "t_start": release_frame["t"],
                    "t_end": next_frame["t"],
                    "from_player": pid,
                    "to_player": next_pid,
                    "team": team,
                    "status": status,
                    "start": {"x": release_pos[0], "y": release_pos[1]},
                    "end": {"x": next_frame["ball"]["x"], "y": next_frame["ball"]["y"]},
                }
            )

    return passes, shots
