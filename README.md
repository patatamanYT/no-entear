# Tactical Football Analytics

A full-stack tactical video analytics platform for **fútbol 7** (7-a-side) match clips. It extracts 2D bird's-eye tracking data from video using computer vision (YOLO + ByteTrack + homography + jersey-color team clustering), computes possession/pass/shot events and heatmaps, and renders it all in an interactive dark-mode dashboard synced to the source video.

The pitch is modeled as a 60m x 40m fútbol 7 field (6m x 2m goals), not an 11-a-side 105x68 pitch — see `PITCH_LENGTH_M`/`PITCH_WIDTH_M` in `backend/app/schemas.py` (mirrored in `frontend/src/types/match.ts`) if your fields use different dimensions.

A synthetic 30-second match generator is included so the full dashboard works immediately, with zero GPU/model setup.

## Architecture

```
no-entear/
├── backend/                 FastAPI + computer vision pipeline
│   └── app/
│       ├── cv/
│       │   ├── detector.py          YOLO detection + ByteTrack multi-object tracking
│       │   ├── homography.py        4-point pixel → pitch-meter (60×40) transform
│       │   └── team_classifier.py   Jersey color extraction + K-Means team clustering
│       ├── analytics/
│       │   ├── events.py            Possession / pass / shot heuristics
│       │   └── heatmaps.py          2D Gaussian KDE heatmap grids (40×60, 1m bins)
│       ├── storage/                 Uploaded videos + generated match JSON
│       ├── mock_data.py             Synthetic match generator (CLI + importable)
│       ├── schemas.py               Pydantic data contract (source of truth)
│       └── main.py                  REST API (CORS enabled for the frontend)
│
└── frontend/                 Next.js 14 + TypeScript + Tailwind CSS
    └── src/
        ├── components/
        │   ├── Pitch2D.tsx           SVG pitch (60:40, fútbol 7) with live player/ball dots
        │   ├── HeatmapCanvas.tsx     Canvas density overlay from KDE matrices
        │   ├── EventOverlay.tsx      Pass arrows + shot trajectories
        │   ├── VideoSyncPlayer.tsx   Video/timeline playback, frame-synced with the pitch
        │   ├── AnalyticsPanel.tsx    Possession, passes, accuracy, shots, compactness
        │   └── FilterBar.tsx         Team / player / event-type / timeline filters
        ├── lib/                      API client, geometry helpers, pitch coordinate transform
        ├── types/match.ts            TypeScript mirror of backend/app/schemas.py
        └── app/                      Next.js App Router pages
```

The two halves talk over a single JSON contract (`GET /api/match-data`) defined once in `backend/app/schemas.py` and mirrored in `frontend/src/types/match.ts`.

## Quick start

**Requirements:** Python 3.10+, Node.js 18+, npm.

```bash
git clone <this repo>
cd no-entear
./run.sh
```

This installs backend + frontend dependencies (first run only) and starts:

- Backend: http://localhost:8000 (interactive docs at `/docs`)
- Frontend: http://localhost:3000

On first request, the backend automatically generates a synthetic 30-second fútbol 7 match (14 tracked players + referee, realistic passes/shots/heatmaps) so the dashboard is populated with zero manual steps. Open http://localhost:3000 to explore it.

Stop both servers with `Ctrl+C`.

### Manual setup

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.mock_data          # optional: pre-generate the synthetic match JSON
uvicorn app.main:app --reload --port 8000

# Frontend (in a second terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Or use the Makefile: `make install`, `make backend`, `make frontend`, `make mock`, `make test`.

## Using real video

1. `POST /api/upload` a video file (multipart) → returns `{video_id, filename}`.
2. `POST /api/process` with `{"video_id": "...", "mock": false}` to run the real CV pipeline: YOLO detection → ByteTrack → homography calibration → team classification → event/heatmap analytics.
3. `GET /api/match-data` returns the processed result in the same schema as the mock data, so the frontend needs no changes.

`ultralytics`, `supervision`, and `opencv-python-headless` are only imported when the real pipeline actually runs, so the mock flow above works with no model weights, GPU, or internet access required.

## API reference

| Method | Path              | Description                                              |
|--------|-------------------|------------------------------------------------------------|
| GET    | `/api/health`     | Liveness check                                              |
| POST   | `/api/upload`     | Upload a video file                                         |
| POST   | `/api/process`    | Run the tracking pipeline (`mock: true` for synthetic data) |
| GET    | `/api/match-data` | Full `MatchData` payload: frames, passes, shots, heatmaps   |

Full request/response shapes: `backend/app/schemas.py`.

## Analytics heuristics

- **Possession:** a player controls the ball when `distance(ball, player) ≤ 1.2m`.
- **Pass:** ball leaves a player at `>4 m/s` and is next possessed by a teammate (completed) or opponent (intercepted).
- **Shot:** ball travels at `>12 m/s` toward a goal mouth (`X → 0` or `X → 60`, `Y ∈ [17, 23]`).
- **Heatmaps:** 2D Gaussian KDE over a 60×40 (1m) grid per player and per team, normalized to `[0, 1]`.

## Testing

```bash
make test          # backend: pytest — schema validation, heatmap shape, event heuristics
cd frontend && npm run build   # frontend: production build + type-check
```
