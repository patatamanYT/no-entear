"use client";

import { useMemo } from "react";
import { Crosshair, Goal, Shrink, Users } from "lucide-react";
import { useMatch } from "@/lib/MatchContext";
import { hullArea, Pt } from "@/lib/geometry";
import type { Team } from "@/types/match";

function pct(n: number, d: number): number {
  return d <= 0 ? 0 : (n / d) * 100;
}

function StatCard({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-base-700 bg-base-850 p-3.5 shadow-panel">
      <div className="mb-2.5 flex items-center gap-2 text-base-300">
        {icon}
        <span className="text-[11px] font-semibold uppercase tracking-wide">{title}</span>
      </div>
      {children}
    </div>
  );
}

function TeamRow({
  color,
  label,
  value,
  suffix,
}: {
  color: string;
  label: string;
  value: string;
  suffix?: string;
}) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <div className="flex items-center gap-1.5 text-xs text-base-300">
        <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
        {label}
      </div>
      <div className="font-mono text-sm tabular-nums text-base-100">
        {value}
        {suffix && <span className="ml-0.5 text-[10px] text-base-400">{suffix}</span>}
      </div>
    </div>
  );
}

function SplitBar({ a, b, colorA, colorB }: { a: number; b: number; colorA: string; colorB: string }) {
  const total = a + b || 1;
  const wA = (a / total) * 100;
  return (
    <div className="flex h-2 w-full overflow-hidden rounded-full bg-base-700">
      <div className="h-full" style={{ width: `${wA}%`, backgroundColor: colorA }} />
      <div className="h-full" style={{ width: `${100 - wA}%`, backgroundColor: colorB }} />
    </div>
  );
}

export default function AnalyticsPanel() {
  const { matchData, currentTime, interpolatedFrame } = useMatch();
  const { teams, passes, shots, frames, players } = matchData;

  const playerTeamById = useMemo(() => new Map(players.map((p) => [p.id, p.team])), [players]);

  const stats = useMemo(() => {
    const framesSoFar = frames.filter((f) => f.t <= currentTime);
    let possA = 0;
    let possB = 0;
    for (const f of framesSoFar) {
      let nearest: { id: string; d: number } | null = null;
      for (const p of f.players) {
        const team = playerTeamById.get(p.id);
        if (team !== "A" && team !== "B") continue;
        const d = Math.hypot(p.x - f.ball.x, p.y - f.ball.y);
        if (!nearest || d < nearest.d) nearest = { id: p.id, d };
      }
      if (nearest) {
        const team = playerTeamById.get(nearest.id);
        if (team === "A") possA++;
        else if (team === "B") possB++;
      }
    }

    const passesSoFar = passes.filter((p) => p.t_start <= currentTime);
    const shotsSoFar = shots.filter((s) => s.t <= currentTime);

    const byTeam = (team: Team) => {
      const tp = passesSoFar.filter((p) => p.team === team);
      const completed = tp.filter((p) => p.status === "completed").length;
      const intercepted = tp.filter((p) => p.status === "intercepted").length;
      const ts = shotsSoFar.filter((s) => s.team === team);
      const goals = ts.filter((s) => s.outcome === "goal").length;
      return {
        totalPasses: tp.length,
        accuracy: pct(completed, completed + intercepted),
        shots: ts.length,
        goals,
      };
    };

    return {
      possession: { A: pct(possA, possA + possB), B: pct(possB, possA + possB) },
      A: byTeam("A"),
      B: byTeam("B"),
    };
  }, [frames, passes, shots, currentTime, playerTeamById]);

  const compactness = useMemo(() => {
    const empty = { A: 0, B: 0 };
    if (!interpolatedFrame) return empty;
    const ptsA: Pt[] = [];
    const ptsB: Pt[] = [];
    for (const p of interpolatedFrame.players) {
      const team = playerTeamById.get(p.id);
      // "Outfield" players: the fixed API contract carries no position field,
      // so we approximate outfield-only compactness by including every
      // rostered player on the team (goalkeepers included) — see README note.
      if (team === "A") ptsA.push({ x: p.x, y: p.y });
      else if (team === "B") ptsB.push({ x: p.x, y: p.y });
    }
    return { A: hullArea(ptsA), B: hullArea(ptsB) };
  }, [interpolatedFrame, playerTeamById]);

  return (
    <div className="flex flex-col gap-3">
      <StatCard icon={<Users className="h-3.5 w-3.5" />} title="Possession">
        <div className="mb-2 flex items-center justify-between font-mono text-lg tabular-nums">
          <span style={{ color: teams.A.color }}>{stats.possession.A.toFixed(0)}%</span>
          <span style={{ color: teams.B.color }}>{stats.possession.B.toFixed(0)}%</span>
        </div>
        <SplitBar a={stats.possession.A} b={stats.possession.B} colorA={teams.A.color} colorB={teams.B.color} />
      </StatCard>

      <StatCard icon={<Crosshair className="h-3.5 w-3.5" />} title="Passing">
        <TeamRow color={teams.A.color} label={teams.A.name} value={`${stats.A.totalPasses}`} suffix="passes" />
        <TeamRow color={teams.A.color} label="accuracy" value={`${stats.A.accuracy.toFixed(0)}%`} />
        <div className="my-2 h-px bg-base-700" />
        <TeamRow color={teams.B.color} label={teams.B.name} value={`${stats.B.totalPasses}`} suffix="passes" />
        <TeamRow color={teams.B.color} label="accuracy" value={`${stats.B.accuracy.toFixed(0)}%`} />
      </StatCard>

      <StatCard icon={<Goal className="h-3.5 w-3.5" />} title="Shots & Goals">
        <TeamRow
          color={teams.A.color}
          label={teams.A.name}
          value={`${stats.A.goals}`}
          suffix={`goals / ${stats.A.shots} shots`}
        />
        <TeamRow
          color={teams.B.color}
          label={teams.B.name}
          value={`${stats.B.goals}`}
          suffix={`goals / ${stats.B.shots} shots`}
        />
      </StatCard>

      <StatCard icon={<Shrink className="h-3.5 w-3.5" />} title="Team compactness">
        <TeamRow color={teams.A.color} label={teams.A.name} value={compactness.A.toFixed(0)} suffix="m²" />
        <TeamRow color={teams.B.color} label={teams.B.name} value={compactness.B.toFixed(0)} suffix="m²" />
        <p className="mt-2 text-[10.5px] leading-snug text-base-400">
          Convex hull area of each team&apos;s on-pitch players at the current frame. Lower = more compact.
        </p>
      </StatCard>
    </div>
  );
}
