"use client";

import { useMemo } from "react";
import { ArrowRightLeft, Flame, RotateCcw, Target, Users } from "lucide-react";
import { useMatch, TeamFilter } from "@/lib/MatchContext";

const TEAM_OPTIONS: TeamFilter[] = ["ALL", "A", "B"];

function ToggleChip({
  active,
  onClick,
  children,
  activeColor,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  activeColor?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-xs font-medium transition ${
        active
          ? "border-transparent text-base-950"
          : "border-base-600 text-base-300 hover:border-base-500 hover:text-base-100"
      }`}
      style={active ? { backgroundColor: activeColor ?? "#38bdf8" } : undefined}
    >
      {children}
    </button>
  );
}

export default function FilterBar() {
  const { matchData, filters, setFilters } = useMatch();
  const { teams, players } = matchData;

  const selectablePlayers = useMemo(
    () =>
      players
        .filter((p) => p.team === "A" || p.team === "B")
        .sort((a, b) => (a.team === b.team ? a.jersey_number - b.jersey_number : a.team.localeCompare(b.team))),
    [players],
  );

  const heatmapTargets = useMemo(() => {
    const teamOpts = [
      { value: "team_A", label: `${teams.A.name} (team)` },
      { value: "team_B", label: `${teams.B.name} (team)` },
    ];
    const playerOpts = selectablePlayers.map((p) => ({
      value: `player_${p.id}`,
      label: `${p.team} #${p.jersey_number} ${p.name}`,
    }));
    return [...teamOpts, ...playerOpts];
  }, [teams, selectablePlayers]);

  function resetFilters() {
    setFilters((f) => ({ ...f, team: "ALL", playerId: null }));
  }

  return (
    <div className="flex flex-wrap items-center gap-4 rounded-lg border border-base-700 bg-base-850 px-3.5 py-2.5">
      {/* Team filter */}
      <div className="flex items-center gap-1.5">
        <Users className="h-3.5 w-3.5 text-base-400" />
        <div className="flex overflow-hidden rounded-md border border-base-600">
          {TEAM_OPTIONS.map((t) => {
            const active = filters.team === t;
            const color = t === "A" ? teams.A.color : t === "B" ? teams.B.color : "#8891a0";
            return (
              <button
                key={t}
                onClick={() => setFilters((f) => ({ ...f, team: t }))}
                className={`px-2.5 py-1.5 text-xs font-medium transition ${
                  active ? "text-base-950" : "text-base-300 hover:text-base-100"
                }`}
                style={active ? { backgroundColor: color } : undefined}
              >
                {t === "ALL" ? "All" : teams[t].name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Player filter */}
      <div className="flex items-center gap-1.5">
        <select
          value={filters.playerId ?? ""}
          onChange={(e) => setFilters((f) => ({ ...f, playerId: e.target.value || null }))}
          className="rounded-md border border-base-600 bg-base-800 px-2 py-1.5 text-xs text-base-200 outline-none focus:border-accent"
        >
          <option value="">All players</option>
          {selectablePlayers.map((p) => (
            <option key={p.id} value={p.id}>
              {p.team} #{p.jersey_number} · {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="h-5 w-px bg-base-700" />

      {/* Event toggles */}
      <div className="flex items-center gap-2">
        <ToggleChip
          active={filters.showPasses}
          onClick={() => setFilters((f) => ({ ...f, showPasses: !f.showPasses }))}
          activeColor="#34d399"
        >
          <ArrowRightLeft className="h-3.5 w-3.5" />
          Passes
        </ToggleChip>
        <ToggleChip
          active={filters.showShots}
          onClick={() => setFilters((f) => ({ ...f, showShots: !f.showShots }))}
          activeColor="#fbbf24"
        >
          <Target className="h-3.5 w-3.5" />
          Shots
        </ToggleChip>
        <ToggleChip
          active={filters.showHeatmap}
          onClick={() => setFilters((f) => ({ ...f, showHeatmap: !f.showHeatmap }))}
          activeColor="#f97316"
        >
          <Flame className="h-3.5 w-3.5" />
          Heatmap
        </ToggleChip>
        {filters.showHeatmap && (
          <select
            value={filters.heatmapTarget ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, heatmapTarget: e.target.value || null }))}
            className="rounded-md border border-base-600 bg-base-800 px-2 py-1.5 text-xs text-base-200 outline-none focus:border-accent"
          >
            {heatmapTargets.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        )}
      </div>

      <button
        onClick={resetFilters}
        className="ml-auto flex items-center gap-1.5 rounded-md border border-base-600 px-2.5 py-1.5 text-xs text-base-300 transition hover:border-base-500 hover:text-base-100"
      >
        <RotateCcw className="h-3.5 w-3.5" />
        Reset
      </button>
    </div>
  );
}
