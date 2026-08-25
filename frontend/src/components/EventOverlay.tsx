"use client";

import { useMemo, useState } from "react";
import { useMatch } from "@/lib/MatchContext";
import { PITCH_VB_HEIGHT, PITCH_VB_WIDTH } from "@/lib/pitchTransform";
import type { PassEvent, ShotEvent, ShotOutcome } from "@/types/match";

const OUTCOME_COLOR: Record<ShotOutcome, string> = {
  goal: "#fbbf24",
  on_target: "#38bdf8",
  off_target: "#94a3b8",
  blocked: "#fb923c",
};

interface TooltipState {
  x: number;
  y: number;
  lines: string[];
}

function fmtT(t: number): string {
  return `${t.toFixed(1)}s`;
}

export default function EventOverlay() {
  const { matchData, currentTime, filters } = useMatch();
  const { passes, shots, players } = matchData;
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const playerById = useMemo(() => new Map(players.map((p) => [p.id, p])), [players]);

  function playerLabel(id: string | null): string {
    if (!id) return "unknown";
    const p = playerById.get(id);
    return p ? `${p.name} (#${p.jersey_number})` : id;
  }

  function matchesFilters(team: string, involved: (string | null)[]): boolean {
    if (filters.team !== "ALL" && team !== filters.team) return false;
    if (filters.playerId && !involved.includes(filters.playerId)) return false;
    return true;
  }

  function eventOpacity(tStart: number, tEnd: number): number | null {
    if (tStart > currentTime) return null; // hasn't happened yet
    const sinceEnd = currentTime - tEnd;
    if (sinceEnd < 2.5) return 1;
    return 0.3;
  }

  const visiblePasses: PassEvent[] = filters.showPasses
    ? passes.filter((p) => matchesFilters(p.team, [p.from_player, p.to_player]))
    : [];
  const visibleShots: ShotEvent[] = filters.showShots
    ? shots.filter((s) => matchesFilters(s.team, [s.player]))
    : [];

  function onEnter(e: React.MouseEvent, lines: string[]) {
    setTooltip({ x: e.clientX, y: e.clientY, lines });
  }
  function onMove(e: React.MouseEvent) {
    setTooltip((prev) => (prev ? { ...prev, x: e.clientX, y: e.clientY } : prev));
  }
  function onLeave() {
    setTooltip(null);
  }

  return (
    <>
      <svg
        viewBox={`0 0 ${PITCH_VB_WIDTH} ${PITCH_VB_HEIGHT}`}
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="none"
      >
        <defs>
          <marker id="arrow-completed" markerWidth="6" markerHeight="6" refX="4.5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#34d399" />
          </marker>
          <marker id="arrow-intercepted" markerWidth="6" markerHeight="6" refX="4.5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f87171" />
          </marker>
        </defs>

        {visiblePasses.map((p) => {
          const opacity = eventOpacity(p.t_start, p.t_end);
          if (opacity === null) return null;
          const color = p.status === "completed" ? "#34d399" : "#f87171";
          const marker = p.status === "completed" ? "url(#arrow-completed)" : "url(#arrow-intercepted)";
          return (
            <g key={p.id} opacity={opacity}>
              <line
                x1={p.start.x}
                y1={p.start.y}
                x2={p.end.x}
                y2={p.end.y}
                stroke={color}
                strokeWidth={0.35}
                strokeDasharray={p.status === "intercepted" ? "1.2,0.8" : undefined}
                markerEnd={marker}
              />
              <line
                x1={p.start.x}
                y1={p.start.y}
                x2={p.end.x}
                y2={p.end.y}
                stroke="transparent"
                strokeWidth={2.2}
                className="pointer-events-auto cursor-pointer"
                onMouseEnter={(e) =>
                  onEnter(e, [
                    `Pass · ${p.status}`,
                    `${playerLabel(p.from_player)} -> ${playerLabel(p.to_player)}`,
                    `${fmtT(p.t_start)} - ${fmtT(p.t_end)} · Team ${p.team}`,
                  ])
                }
                onMouseMove={onMove}
                onMouseLeave={onLeave}
              />
            </g>
          );
        })}

        {visibleShots.map((s) => {
          const opacity = eventOpacity(s.t, s.t + 1);
          if (opacity === null) return null;
          const color = OUTCOME_COLOR[s.outcome];
          return (
            <g key={s.id} opacity={opacity}>
              <line x1={s.start.x} y1={s.start.y} x2={s.end.x} y2={s.end.y} stroke={color} strokeWidth={0.4} />
              {s.outcome === "goal" ? (
                <circle cx={s.end.x} cy={s.end.y} r={1} fill={color} stroke="#08090b" strokeWidth={0.2} />
              ) : s.outcome === "on_target" ? (
                <circle cx={s.end.x} cy={s.end.y} r={0.8} fill="none" stroke={color} strokeWidth={0.3} />
              ) : s.outcome === "blocked" ? (
                <rect
                  x={s.end.x - 0.7}
                  y={s.end.y - 0.7}
                  width={1.4}
                  height={1.4}
                  fill={color}
                  opacity={0.85}
                />
              ) : (
                <g stroke={color} strokeWidth={0.3}>
                  <line x1={s.end.x - 0.8} y1={s.end.y - 0.8} x2={s.end.x + 0.8} y2={s.end.y + 0.8} />
                  <line x1={s.end.x - 0.8} y1={s.end.y + 0.8} x2={s.end.x + 0.8} y2={s.end.y - 0.8} />
                </g>
              )}
              <line
                x1={s.start.x}
                y1={s.start.y}
                x2={s.end.x}
                y2={s.end.y}
                stroke="transparent"
                strokeWidth={2.2}
                className="pointer-events-auto cursor-pointer"
                onMouseEnter={(e) =>
                  onEnter(e, [
                    `Shot · ${s.outcome.replace("_", " ")}`,
                    `${playerLabel(s.player)} · Team ${s.team}`,
                    `${fmtT(s.t)} · ${s.velocity.toFixed(1)} m/s`,
                  ])
                }
                onMouseMove={onMove}
                onMouseLeave={onLeave}
              />
            </g>
          );
        })}
      </svg>

      {tooltip && (
        <div
          className="pointer-events-none fixed z-50 max-w-[220px] rounded-md border border-base-600 bg-base-900/95 px-2.5 py-1.5 text-xs text-base-100 shadow-panel"
          style={{ left: tooltip.x + 14, top: tooltip.y + 14 }}
        >
          {tooltip.lines.map((line, i) => (
            <div key={i} className={i === 0 ? "font-semibold text-base-100" : "text-base-300"}>
              {line}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
