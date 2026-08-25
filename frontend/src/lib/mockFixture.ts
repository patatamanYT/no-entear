/**
 * Static, schema-valid MatchData fixture used for local development and as
 * the graceful fallback when the backend is unreachable. ~8 seconds at 5fps
 * (40 frames), 11 players (5v5 + referee), 3 passes (2 completed, 1
 * intercepted), 1 shot (goal), and per-player/per-team heatmaps built as
 * simple Gaussian occupancy blobs around each player's average position.
 *
 * This is deliberately hand-authored (waypoints, roster, event script) with
 * small deterministic generator functions filling in the dense per-frame /
 * per-cell arrays the schema requires — not randomized, not fetched.
 */

import {
  GOAL_Y_MAX,
  GOAL_Y_MIN,
  HEATMAP_COLS,
  HEATMAP_ROWS,
  MatchData,
  PITCH_LENGTH_M,
  PITCH_WIDTH_M,
  PlayerMeta,
  Point2D,
} from "@/types/match";

const FPS = 5;
const FRAME_COUNT = 40; // 0..39 -> t = 0.0 .. 7.8s
const DT = 1 / FPS;

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}

// --- Roster -----------------------------------------------------------

interface RosterEntry extends PlayerMeta {
  base: Point2D;
  ampX: number;
  ampY: number;
  freq: number;
  phase: number;
}

const roster: RosterEntry[] = [
  { id: "a1", team: "A", jersey_number: 1, name: "A. Keeper", base: { x: 5, y: 34 }, ampX: 1.5, ampY: 2, freq: 0.4, phase: 0 },
  { id: "a2", team: "A", jersey_number: 2, name: "A. Rios", base: { x: 20, y: 20 }, ampX: 4, ampY: 3, freq: 0.55, phase: 0.6 },
  { id: "a3", team: "A", jersey_number: 3, name: "A. Diallo", base: { x: 20, y: 48 }, ampX: 4, ampY: 5, freq: 0.5, phase: 1.4 },
  { id: "a4", team: "A", jersey_number: 8, name: "A. Silva", base: { x: 40, y: 34 }, ampX: 6, ampY: 4, freq: 0.6, phase: 2.1 },
  { id: "a5", team: "A", jersey_number: 9, name: "A. Torres", base: { x: 55, y: 34 }, ampX: 6, ampY: 6, freq: 0.65, phase: 0.3 },
  { id: "b1", team: "B", jersey_number: 1, name: "B. Keeper", base: { x: 100, y: 34 }, ampX: 1.5, ampY: 2, freq: 0.4, phase: 0.2 },
  { id: "b2", team: "B", jersey_number: 4, name: "B. Novak", base: { x: 85, y: 20 }, ampX: 4, ampY: 3, freq: 0.5, phase: 1.1 },
  { id: "b3", team: "B", jersey_number: 5, name: "B. Costa", base: { x: 85, y: 48 }, ampX: 4, ampY: 5, freq: 0.55, phase: 2.4 },
  { id: "b4", team: "B", jersey_number: 6, name: "B. Haas", base: { x: 65, y: 34 }, ampX: 8, ampY: 5, freq: 0.6, phase: 0.9 },
  { id: "b5", team: "B", jersey_number: 11, name: "B. Yilmaz", base: { x: 50, y: 30 }, ampX: 6, ampY: 5, freq: 0.7, phase: 1.8 },
  { id: "r1", team: "REF", jersey_number: 0, name: "Referee", base: { x: 52, y: 40 }, ampX: 10, ampY: 6, freq: 0.3, phase: 0.5 },
];

// --- Ball waypoints (frame index -> pitch position) --------------------
// Scripted so the ball's motion lines up with the passes/shot below.
const ballWaypoints: Array<[number, number, number]> = [
  [0, 40, 34],
  [9, 40, 34],
  [10, 40, 34], // pass 1 start (a4 -> a5)
  [14, 55, 34], // pass 1 end
  [19, 60, 30], // dribble
  [20, 60, 30], // pass 2 start (a5 -> a3)
  [24, 20, 48], // pass 2 end
  [25, 20, 48], // pass 3 start (a3 -> a4, intercepted)
  [28, 55, 36], // intercepted by b4
  [34, 50, 30], // counter to b5
  [35, 50, 30], // shot start
  [36, 37, 32],
  [37, 25, 33],
  [38, 12, 33.5],
  [39, 0, 34], // goal
];

function ballAt(frame: number): Point2D {
  let lo = ballWaypoints[0];
  let hi = ballWaypoints[ballWaypoints.length - 1];
  for (let i = 0; i < ballWaypoints.length - 1; i++) {
    if (frame >= ballWaypoints[i][0] && frame <= ballWaypoints[i + 1][0]) {
      lo = ballWaypoints[i];
      hi = ballWaypoints[i + 1];
      break;
    }
  }
  const [f0, x0, y0] = lo;
  const [f1, x1, y1] = hi;
  const t = f1 === f0 ? 0 : (frame - f0) / (f1 - f0);
  return { x: x0 + (x1 - x0) * t, y: y0 + (y1 - y0) * t };
}

