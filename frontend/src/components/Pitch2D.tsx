"use client";

import { ReactNode, useMemo } from "react";
import { useMatch } from "@/lib/MatchContext";
import { PITCH_VB_HEIGHT, PITCH_VB_WIDTH } from "@/lib/pitchTransform";
import { GOAL_Y_MAX, GOAL_Y_MIN } from "@/types/match";

const LINE = "rgba(226,232,240,0.5)";
const LINE_STRONG = "rgba(226,232,240,0.65)";

const PEN_BOX_DEPTH = 16.5;
const PEN_BOX_Y_MIN = (PITCH_VB_HEIGHT - 40.32) / 2;
const PEN_BOX_Y_MAX = PITCH_VB_HEIGHT - PEN_BOX_Y_MIN;
const SIX_YD_DEPTH = 5.5;
const SIX_YD_Y_MIN = (PITCH_VB_HEIGHT - 18.32) / 2;
const SIX_YD_Y_MAX = PITCH_VB_HEIGHT - SIX_YD_Y_MIN;
const PEN_SPOT_X_LEFT = 11;
const PEN_SPOT_X_RIGHT = PITCH_VB_WIDTH - 11;
const ARC_R = 9.15;
const CENTER_R = 9.15;

function penaltyArcPath(spotX: number, side: "left" | "right"): string {
  const boxEdge = side === "left" ? PEN_BOX_DEPTH : PITCH_VB_WIDTH - PEN_BOX_DEPTH;
  const dx = Math.abs(boxEdge - spotX);
  const theta = Math.acos(dx / ARC_R);
  const dy = ARC_R * Math.sin(theta);
  const y1 = PITCH_VB_HEIGHT / 2 - dy;
  const y2 = PITCH_VB_HEIGHT / 2 + dy;
  const sweep = side === "left" ? 1 : 0;
  return `M ${boxEdge} ${y1} A ${ARC_R} ${ARC_R} 0 0 ${sweep} ${boxEdge} ${y2}`;
}

function cornerArcPath(cx: number, cy: number, sx: 1 | -1, sy: 1 | -1): string {
  const r = 1;
  const p1 = { x: cx + sx * r, y: cy };
  const p2 = { x: cx, y: cy + sy * r };
  const sweep = sx * sy === 1 ? 1 : 0;
  return `M ${p1.x} ${p1.y} A ${r} ${r} 0 0 ${sweep} ${p2.x} ${p2.y}`;
}

interface Pitch2DProps {
  /** Overlay layers stacked between the pitch markings and the live player dots (e.g. heatmap, event arrows). */
  children?: ReactNode;
  className?: string;
}

