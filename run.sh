#!/usr/bin/env bash
# Launches the backend (FastAPI) and frontend (Next.js) dev servers together.
#
# Usage:
#   ./run.sh            # install deps if missing, then run both servers
#   ./run.sh --no-install
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
SKIP_INSTALL=false

if [[ "${1:-}" == "--no-install" ]]; then
  SKIP_INSTALL=true
fi

cleanup() {
  echo ""
  echo "Shutting down..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "=== Tactical Football Analytics — dev launcher ==="

# --- Backend setup ---
cd "$BACKEND_DIR"
if [[ ! -d ".venv" ]]; then
  echo "[backend] creating virtualenv..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ "$SKIP_INSTALL" == "false" ]]; then
  echo "[backend] installing python dependencies (this can take a while)..."
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
fi

echo "[backend] starting FastAPI on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
deactivate

# --- Frontend setup ---
cd "$FRONTEND_DIR"
if [[ "$SKIP_INSTALL" == "false" ]]; then
  if [[ ! -d "node_modules" ]]; then
    echo "[frontend] installing node dependencies..."
    npm install
  fi
fi

if [[ ! -f ".env.local" ]]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo "[frontend] starting Next.js on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000  (docs at /docs)"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both."
echo ""

wait "$BACKEND_PID" "$FRONTEND_PID"
