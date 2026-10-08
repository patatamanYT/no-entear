"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertTriangle, Radar, Wifi, WifiOff } from "lucide-react";
import { getMatchDataWithFallback, MatchDataSource } from "@/lib/api";
import { MatchProvider } from "@/lib/MatchContext";
import type { MatchData } from "@/types/match";
import Pitch2D from "@/components/Pitch2D";
import { ConnectedHeatmapLayer } from "@/components/HeatmapCanvas";
import EventOverlay from "@/components/EventOverlay";
import VideoSyncPlayer from "@/components/VideoSyncPlayer";
import AnalyticsPanel from "@/components/AnalyticsPanel";
import FilterBar from "@/components/FilterBar";
import UploadPanel from "@/components/UploadPanel";

interface LoadState {
  status: "loading" | "ready" | "error";
  data: MatchData | null;
  source: MatchDataSource | null;
  error?: string;
}

export default function Page() {
  const [state, setState] = useState<LoadState>({ status: "loading", data: null, source: null });

  // Each load gets a sequence number so a stale response (e.g. the initial
  // load finishing after a post-upload reload) can't overwrite a newer one.
  const loadSeq = useRef(0);

  const load = useCallback(() => {
    const seq = ++loadSeq.current;
    getMatchDataWithFallback()
      .then((res) => {
        if (seq !== loadSeq.current) return;
        setState({ status: "ready", data: res.data, source: res.source, error: res.error });
      })
      .catch((err) => {
        if (seq !== loadSeq.current) return;
        setState({
          status: "error",
          data: null,
          source: null,
          error: err instanceof Error ? err.message : String(err),
        });
      });
  }, []);

  useEffect(() => {
    load();
    // Invalidate any in-flight load on unmount (the ref is a counter, not a DOM node).
    const seqRef = loadSeq;
    return () => {
      seqRef.current++;
    };
  }, [load]);

  return (
    <main className="mx-auto flex min-h-screen max-w-[1600px] flex-col gap-4 px-4 py-4 md:px-6">
      <Header source={state.source} error={state.error} onProcessed={load} />

      {state.status === "loading" && <LoadingState />}
      {state.status === "error" && <ErrorState error={state.error} />}
      {state.status === "ready" && state.data && (
        // Keyed by match_id so playback/filter state resets for a newly processed match.
        <MatchProvider key={state.data.meta.match_id} matchData={state.data}>
          <Dashboard />
        </MatchProvider>
      )}
    </main>
  );
}

function Header({
  source,
  error,
  onProcessed,
}: {
  source: MatchDataSource | null;
  error?: string;
  onProcessed: () => void;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-base-700 bg-base-850 px-4 py-3">
      <div className="flex items-center gap-2.5">
        <Radar className="h-5 w-5 text-accent" strokeWidth={1.75} />
        <div>
          <h1 className="text-sm font-semibold tracking-tight text-base-100">No Entear</h1>
          <p className="text-[11px] text-base-400">Tactical video analytics</p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {/* Uploading needs the real backend; the fixture fallback means it's unreachable. */}
        {source === "api" && <UploadPanel onCompleted={onProcessed} />}
        {source && (
          <div
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium ${
              source === "api"
                ? "border-good/30 bg-good/10 text-good"
                : "border-warn/30 bg-warn/10 text-warn"
            }`}
            title={error}
          >
            {source === "api" ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
            {source === "api" ? "Live backend" : "Fixture fallback"}
          </div>
        )}
      </div>
    </header>
  );
}

function LoadingState() {
  return (
    <div className="flex flex-1 items-center justify-center rounded-lg border border-base-700 bg-base-850 py-24 text-base-400">
      <div className="flex items-center gap-2 text-sm">
        <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
        Loading match data…
      </div>
    </div>
  );
}

function ErrorState({ error }: { error?: string }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-2 rounded-lg border border-bad/30 bg-bad/5 py-24 text-bad">
      <AlertTriangle className="h-6 w-6" />
      <p className="text-sm font-medium">Could not load match data</p>
      {error && <p className="max-w-md text-center text-xs text-base-400">{error}</p>}
    </div>
  );
}

function Dashboard() {
  return (
    <div className="flex flex-1 flex-col gap-4">
      <FilterBar />
      <div className="grid flex-1 grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="flex flex-col gap-4">
          <VideoSyncPlayer />
          <Pitch2D>
            <ConnectedHeatmapLayer />
            <EventOverlay />
          </Pitch2D>
        </div>
        <aside className="xl:sticky xl:top-4 xl:self-start">
          <AnalyticsPanel />
        </aside>
      </div>
    </div>
  );
}
