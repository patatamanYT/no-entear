"use client";

import { useEffect, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2, Upload } from "lucide-react";
import { triggerProcess, uploadVideo, waitForProcessing } from "@/lib/api";

// Mirrors ALLOWED_VIDEO_EXTENSIONS in backend/app/config.py; the backend is
// still the source of truth and rejects anything else with a 415.
const ACCEPTED_EXTENSIONS = ".mp4,.mov,.avi,.webm,.mkv,.m4v";

type UploadState =
  | { phase: "idle" }
  | { phase: "uploading"; filename: string }
  | { phase: "processing"; filename: string }
  | { phase: "done"; filename: string }
  | { phase: "error"; message: string };

/**
 * Upload → process → poll flow for a real clip. The real CV pipeline runs
 * on a backend thread and can take minutes, so this polls the job status
 * and calls `onCompleted` once GET /api/match-data has the new result.
 */
export default function UploadPanel({ onCompleted }: { onCompleted: () => void }) {
  const [state, setState] = useState<UploadState>({ phase: "idle" });
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  const busy = state.phase === "uploading" || state.phase === "processing";

  async function handleFile(file: File) {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      setState({ phase: "uploading", filename: file.name });
      const { video_id } = await uploadVideo(file);
      if (controller.signal.aborted) return;

      setState({ phase: "processing", filename: file.name });
      await triggerProcess({ video_id, mock: false });
      const job = await waitForProcessing(video_id, { signal: controller.signal });

      if (job.status === "failed") {
        setState({ phase: "error", message: job.error || "Processing failed." });
        return;
      }
      setState({ phase: "done", filename: file.name });
      onCompleted();
    } catch (err) {
      if (controller.signal.aborted) return;
      setState({ phase: "error", message: err instanceof Error ? err.message : String(err) });
    }
  }

  return (
    <div className="flex items-center gap-2">
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = ""; // allow re-selecting the same file
          if (file) void handleFile(file);
        }}
      />
      <StatusText state={state} />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={busy}
        className="flex items-center gap-1.5 rounded-md border border-base-600 px-2.5 py-1.5 text-xs font-medium text-base-300 transition hover:border-base-500 hover:text-base-100 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}
        Upload video
      </button>
    </div>
  );
}

function StatusText({ state }: { state: UploadState }) {
  switch (state.phase) {
    case "idle":
      return null;
    case "uploading":
      return <span className="max-w-[240px] truncate text-[11px] text-base-400">Uploading {state.filename}…</span>;
    case "processing":
      return (
        <span className="max-w-[240px] truncate text-[11px] text-base-400">
          Processing {state.filename} (this can take minutes)…
        </span>
      );
    case "done":
      return (
        <span className="flex max-w-[240px] items-center gap-1 truncate text-[11px] text-good">
          <CheckCircle2 className="h-3 w-3 shrink-0" />
          {state.filename} processed
        </span>
      );
    case "error":
      return (
        <span className="flex max-w-[320px] items-center gap-1 truncate text-[11px] text-bad" title={state.message}>
          <AlertTriangle className="h-3 w-3 shrink-0" />
          {state.message}
        </span>
      );
  }
}
