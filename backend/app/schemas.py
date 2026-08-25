"""
Shared data contract for the tactical analytics API.

IMPORTANT: This file is the source of truth for the JSON shape returned by
GET /api/match-data. The frontend TypeScript types in
frontend/src/types/match.ts MUST mirror this file exactly (field names,
optionality, enums). If you change this file, update that file too.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0
GOAL_Y_MIN = 30.66
GOAL_Y_MAX = 37.34

HEATMAP_COLS = 105  # X bins, 1m resolution
HEATMAP_ROWS = 68   # Y bins, 1m resolution


class Team(str, Enum):
    A = "A"
    B = "B"
    REF = "REF"


class PassStatus(str, Enum):
    completed = "completed"
    intercepted = "intercepted"


class ShotOutcome(str, Enum):
    goal = "goal"
    on_target = "on_target"
    off_target = "off_target"
    blocked = "blocked"


class Point2D(BaseModel):
    x: float
    y: float


class TeamInfo(BaseModel):
    name: str
    color: str  # hex color, e.g. "#3b82f6"


class TeamsInfo(BaseModel):
    A: TeamInfo
    B: TeamInfo


class PlayerMeta(BaseModel):
    id: str
    team: Team
    jersey_number: int
    name: str


class PlayerFrame(BaseModel):
    id: str
    x: float
    y: float
    v: float = 0.0  # speed in m/s


class BallFrame(BaseModel):
    x: float
    y: float


class Frame(BaseModel):
    frame: int
    t: float  # seconds from start
    ball: BallFrame
    players: List[PlayerFrame]


class PassEvent(BaseModel):
    id: str
    frame_start: int
    frame_end: int
    t_start: float
    t_end: float
    from_player: str
    to_player: Optional[str] = None
    team: Team
    status: PassStatus
    start: Point2D
    end: Point2D


class ShotEvent(BaseModel):
    id: str
    frame: int
    t: float
    player: str
    team: Team
    start: Point2D
    end: Point2D
    outcome: ShotOutcome
    velocity: float


class MatchMeta(BaseModel):
    match_id: str
    duration_seconds: float
    fps: float
    pitch_length: float = PITCH_LENGTH_M
    pitch_width: float = PITCH_WIDTH_M
    video_url: Optional[str] = None
    source: str = Field(description="'mock' or 'cv_pipeline'")


class MatchData(BaseModel):
    meta: MatchMeta
    teams: TeamsInfo
    players: List[PlayerMeta]
    frames: List[Frame]
    passes: List[PassEvent]
    shots: List[ShotEvent]
    heatmaps: dict[str, List[List[float]]] = Field(
        description="key -> matrix[HEATMAP_ROWS][HEATMAP_COLS], normalized 0..1. "
        "Keys: 'player_<id>' for each player, plus 'team_A' and 'team_B'."
    )


class UploadResponse(BaseModel):
    video_id: str
    filename: str


class ProcessRequest(BaseModel):
    video_id: Optional[str] = None
    mock: bool = True


class ProcessResponse(BaseModel):
    match_id: str
    source: str
    status: str
