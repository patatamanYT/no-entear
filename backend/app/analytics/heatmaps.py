"""
Player/team positional heatmaps.

Builds a HEATMAP_ROWS (Y) x HEATMAP_COLS (X) matrix at 1m resolution — 40x60
for the fútbol 7 pitch this app targets — from a set of pitch-coordinate
samples, using a Gaussian-blurred 2D histogram (robust to sparse/degenerate
point sets, unlike `scipy.stats.gaussian_kde` which can be singular on
collinear or near-duplicate points).

Only numpy/scipy are required — these are part of the core (non-lazy) mock
flow dependency set, so they're imported normally at module level.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

from app.schemas import HEATMAP_COLS, HEATMAP_ROWS, PITCH_LENGTH_M, PITCH_WIDTH_M

DEFAULT_SIGMA = 2.0  # smoothing kernel std-dev, in meters/bins


def compute_heatmap(
    points_xy: Sequence[Tuple[float, float]], sigma: float = DEFAULT_SIGMA
) -> List[List[float]]:
    """Build a HEATMAP_ROWS x HEATMAP_COLS matrix (Y rows, X cols) from
    (x, y) pitch-coordinate samples, normalized to [0, 1]."""
    grid = np.zeros((HEATMAP_ROWS, HEATMAP_COLS), dtype=np.float64)

    pts = np.asarray(points_xy, dtype=np.float64) if len(points_xy) else np.empty((0, 2))
    if pts.size == 0:
        return grid.tolist()

    xs = np.clip(pts[:, 0], 0.0, PITCH_LENGTH_M - 1e-6)
    ys = np.clip(pts[:, 1], 0.0, PITCH_WIDTH_M - 1e-6)
    col_idx = np.clip(np.floor(xs).astype(int), 0, HEATMAP_COLS - 1)
    row_idx = np.clip(np.floor(ys).astype(int), 0, HEATMAP_ROWS - 1)

    np.add.at(grid, (row_idx, col_idx), 1.0)

    smoothed = gaussian_filter(grid, sigma=sigma)
    max_val = smoothed.max()
    if max_val > 0:
        smoothed = smoothed / max_val

    return smoothed.tolist()


def compute_all_heatmaps(
    frames: Sequence[dict], players: Sequence[dict], sigma: float = DEFAULT_SIGMA
) -> Dict[str, List[List[float]]]:
    """Build the full `heatmaps` dict for a match: one entry per player
    (`player_<id>`) plus per-team aggregates (`team_A`, `team_B`)."""
    team_of_player = {p["id"]: p.get("team") for p in players}

    points_by_player: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
    points_by_team: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    for f in frames:
        for pf in f["players"]:
            pid = pf["id"]
            xy = (pf["x"], pf["y"])
            points_by_player[pid].append(xy)
            team = team_of_player.get(pid)
            if team in ("A", "B"):
                points_by_team[team].append(xy)

    heatmaps: Dict[str, List[List[float]]] = {}
    for p in players:
        pid = p["id"]
        heatmaps[f"player_{pid}"] = compute_heatmap(points_by_player.get(pid, []), sigma=sigma)

    for team in ("A", "B"):
        heatmaps[f"team_{team}"] = compute_heatmap(points_by_team.get(team, []), sigma=sigma)

    return heatmaps
