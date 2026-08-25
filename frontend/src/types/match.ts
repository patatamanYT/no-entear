/**
 * Shared data contract for the tactical analytics API.
 *
 * IMPORTANT: This file mirrors backend/app/schemas.py exactly (field names,
 * optionality, enums/unions). If you change one, update the other.
 */

export const PITCH_LENGTH_M = 105;
export const PITCH_WIDTH_M = 68;
export const GOAL_Y_MIN = 30.66;
export const GOAL_Y_MAX = 37.34;

export const HEATMAP_COLS = 105; // X bins, 1m resolution
export const HEATMAP_ROWS = 68; // Y bins, 1m resolution

export type Team = "A" | "B" | "REF";
export type PassStatus = "completed" | "intercepted";
export type ShotOutcome = "goal" | "on_target" | "off_target" | "blocked";

export interface Point2D {
  x: number;
  y: number;
}

export interface TeamInfo {
  name: string;
  color: string; // hex color
}

export interface TeamsInfo {
  A: TeamInfo;
  B: TeamInfo;
}

export interface PlayerMeta {
  id: string;
  team: Team;
  jersey_number: number;
  name: string;
}

export interface PlayerFrame {
  id: string;
  x: number;
  y: number;
  v: number; // speed m/s
}

export interface BallFrame {
  x: number;
  y: number;
}

export interface Frame {
  frame: number;
  t: number; // seconds
  ball: BallFrame;
  players: PlayerFrame[];
}

export interface PassEvent {
  id: string;
  frame_start: number;
  frame_end: number;
  t_start: number;
  t_end: number;
  from_player: string;
  to_player: string | null;
  team: Team;
  status: PassStatus;
  start: Point2D;
  end: Point2D;
}

export interface ShotEvent {
  id: string;
  frame: number;
  t: number;
  player: string;
  team: Team;
  start: Point2D;
  end: Point2D;
  outcome: ShotOutcome;
  velocity: number;
}

export interface MatchMeta {
  match_id: string;
  duration_seconds: number;
  fps: number;
  pitch_length: number;
  pitch_width: number;
  video_url: string | null;
  source: "mock" | "cv_pipeline";
}

export interface MatchData {
  meta: MatchMeta;
  teams: TeamsInfo;
  players: PlayerMeta[];
  frames: Frame[];
  passes: PassEvent[];
  shots: ShotEvent[];
  /** key -> matrix[HEATMAP_ROWS][HEATMAP_COLS], normalized 0..1.
   *  Keys: `player_<id>` for each player, plus `team_A` and `team_B`. */
  heatmaps: Record<string, number[][]>;
}

export interface UploadResponse {
  video_id: string;
  filename: string;
}

export interface ProcessRequest {
  video_id?: string | null;
  mock?: boolean;
}

export interface ProcessResponse {
  match_id: string;
  source: string;
  status: string;
}