export default function Pitch2D({ children, className }: Pitch2DProps) {
  const { matchData, interpolatedFrame, filters } = useMatch();
  const { teams, players } = matchData;

  const playerMetaById = useMemo(() => new Map(players.map((p) => [p.id, p])), [players]);

  const midY = PITCH_VB_HEIGHT / 2;
  const midX = PITCH_VB_WIDTH / 2;

  return (
    <div
      className={`relative w-full select-none overflow-hidden rounded-lg border border-base-700 bg-pitch-grass shadow-panel ${className ?? ""}`}
      style={{ aspectRatio: `${PITCH_VB_WIDTH} / ${PITCH_VB_HEIGHT}` }}
    >
      {/* Turf stripes + markings */}
      <svg
        viewBox={`0 0 ${PITCH_VB_WIDTH} ${PITCH_VB_HEIGHT}`}
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="none"
      >
        <defs>
          <pattern id="stripes" width={PITCH_VB_WIDTH / 9} height={PITCH_VB_HEIGHT} patternUnits="userSpaceOnUse">
            <rect width={PITCH_VB_WIDTH / 18} height={PITCH_VB_HEIGHT} fill="#0e4429" />
            <rect x={PITCH_VB_WIDTH / 18} width={PITCH_VB_WIDTH / 18} height={PITCH_VB_HEIGHT} fill="#0d3d24" />
          </pattern>
        </defs>
        <rect x={0} y={0} width={PITCH_VB_WIDTH} height={PITCH_VB_HEIGHT} fill="url(#stripes)" />

        <g fill="none" stroke={LINE} strokeWidth={0.18} vectorEffect="non-scaling-stroke">
          {/* Outer boundary */}
          <rect x={0.1} y={0.1} width={PITCH_VB_WIDTH - 0.2} height={PITCH_VB_HEIGHT - 0.2} stroke={LINE_STRONG} />
          {/* Halfway line */}
          <line x1={midX} y1={0} x2={midX} y2={PITCH_VB_HEIGHT} />
          {/* Center circle + spot */}
          <circle cx={midX} cy={midY} r={CENTER_R} />
          <circle cx={midX} cy={midY} r={0.35} fill={LINE} stroke="none" />

          {/* Penalty boxes */}
          <rect x={0} y={PEN_BOX_Y_MIN} width={PEN_BOX_DEPTH} height={PEN_BOX_Y_MAX - PEN_BOX_Y_MIN} />
          <rect
            x={PITCH_VB_WIDTH - PEN_BOX_DEPTH}
            y={PEN_BOX_Y_MIN}
            width={PEN_BOX_DEPTH}
            height={PEN_BOX_Y_MAX - PEN_BOX_Y_MIN}
          />

          {/* 6-yard boxes */}
          <rect x={0} y={SIX_YD_Y_MIN} width={SIX_YD_DEPTH} height={SIX_YD_Y_MAX - SIX_YD_Y_MIN} />
          <rect
            x={PITCH_VB_WIDTH - SIX_YD_DEPTH}
            y={SIX_YD_Y_MIN}
            width={SIX_YD_DEPTH}
            height={SIX_YD_Y_MAX - SIX_YD_Y_MIN}
          />

          {/* Penalty arcs */}
          <path d={penaltyArcPath(PEN_SPOT_X_LEFT, "left")} />
          <path d={penaltyArcPath(PEN_SPOT_X_RIGHT, "right")} />

          {/* Corner arcs */}
          <path d={cornerArcPath(0, 0, 1, 1)} />
          <path d={cornerArcPath(PITCH_VB_WIDTH, 0, -1, 1)} />
          <path d={cornerArcPath(0, PITCH_VB_HEIGHT, 1, -1)} />
          <path d={cornerArcPath(PITCH_VB_WIDTH, PITCH_VB_HEIGHT, -1, -1)} />

          {/* Goals (drawn slightly outside the boundary) */}
          <rect x={-1.6} y={GOAL_Y_MIN} width={1.6} height={GOAL_Y_MAX - GOAL_Y_MIN} stroke={LINE_STRONG} />
          <rect
            x={PITCH_VB_WIDTH}
            y={GOAL_Y_MIN}
            width={1.6}
            height={GOAL_Y_MAX - GOAL_Y_MIN}
            stroke={LINE_STRONG}
          />
        </g>

        {/* Penalty spots (filled) */}
        <circle cx={PEN_SPOT_X_LEFT} cy={midY} r={0.35} fill={LINE} />
        <circle cx={PEN_SPOT_X_RIGHT} cy={midY} r={0.35} fill={LINE} />
      </svg>

      {/* Overlay layers (heatmap, event arrows) supplied by caller, stacked above markings */}
      {children}

      {/* Live player + ball layer, always on top */}
      <svg
        viewBox={`0 0 ${PITCH_VB_WIDTH} ${PITCH_VB_HEIGHT}`}
        className="pointer-events-none absolute inset-0 h-full w-full"
        preserveAspectRatio="none"
      >
        {interpolatedFrame?.players.map((p) => {
          const meta = playerMetaById.get(p.id);
          if (!meta) return null;
          const teamColor =
            meta.team === "A" ? teams.A.color : meta.team === "B" ? teams.B.color : "#9ca3af";
          const isRef = meta.team === "REF";

          const teamMismatch = filters.team !== "ALL" && meta.team !== filters.team;
          const playerMismatch = filters.playerId !== null && filters.playerId !== meta.id;
          const dimmed = teamMismatch || playerMismatch;
          const highlighted = filters.playerId === meta.id;

          const r = isRef ? 1.05 : highlighted ? 1.85 : 1.55;

          return (
            <g
              key={p.id}
              transform={`translate(${p.x} ${p.y})`}
              style={{ transition: "transform 90ms linear", opacity: dimmed ? 0.25 : 1 }}
            >
              {highlighted && <circle r={r + 0.7} fill="none" stroke={teamColor} strokeWidth={0.3} opacity={0.9} />}
              <circle
                r={r}
                fill={isRef ? "#71717a" : teamColor}
                stroke="rgba(8,9,11,0.85)"
                strokeWidth={0.25}
              />
              {!isRef && (
                <text
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={1.5}
                  fontWeight={700}
                  fill="#08090b"
                  style={{ fontFamily: "var(--font-mono, monospace)" }}
                >
                  {meta.jersey_number}
                </text>
              )}
            </g>
          );
        })}

        {interpolatedFrame && (
          <g transform={`translate(${interpolatedFrame.ball.x} ${interpolatedFrame.ball.y})`}
             style={{ transition: "transform 90ms linear" }}>
            <circle r={0.85} fill="#fef9c3" stroke="#08090b" strokeWidth={0.22} />
          </g>
        )}
      </svg>
    </div>
  );
}
