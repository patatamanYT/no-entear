/**
 * Fetch client for the FastAPI backend. Tries the real API first; callers
 * (see getMatchDataWithFallback) fall back to the static fixture if the
 * network call fails or NEXT_PUBLIC_USE_FIXTURE is set, so the UI is always
 * developable without the backend running.
 */

import type { MatchData, ProcessRequest, ProcessResponse, UploadResponse } from "@/types/match";
import { mockMatchData } from "@/lib/mockFixture";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const USE_FIXTURE_FLAG = process.env.NEXT_PUBLIC_USE_FIXTURE === "true";

class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    throw new ApiError(`Request to ${path} failed with status ${res.status}`, res.status);
  }
  return (await res.json()) as T;
}

/** GET /api/health */
export function getHealth(): Promise<{ status: string } & Record<string, unknown>> {
  return request("/api/health");
}

/** GET /api/match-data — raw call, throws on failure. Use getMatchDataWithFallback for UI code. */
export function getMatchData(): Promise<MatchData> {
  return request<MatchData>("/api/match-data");
}

/** POST /api/upload — multipart form upload of a video file. */
export function uploadVideo(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResponse>("/api/upload", {
    method: "POST",
    body: form,
  });
}

/** POST /api/process — kick off (mock or real) processing pipeline. */
export function triggerProcess(payload: ProcessRequest = {}): Promise<ProcessResponse> {
  return request<ProcessResponse>("/api/process", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export type MatchDataSource = "api" | "fixture";

export interface MatchDataResult {
  data: MatchData;
  source: MatchDataSource;
  error?: string;
}

/**
 * The graceful primary/fallback path the app actually uses: try the real
 * backend, and if it's unreachable (or NEXT_PUBLIC_USE_FIXTURE=true forces
 * it), fall back to the bundled static fixture so the UI stays usable.
 */
export async function getMatchDataWithFallback(): Promise<MatchDataResult> {
  if (USE_FIXTURE_FLAG) {
    return { data: mockMatchData, source: "fixture" };
  }
  try {
    const data = await getMatchData();
    return { data, source: "api" };
  } catch (err) {
    return {
      data: mockMatchData,
      source: "fixture",
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

export { ApiError };
