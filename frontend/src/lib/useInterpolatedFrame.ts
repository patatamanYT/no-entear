import { useMemo } from "react";
import type { Frame, MatchData } from "@/types/match";

export interface InterpolatedPlayer {
  id: string;
  x: number;
  y: number;
  v: number;
}

export interface InterpolatedFrame {
  t: number;
  ball: { x: number; y: number };
  players: InterpolatedPlayer[];
}

function lerp(a: number, b: number, r: number): number {
  return a + (b - a) * r;
}

function interpolateFrames(a: Frame, b: Frame, ratio: number): InterpolatedFrame {
  const playersById = new Map(b.players.map((p) => [p.id, p]));
  const players: InterpolatedPlayer[] = a.players.map((pa) => {
    const pb = playersById.get(pa.id) ?? pa;
    return {
      id: pa.id,
      x: lerp(pa.x, pb.x, ratio),
      y: lerp(pa.y, pb.y, ratio),
      v: lerp(pa.v, pb.v, ratio),
    };
  });
  return {
    t: lerp(a.t, b.t, ratio),
    ball: { x: lerp(a.ball.x, b.ball.x, ratio), y: lerp(a.ball.y, b.ball.y, ratio) },
    players,
  };
}

/**
 * Find the two frames bounding `t` and linearly interpolate player/ball
 * positions between them, so playback looks smooth regardless of the
 * source data's fps (and regardless of the scrub rate during seeking).
 */
export function interpolateAt(frames: Frame[], t: number): InterpolatedFrame | null {
  if (frames.length === 0) return null;
  if (t <= frames[0].t) {
    const f = frames[0];
    return { t: f.t, ball: f.ball, players: f.players.map((p) => ({ ...p })) };
  }
  const last = frames[frames.length - 1];
  if (t >= last.t) {
    return { t: last.t, ball: last.ball, players: last.players.map((p) => ({ ...p })) };
  }

  // Linear scan is fine at this data scale (hundreds-low thousands of frames).
  let lo = 0;
  let hi = frames.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (frames[mid].t <= t) lo = mid;
    else hi = mid;
  }
  const a = frames[lo];
  const b = frames[hi];
  const span = b.t - a.t;
  const ratio = span <= 0 ? 0 : (t - a.t) / span;
  return interpolateFrames(a, b, ratio);
}

export function useInterpolatedFrame(matchData: MatchData | null, t: number): InterpolatedFrame | null {
  return useMemo(() => {
    if (!matchData) return null;
    return interpolateAt(matchData.frames, t);
  }, [matchData, t]);
}
