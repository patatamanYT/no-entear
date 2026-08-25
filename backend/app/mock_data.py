"""
Synthetic match generator.

Produces a realistic ~30 second, ~10 fps synthetic fútbol 7 (7-a-side) match:
2 teams of 7 players in a 1-2-3-1 formation + 1 referee, on a 60x40m pitch,
with smooth noise-perturbed formation movement and a continuous ball
trajectory that moves between players' feet with occasional fast passes and
a handful of shots on goal.

Passes, shots, and heatmaps are DERIVED from the simulated trajectories by
running them through `app.analytics.events` and `app.analytics.heatmaps` —
they are not hand-authored, so this both produces plausible data and
exercises the analytics modules.

Runnable as a CLI:
    python -m app.mock_data
writes `app/storage/mock_match.json` and exits 0. No network or model
weights required — only numpy/scipy/pydantic (already required for the core
app to run at all).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter1d

from app.analytics.events import GOAL_Y_CENTER, compute_events
from app.analytics.heatmaps import compute_all_heatmaps
from app.schemas import PITCH_LENGTH_M, PITCH_WIDTH_M, MatchData

STORAGE_DIR = Path(__file__).parent / "storage"
MOCK_MATCH_PATH = STORAGE_DIR / "mock_match.json"

DEFAULT_N_FRAMES = 300
DEFAULT_FPS = 10.0
DEFAULT_SEED = 42

TEAM_COLORS = {"A": "#e63946", "B": "#1d3557"}
TEAM_NAMES = {"A": "Home FC", "B": "Away United"}

# Fútbol 7 1-2-3-1 formation (GK + 2 DF + 3 MF + 1 FW), defined for the side
# that defends X=0 / attacks X=60 on a 60x40m pitch.
# (role, x, y) — mirrored (60 - x, y) for the side attacking X=0.
_FORMATION_1231: List[Tuple[str, float, float]] = [
    ("GK", 4.0, 20.0),
    ("DF", 14.0, 10.0),
    ("DF", 14.0, 30.0),
    ("MF", 28.0, 8.0),
    ("MF", 26.0, 20.0),
    ("MF", 28.0, 32.0),
    ("FW", 45.0, 20.0),
]


def _build_roster() -> Tuple[List[dict], Dict[str, Tuple[float, float]], Dict[str, str], Dict[str, str]]:
    """Returns (players_meta, base_positions, roles, team_of)."""
    players_meta: List[dict] = []
    base_positions: Dict[str, Tuple[float, float]] = {}
    roles: Dict[str, str] = {}
    team_of: Dict[str, str] = {}

    for side in ("A", "B"):
        for jersey, (role, x, y) in enumerate(_FORMATION_1231, start=1):
            pid = f"{side}{jersey}"
            bx = x if side == "A" else PITCH_LENGTH_M - x
            by = y
            players_meta.append(
                {"id": pid, "team": side, "jersey_number": jersey, "name": f"Player {pid}"}
            )
            base_positions[pid] = (bx, by)
            roles[pid] = role
            team_of[pid] = side

    ref_id = "REF"
    players_meta.append(
        {"id": ref_id, "team": "REF", "jersey_number": 0, "name": "Referee"}
    )
    base_positions[ref_id] = (PITCH_LENGTH_M / 2, PITCH_WIDTH_M / 2)
    roles[ref_id] = "REF"
    team_of[ref_id] = "REF"

    return players_meta, base_positions, roles, team_of


def _smoothed_walk(rng: np.random.Generator, n_frames: int, sigma: float, span: float) -> np.ndarray:
    """A zero-mean, low-frequency random walk bounded to roughly +/-span/2,
    used to add plausible organic drift on top of each player's formation
    position without letting them wander off unboundedly."""
    steps = rng.normal(0.0, 0.4, size=n_frames)
    walk = np.cumsum(steps)
    # Detrend so the walk returns near its start (keeps players near their
    # formation slot over the whole clip instead of drifting away).
    walk = walk - np.linspace(walk[0], walk[-1], n_frames)
    walk = gaussian_filter1d(walk, sigma=sigma)
    rng_span = walk.max() - walk.min()
    if rng_span > 1e-6:
        walk = (walk - walk.mean()) / rng_span * span
    else:
        walk = np.zeros(n_frames)
    return walk


def _simulate_player_trajectories(
    base_positions: Dict[str, Tuple[float, float]],
    n_frames: int,
    fps: float,
    rng: np.random.Generator,
) -> Dict[str, np.ndarray]:
    dt = 1.0 / fps
    t = np.arange(n_frames) * dt
    traj: Dict[str, np.ndarray] = {}

    for pid, (bx, by) in base_positions.items():
        freq = rng.uniform(0.04, 0.12)
        phase_x = rng.uniform(0, 2 * math.pi)
        phase_y = rng.uniform(0, 2 * math.pi)
        amp_x = rng.uniform(2.0, 5.5)
        amp_y = rng.uniform(2.0, 5.5)

        walk_x = _smoothed_walk(rng, n_frames, sigma=15.0, span=7.0)
        walk_y = _smoothed_walk(rng, n_frames, sigma=15.0, span=7.0)

        x = bx + amp_x * np.sin(2 * math.pi * freq * t + phase_x) + walk_x
        y = by + amp_y * np.cos(2 * math.pi * freq * t + phase_y) + walk_y

        x = np.clip(x, 1.0, PITCH_LENGTH_M - 1.0)
        y = np.clip(y, 1.0, PITCH_WIDTH_M - 1.0)
        traj[pid] = np.stack([x, y], axis=1)

    return traj


def _player_speeds(traj: np.ndarray, dt: float) -> np.ndarray:
    n = traj.shape[0]
    speeds = np.zeros(n)
    if n >= 2:
        diffs = traj[1:] - traj[:-1]
        step_speeds = np.hypot(diffs[:, 0], diffs[:, 1]) / dt
        speeds[:-1] = step_speeds
        speeds[-1] = step_speeds[-1]
    return speeds


def _simulate_ball_trajectory(
    player_traj: Dict[str, np.ndarray],
    roles: Dict[str, str],
    team_of: Dict[str, str],
    n_frames: int,
    fps: float,
    rng: np.random.Generator,
) -> np.ndarray:
    dt = 1.0 / fps
    ball = np.zeros((n_frames, 2))

    outfield_ids = [pid for pid, tm in team_of.items() if tm in ("A", "B")]

    # Kick off with a central midfielder.
    kickoff_candidates = [pid for pid in outfield_ids if roles[pid] == "MF" and team_of[pid] == "A"]
    possessor = kickoff_candidates[0] if kickoff_candidates else outfield_ids[0]

    frame = 0
    while frame < n_frames:
        hold_frames = int(rng.integers(8, 20))
        end = min(frame + hold_frames, n_frames)
        for f in range(frame, end):
            px, py = player_traj[possessor][f]
            ball[f] = (px + rng.normal(0, 0.12), py + rng.normal(0, 0.12))
        frame = end
        if frame >= n_frames:
            break

        role = roles[possessor]
        team = team_of[possessor]
        attacking_dir = 1 if team == "A" else -1
        goal_x = PITCH_LENGTH_M if attacking_dir == 1 else 0.0
        cur = ball[frame - 1].copy()
        dist_to_goal = abs(goal_x - cur[0])

        shoot_prob = 0.0
        if role == "FW" and dist_to_goal < 18:
            shoot_prob = 0.40
        elif role == "MF" and dist_to_goal < 13:
            shoot_prob = 0.15

        if rng.random() < shoot_prob:
            # --- shot ---
            target_y = float(np.clip(rng.normal(GOAL_Y_CENTER, 7.0), 4.0, PITCH_WIDTH_M - 4.0))
            speed = rng.uniform(14.0, 24.0)
            distance = math.hypot(goal_x - cur[0], target_y - cur[1])
            n_shot = max(1, int(round((distance / speed) / dt)))
            end_f = min(frame + n_shot, n_frames)
            count = end_f - frame
            if count > 0:
                xs = np.linspace(cur[0], goal_x, n_shot + 1)[1 : count + 1]
                ys = np.linspace(cur[1], target_y, n_shot + 1)[1 : count + 1]
                ball[frame:end_f] = np.stack([xs, ys], axis=1)
            frame = end_f
            if frame >= n_frames:
                break

            landing = ball[frame - 1].copy()
            nearest = min(
                outfield_ids,
                key=lambda pid: math.hypot(
                    player_traj[pid][frame][0] - landing[0],
                    player_traj[pid][frame][1] - landing[1],
                ),
            )
            recover_frames = int(rng.integers(6, 14))
            end_f2 = min(frame + recover_frames, n_frames)
            cnt = end_f2 - frame
            if cnt > 0:
                target_pos = player_traj[nearest][end_f2 - 1]
                xs2 = np.linspace(landing[0], target_pos[0], cnt + 1)[1:]
                ys2 = np.linspace(landing[1], target_pos[1], cnt + 1)[1:]
                ball[frame:end_f2] = np.stack([xs2, ys2], axis=1)
            frame = end_f2
            possessor = nearest
        else:
            # --- pass ---
            same_team = [
                pid for pid in outfield_ids if team_of[pid] == team and pid != possessor
            ]
            other_team = [pid for pid in outfield_ids if team_of[pid] != team]
            pool = same_team if (rng.random() < 0.85 and same_team) else (other_team or same_team)

            dists = sorted(
                pool,
                key=lambda pid: math.hypot(
                    player_traj[pid][frame][0] - cur[0], player_traj[pid][frame][1] - cur[1]
                ),
            )
            top_n = min(len(dists), 3)
            target = dists[int(rng.integers(0, top_n))]

            speed = rng.uniform(7.0, 16.0)
            lookahead = min(frame + 10, n_frames - 1)
            target_pos = player_traj[target][lookahead]
            distance = math.hypot(target_pos[0] - cur[0], target_pos[1] - cur[1])
            n_pass = max(1, int(round((distance / speed) / dt)))
            end_f = min(frame + n_pass, n_frames)
            count = end_f - frame
            if count > 0:
                xs = np.linspace(cur[0], target_pos[0], n_pass + 1)[1 : count + 1]
                ys = np.linspace(cur[1], target_pos[1], n_pass + 1)[1 : count + 1]
                ball[frame:end_f] = np.stack([xs, ys], axis=1)
            frame = end_f
            possessor = target

    return ball


def generate_mock_match(
    n_frames: int = DEFAULT_N_FRAMES,
    fps: float = DEFAULT_FPS,
    seed: Optional[int] = DEFAULT_SEED,
    match_id: str = "mock-match-001",
) -> MatchData:
    """Generate a full synthetic match and validate it against schemas.MatchData."""
    rng = np.random.default_rng(seed)
    dt = 1.0 / fps

    players_meta, base_positions, roles, team_of = _build_roster()
    player_traj = _simulate_player_trajectories(base_positions, n_frames, fps, rng)
    ball_traj = _simulate_ball_trajectory(player_traj, roles, team_of, n_frames, fps, rng)

    speeds = {pid: _player_speeds(traj, dt) for pid, traj in player_traj.items()}

    frames: List[dict] = []
    for i in range(n_frames):
        players_frame = [
            {
                "id": pid,
                "x": float(player_traj[pid][i, 0]),
                "y": float(player_traj[pid][i, 1]),
                "v": float(speeds[pid][i]),
            }
            for pid in player_traj.keys()
        ]
        frames.append(
            {
                "frame": i,
                "t": round(i * dt, 3),
                "ball": {"x": float(ball_traj[i, 0]), "y": float(ball_traj[i, 1])},
                "players": players_frame,
            }
        )

    passes, shots = compute_events(frames, players_meta)
    heatmaps = compute_all_heatmaps(frames, players_meta)

    match_data = {
        "meta": {
            "match_id": match_id,
            "duration_seconds": round((n_frames - 1) * dt, 3),
            "fps": fps,
            "pitch_length": PITCH_LENGTH_M,
            "pitch_width": PITCH_WIDTH_M,
            "video_url": None,
            "source": "mock",
        },
        "teams": {
            "A": {"name": TEAM_NAMES["A"], "color": TEAM_COLORS["A"]},
            "B": {"name": TEAM_NAMES["B"], "color": TEAM_COLORS["B"]},
        },
        "players": players_meta,
        "frames": frames,
        "passes": passes,
        "shots": shots,
        "heatmaps": heatmaps,
    }

    return MatchData(**match_data)


def save_mock_match(match: Optional[MatchData] = None, path: Path = MOCK_MATCH_PATH) -> Path:
    if match is None:
        match = generate_mock_match()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(match.model_dump_json(indent=2))
    return path


def main() -> int:
    match = generate_mock_match()
    out_path = save_mock_match(match)
    print(
        f"Generated mock match '{match.meta.match_id}': "
        f"{len(match.frames)} frames, {len(match.players)} players, "
        f"{len(match.passes)} passes, {len(match.shots)} shots, "
        f"{len(match.heatmaps)} heatmaps -> {out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
