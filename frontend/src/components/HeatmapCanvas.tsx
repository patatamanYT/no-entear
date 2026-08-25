"use client";

import { useEffect, useRef } from "react";
import { useMatch } from "@/lib/MatchContext";
import { HEATMAP_COLS, HEATMAP_ROWS } from "@/types/match";

// Blue -> green -> yellow -> red density ramp.
const STOPS: Array<[number, number, number, number]> = [
  [0.0, 30, 64, 175], // blue
  [0.35, 16, 185, 129], // green
  [0.65, 234, 179, 8], // yellow
  [1.0, 220, 38, 38], // red
];

function rampColor(v: number): [number, number, number] {
  const t = Math.min(1, Math.max(0, v));
  for (let i = 0; i < STOPS.length - 1; i++) {
    const [t0, r0, g0, b0] = STOPS[i];
    const [t1, r1, g1, b1] = STOPS[i + 1];
    if (t >= t0 && t <= t1) {
      const local = t1 === t0 ? 0 : (t - t0) / (t1 - t0);
      return [r0 + (r1 - r0) * local, g0 + (g1 - g0) * local, b0 + (b1 - b0) * local];
    }
  }
  return [STOPS[STOPS.length - 1][1], STOPS[STOPS.length - 1][2], STOPS[STOPS.length - 1][3]];
}

interface HeatmapCanvasProps {
  matrix: number[][] | undefined;
  visible: boolean;
  /** Peak opacity applied to the highest-density cells. */
  maxOpacity?: number;
}

export default function HeatmapCanvas({ matrix, visible, maxOpacity = 0.75 }: HeatmapCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const offscreenRef = useRef<HTMLCanvasElement | null>(null);

  // Build (or rebuild) the low-res offscreen bitmap whenever the matrix changes.
  useEffect(() => {
    if (!matrix) return;
    let off = offscreenRef.current;
    if (!off) {
      off = document.createElement("canvas");
      offscreenRef.current = off;
    }
    off.width = HEATMAP_COLS;
    off.height = HEATMAP_ROWS;
    const octx = off.getContext("2d");
    if (!octx) return;
    const img = octx.createImageData(HEATMAP_COLS, HEATMAP_ROWS);
    for (let row = 0; row < HEATMAP_ROWS; row++) {
      const srcRow = matrix[row];
      if (!srcRow) continue;
      for (let col = 0; col < HEATMAP_COLS; col++) {
        const v = srcRow[col] ?? 0;
        const [r, g, b] = rampColor(v);
        const idx = (row * HEATMAP_COLS + col) * 4;
        img.data[idx] = r;
        img.data[idx + 1] = g;
        img.data[idx + 2] = b;
        img.data[idx + 3] = v <= 0.02 ? 0 : Math.round(Math.min(1, v) * maxOpacity * 255);
      }
    }
    octx.putImageData(img, 0, 0);
    draw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matrix, maxOpacity]);

  function draw() {
    const canvas = canvasRef.current;
    const off = offscreenRef.current;
    if (!canvas || !off) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(off, 0, 0, HEATMAP_COLS, HEATMAP_ROWS, 0, 0, canvas.width, canvas.height);
  }

  // Keep the visible canvas sized to its container in device pixels, redraw on resize.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = parent.getBoundingClientRect();
      canvas.width = Math.max(1, Math.round(rect.width * dpr));
      canvas.height = Math.max(1, Math.round(rect.height * dpr));
      draw();
    };

    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(parent);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      style={{ opacity: visible && matrix ? 1 : 0, transition: "opacity 150ms ease" }}
      aria-hidden
    />
  );
}

/** Convenience wrapper: reads the active target/visibility straight from match filters + heatmaps. */
export function ConnectedHeatmapLayer() {
  const { matchData, filters } = useMatch();
  const matrix = filters.heatmapTarget ? matchData.heatmaps[filters.heatmapTarget] : undefined;
  return <HeatmapCanvas matrix={matrix} visible={filters.showHeatmap} />;
}
