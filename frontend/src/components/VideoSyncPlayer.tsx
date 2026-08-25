"use client";

import { useEffect, useRef } from "react";
import { Pause, Play, Radar, RotateCcw, Video } from "lucide-react";
import { useMatch, PlaybackSpeed } from "@/lib/MatchContext";

const SPEEDS: PlaybackSpeed[] = [0.5, 1, 2];

function fmtClock(t: number): string {
  const m = Math.floor(t / 60);
  const s = t - m * 60;
  return `${m}:${s.toFixed(1).padStart(4, "0")}`;
}

export default function VideoSyncPlayer() {
  const { matchData, currentTime, setCurrentTime, isPlaying, setIsPlaying, speed, setSpeed, duration } =
    useMatch();
  const videoUrl = matchData.meta.video_url;
  const videoRef = useRef<HTMLVideoElement>(null);
  const rafRef = useRef<number | null>(null);
  const lastTsRef = useRef<number | null>(null);

  // --- Mode A: real <video> element drives the clock via timeupdate -----
  useEffect(() => {
    if (!videoUrl) return;
    const video = videoRef.current;
    if (!video) return;
    if (isPlaying) {
      video.play().catch(() => setIsPlaying(false));
    } else {
      video.pause();
    }
  }, [isPlaying, videoUrl, setIsPlaying]);

  useEffect(() => {
    if (!videoUrl) return;
    const video = videoRef.current;
    if (video) video.playbackRate = speed;
  }, [speed, videoUrl]);

  // --- Mode B: no source video -> virtual clock via requestAnimationFrame
  useEffect(() => {
    if (videoUrl) return; // real video drives itself
    if (!isPlaying) {
      lastTsRef.current = null;
      return;
    }

    const tick = (ts: number) => {
      if (lastTsRef.current === null) lastTsRef.current = ts;
      const dt = (ts - lastTsRef.current) / 1000;
      lastTsRef.current = ts;
      setCurrentTime((prev) => {
        const next = prev + dt * speed;
        if (next >= duration) {
          setIsPlaying(false);
          return duration;
        }
        return next;
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      lastTsRef.current = null;
    };
  }, [isPlaying, speed, duration, videoUrl, setCurrentTime, setIsPlaying]);

  function togglePlay() {
    setIsPlaying((p) => !p);
  }

  function handleScrub(value: number) {
    setCurrentTime(value);
    if (videoUrl && videoRef.current) {
      videoRef.current.currentTime = value;
    }
  }

  function handleRestart() {
    handleScrub(0);
  }

  function handleVideoTimeUpdate() {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);
  }

  function handleVideoEnded() {
    setIsPlaying(false);
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-base-700 bg-base-950">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            className="h-full w-full object-contain"
            onTimeUpdate={handleVideoTimeUpdate}
            onEnded={handleVideoEnded}
            playsInline
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-2 bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.07),transparent_70%)] text-base-300">
            <Radar className="h-8 w-8 text-accent/70" strokeWidth={1.5} />
            <div className="text-sm font-medium text-base-200">No video source</div>
            <div className="text-xs text-base-400">Simulated timeline — tactical playback only</div>
          </div>
        )}

        <div className="absolute left-2 top-2 flex items-center gap-1.5 rounded-full border border-base-600 bg-base-950/80 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-base-300">
          {videoUrl ? <Video className="h-3 w-3" /> : <Radar className="h-3 w-3" />}
          {videoUrl ? "video feed" : "simulated"}
        </div>
      </div>

      <div className="flex flex-col gap-2 rounded-lg border border-base-700 bg-base-850 p-3">
        <input
          type="range"
          min={0}
          max={duration}
          step={0.02}
          value={Math.min(currentTime, duration)}
          onChange={(e) => handleScrub(parseFloat(e.target.value))}
          className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-base-700 accent-accent"
          aria-label="Timeline scrubber"
        />
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={handleRestart}
              className="rounded-md border border-base-600 p-1.5 text-base-300 transition hover:border-base-500 hover:text-base-100"
              aria-label="Restart"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={togglePlay}
              className="rounded-md bg-accent p-1.5 text-base-950 transition hover:bg-accent-soft"
              aria-label={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
            </button>
            <span className="font-mono text-xs tabular-nums text-base-300">
              {fmtClock(currentTime)} <span className="text-base-500">/ {fmtClock(duration)}</span>
            </span>
          </div>

          <div className="flex items-center gap-1 rounded-md border border-base-600 p-0.5">
            {SPEEDS.map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`rounded px-2 py-1 text-[11px] font-medium tabular-nums transition ${
                  speed === s ? "bg-accent text-base-950" : "text-base-300 hover:text-base-100"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