function playerAt(p: RosterEntry, frame: number): { x: number; y: number; v: number } {
  const t = frame * DT;
  const dx = Math.sin(t * p.freq * Math.PI * 2 + p.phase) * p.ampX;
  const dy = Math.cos(t * p.freq * Math.PI * 2 * 0.8 + p.phase) * p.ampY;
  const x = clamp(p.base.x + dx, 1, PITCH_LENGTH_M - 1);
  const y = clamp(p.base.y + dy, 1, PITCH_WIDTH_M - 1);
  const vx = Math.cos(t * p.freq * Math.PI * 2 + p.phase) * p.ampX * p.freq * Math.PI * 2;
  const vy = -Math.sin(t * p.freq * Math.PI * 2 * 0.8 + p.phase) * p.ampY * p.freq * Math.PI * 2 * 0.8;
  const v = Math.sqrt(vx * vx + vy * vy);
  return { x, y, v: Math.round(v * 100) / 100 };
}

const frames: MatchData["frames"] = Array.from({ length: FRAME_COUNT }, (_, i) => {
  const t = Math.round(i * DT * 100) / 100;
  return {
    frame: i,
    t,
    ball: ballAt(i),
    players: roster.map((p) => {
      const { x, y, v } = playerAt(p, i);
      return { id: p.id, x: Math.round(x * 100) / 100, y: Math.round(y * 100) / 100, v };
    }),
  };
});

// --- Events --------------------------------------------------------------

const passes: MatchData["passes"] = [
  {
    id: "pass-1",
    frame_start: 10,
    frame_end: 14,
    t_start: 2.0,
    t_end: 2.8,
    from_player: "a4",
    to_player: "a5",
    team: "A",
    status: "completed",
    start: { x: 40, y: 34 },
    end: { x: 55, y: 34 },
  },
  {
    id: "pass-2",
    frame_start: 20,
    frame_end: 24,
    t_start: 4.0,
    t_end: 4.8,
    from_player: "a5",
    to_player: "a3",
    team: "A",
    status: "completed",
    start: { x: 60, y: 30 },
    end: { x: 20, y: 48 },
  },
  {
    id: "pass-3",
    frame_start: 25,
    frame_end: 28,
    t_start: 5.0,
    t_end: 5.6,
    from_player: "a3",
    to_player: null,
    team: "A",
    status: "intercepted",
    start: { x: 20, y: 48 },
    end: { x: 55, y: 36 },
  },
];

const shots: MatchData["shots"] = [
  {
    id: "shot-1",
    frame: 35,
    t: 7.0,
    player: "b5",
    team: "B",
    start: { x: 50, y: 30 },
    end: { x: 0, y: 34 },
    outcome: "goal",
    velocity: 27.5,
  },
];

// --- Heatmaps --------------------------------------------------------------

function gaussianHeatmap(cx: number, cy: number, sx: number, sy: number): number[][] {
  const matrix: number[][] = [];
  let max = 0;
  for (let row = 0; row < HEATMAP_ROWS; row++) {
    const rowVals: number[] = [];
    for (let col = 0; col < HEATMAP_COLS; col++) {
      const dx = col - cx;
      const dy = row - cy;
      const val = Math.exp(-((dx * dx) / (2 * sx * sx) + (dy * dy) / (2 * sy * sy)));
      rowVals.push(val);
      if (val > max) max = val;
    }
    matrix.push(rowVals);
  }
  if (max > 0) {
    for (let row = 0; row < HEATMAP_ROWS; row++) {
      for (let col = 0; col < HEATMAP_COLS; col++) {
        matrix[row][col] = Math.round((matrix[row][col] / max) * 1000) / 1000;
      }
    }
  }
  return matrix;
}

function combineHeatmaps(matrices: number[][][]): number[][] {
  const out: number[][] = Array.from({ length: HEATMAP_ROWS }, () => new Array(HEATMAP_COLS).fill(0));
  let max = 0;
  for (const m of matrices) {
    for (let row = 0; row < HEATMAP_ROWS; row++) {
      for (let col = 0; col < HEATMAP_COLS; col++) {
        out[row][col] += m[row][col];
        if (out[row][col] > max) max = out[row][col];
      }
    }
  }
  if (max > 0) {
    for (let row = 0; row < HEATMAP_ROWS; row++) {
      for (let col = 0; col < HEATMAP_COLS; col++) {
        out[row][col] = Math.round((out[row][col] / max) * 1000) / 1000;
      }
    }
  }
  return out;
}

const heatmaps: MatchData["heatmaps"] = {};
const teamAMatrices: number[][][] = [];
const teamBMatrices: number[][][] = [];

for (const p of roster) {
  if (p.team === "REF") continue;
  const m = gaussianHeatmap(p.base.x, p.base.y, Math.max(p.ampX * 1.6, 6), Math.max(p.ampY * 1.6, 5));
  heatmaps[`player_${p.id}`] = m;
  if (p.team === "A") teamAMatrices.push(m);
  else teamBMatrices.push(m);
}
heatmaps.team_A = combineHeatmaps(teamAMatrices);
heatmaps.team_B = combineHeatmaps(teamBMatrices);

// --- Assembled fixture -------------------------------------------------

export const mockMatchData: MatchData = {
  meta: {
    match_id: "mock-001",
    duration_seconds: frames[frames.length - 1].t,
    fps: FPS,
    pitch_length: PITCH_LENGTH_M,
    pitch_width: PITCH_WIDTH_M,
    video_url: null,
    source: "mock",
  },
  teams: {
    A: { name: "Home United", color: "#38bdf8" },
    B: { name: "Away City", color: "#fb7185" },
  },
  players: roster.map(({ id, team, jersey_number, name }) => ({ id, team, jersey_number, name })),
  frames,
  passes,
  shots,
  heatmaps,
};

// Re-exported for anything that wants the raw goal-mouth bounds without a
// second import of the constants module.
export { GOAL_Y_MIN, GOAL_Y_MAX };
