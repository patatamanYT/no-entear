"use client";

import {
  createContext,
  Dispatch,
  ReactNode,
  SetStateAction,
  useContext,
  useMemo,
  useState,
} from "react";
import type { MatchData } from "@/types/match";
import { useInterpolatedFrame, InterpolatedFrame } from "@/lib/useInterpolatedFrame";

export type TeamFilter = "ALL" | "A" | "B";

export interface Filters {
  team: TeamFilter;
  playerId: string | null;
  showPasses: boolean;
  showShots: boolean;
  showHeatmap: boolean;
  /** "team_A" | "team_B" | "player_<id>" | null */
  heatmapTarget: string | null;
}

const defaultFilters: Filters = {
  team: "ALL",
  playerId: null,
  showPasses: true,
  showShots: true,
  showHeatmap: false,
  heatmapTarget: "team_A",
};

export type PlaybackSpeed = 0.5 | 1 | 2;

interface MatchContextValue {
  matchData: MatchData;
  currentTime: number;
  setCurrentTime: Dispatch<SetStateAction<number>>;
  isPlaying: boolean;
  setIsPlaying: Dispatch<SetStateAction<boolean>>;
  speed: PlaybackSpeed;
  setSpeed: Dispatch<SetStateAction<PlaybackSpeed>>;
  duration: number;
  filters: Filters;
  setFilters: Dispatch<SetStateAction<Filters>>;
  interpolatedFrame: InterpolatedFrame | null;
}

const MatchContext = createContext<MatchContextValue | null>(null);

export function MatchProvider({ matchData, children }: { matchData: MatchData; children: ReactNode }) {
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<PlaybackSpeed>(1);
  const [filters, setFilters] = useState<Filters>(defaultFilters);

  const duration = matchData.meta.duration_seconds;
  const interpolatedFrame = useInterpolatedFrame(matchData, currentTime);

  const value = useMemo<MatchContextValue>(
    () => ({
      matchData,
      currentTime,
      setCurrentTime,
      isPlaying,
      setIsPlaying,
      speed,
      setSpeed,
      duration,
      filters,
      setFilters,
      interpolatedFrame,
    }),
    [matchData, currentTime, isPlaying, speed, duration, filters, interpolatedFrame],
  );

  return <MatchContext.Provider value={value}>{children}</MatchContext.Provider>;
}

export function useMatch(): MatchContextValue {
  const ctx = useContext(MatchContext);
  if (!ctx) throw new Error("useMatch must be used within a MatchProvider");
  return ctx;
}
