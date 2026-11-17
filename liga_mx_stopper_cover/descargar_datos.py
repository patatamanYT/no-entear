"""Descarga estadisticas de centrales de Liga MX (fase regular) desde Sportmonks v3.

Uso:
    export SPORTMONKS_API_TOKEN=...      # nunca en el codigo ni en git
    python descargar_datos.py --plan      # solo metadatos: liga, temporada, fases
    python descargar_datos.py --out centrales_apertura2026.csv

Flujo (documentacion: https://docs.sportmonks.com/v3):
  1. Liga por nombre (o --league-id) + temporada actual (o --season-id).
  2. Fases (stages) de la temporada -> se elige la fase regular (--stage-name
     o --stage-id). Liguilla y repechaje quedan fuera porque son otras fases.
  3. Partidos de esa fase; solo los terminados.
  4. Por partido: alineaciones con estadisticas por jugador (lineups.details)
     y posicion detallada. Una peticion por partido, guardada en cache local.
  5. Suma por jugador (todas sus filas, aunque haya cambiado de equipo) y
     escribe el CSV con las columnas de plantilla_centrales.csv.

Pausa entre peticiones (--sleep) y reintentos ante 429. Las respuestas se
guardan en --cache-dir y no se vuelven a pedir (borra la carpeta para
refrescar, o usa --refresh para refrescar solo la lista de partidos).
"""
import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE = "https://api.sportmonks.com/v3/football"

# Tipos de estadistica por jugador (IDs de
# https://docs.sportmonks.com/v3/definitions/types/statistics)
T = {
    "minutes": 119,                 # MINUTES_PLAYED
    "tackles_won": 27267,           # TACKLES_WON
    "aerials_won": 107,             # AERIALS_WON
    "clearances": 101,              # CLEARANCES
    "interceptions": 100,           # INTERCEPTIONS
    "duels_won": 106,               # DUELS_WON
    "dribbled_past": 110,           # DRIBBLED_PAST
    "recoveries": 27271,            # BALL_RECOVERY
    "error_lead_to_shot": 48997,    # ERROR_LEAD_TO_SHOT
    "error_lead_to_goal": 571,      # ERROR_LEAD_TO_GOAL
    "passes": 80,                   # PASSES
    "accurate_passes": 116,         # ACCURATE_PASSES
    "accurate_passes_pct": 1584,    # ACCURATE_PASSES_PERCENTAGE (respaldo)
}
FINISHED = {"FT", "AET", "FT_PEN", "AWARDED"}
CB_NAMES = {"centre back", "center back", "centre-back", "center-back"}
OUT_COLS = ["player", "team", "position", "minutes", "tackles_won", "aerials_won",
            "clearances", "interceptions", "duels_won", "dribbled_past",
            "pass_completion_pct", "recoveries", "errors", "phase"]


class Client:
    def __init__(self, token, cache_dir, sleep, refresh=False):
        self.s = requests.Session()
        self.s.headers["Authorization"] = token  # header, para que no quede en URLs ni logs
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.sleep = sleep
        self.refresh = refresh
        self.calls = 0

    def _key(self, path, params):
        raw = path + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return self.cache / (hashlib.sha1(raw.encode()).hexdigest()[:16] + ".json"), raw

    def get(self, path, params=None, cache=True):
        params = dict(params or {})
        f, raw = self._key(path, params)
        if cache and f.exists() and not self.refresh:
            return json.loads(f.read_text())["body"]
        for attempt in range(6):
            time.sleep(self.sleep)
            r = self.s.get(BASE + path, params=params, timeout=60)
            self.calls += 1
            if r.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"[429] limite de peticiones; espero {wait}s")
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code != 200:
                msg = r.text[:300].replace("\n", " ")
                raise SystemExit(f"HTTP {r.status_code} en {path}: {msg}")
            body = r.json()
            f.write_text(json.dumps({"request": raw, "body": body}))
            return body
        raise SystemExit(f"Sin respuesta valida tras reintentos: {path}")

    def get_all(self, path, params=None, cache=True):
        """Pagina con cursor (has_more / next_cursor)."""
        params = dict(params or {}, per_page=50)
        out = []
        while True:
            body = self.get(path, params, cache)
            data = body.get("data") or []
            out.extend(data if isinstance(data, list) else [data])
            pag = body.get("pagination") or {}
            if not pag.get("has_more"):
                return out
            params = {k: v for k, v in params.items() if k != "per_page"}
            if pag.get("next_cursor"):
                params["cursor"] = pag["next_cursor"]
            else:  # paginacion antigua por pagina
                params["page"] = pag.get("current_page", 1) + 1


def value_of(detail):
    v = (detail.get("data") or {}).get("value")
    if isinstance(v, dict):  # algunos tipos traen {"total": ...}
        v = v.get("total", next(iter(v.values()), None))
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def pick_league(c, a):
    if a.league_id:
        return c.get(f"/leagues/{a.league_id}", {"include": "currentSeason;country"})["data"]
    leagues = c.get_all(f"/leagues/search/{a.league_name}", {"include": "currentSeason;country"})
    mx = [l for l in leagues if ((l.get("country") or {}).get("name") or "").lower() == "mexico"]
    for l in leagues:
        print(f"  liga {l['id']}: {l['name']} ({(l.get('country') or {}).get('name')})")
    if len(mx) != 1:
        raise SystemExit("No pude identificar una sola Liga MX; usa --league-id con uno de arriba")
    return mx[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league-name", default="Liga MX")
    ap.add_argument("--league-id", type=int)
    ap.add_argument("--season-id", type=int, help="default: temporada actual de la liga")
    ap.add_argument("--stage-name", default="Apertura",
                    help="texto que debe contener el nombre de la fase regular")
    ap.add_argument("--stage-exclude", default="play,final,liguilla,repechaje,quarter,semi,knock",
                    help="palabras que descartan una fase (coma)")
    ap.add_argument("--stage-id", type=int, help="fuerza la fase (ver --plan)")
    ap.add_argument("--phase-label", default="Regular",
                    help="valor que se escribe en la columna phase")
    ap.add_argument("--plan", action="store_true",
                    help="solo muestra liga/temporada/fases/partidos, sin bajar estadisticas")
    ap.add_argument("--sleep", type=float, default=1.0, help="segundos entre peticiones")
    ap.add_argument("--cache-dir", default=".cache_sportmonks")
    ap.add_argument("--refresh", action="store_true",
                    help="vuelve a pedir metadatos y lista de partidos (los partidos terminados siguen en cache)")
    ap.add_argument("--out", default="centrales_liga_mx.csv")
    ap.add_argument("--all-positions", action="store_true",
                    help="escribe todos los jugadores (no solo CB); util para revisar")
    a = ap.parse_args()

    token = os.environ.get("SPORTMONKS_API_TOKEN")
    if not token:
        raise SystemExit("Falta la variable de entorno SPORTMONKS_API_TOKEN")
    c = Client(token, a.cache_dir, a.sleep)
    c.refresh = a.refresh  # metadatos y listas

    league = pick_league(c, a)
    season_id = a.season_id or (league.get("currentseason") or league.get("currentSeason") or {}).get("id")
    if not season_id:
        raise SystemExit("La liga no trae temporada actual; usa --season-id")
    season = c.get(f"/seasons/{season_id}")["data"]
    print(f"Liga: {league['name']} (id {league['id']}) · Temporada: {season['name']} (id {season_id})")

    stages = c.get_all(f"/stages/seasons/{season_id}")
    stages.sort(key=lambda s: s.get("sort_order") or 0)
    for s in stages:
        print(f"  fase {s['id']}: {s['name']} · {s.get('starting_at')} → {s.get('ending_at')}"
              f"{' · actual' if s.get('is_current') else ''}{' · terminada' if s.get('finished') else ''}")
    if a.stage_id:
        stage = next((s for s in stages if s["id"] == a.stage_id), None)
    else:
        bad = [w.strip().lower() for w in a.stage_exclude.split(",") if w.strip()]
        cand = [s for s in stages if a.stage_name.lower() in s["name"].lower()
                and not any(w in s["name"].lower() for w in bad)]
        stage = cand[0] if len(cand) == 1 else None
        if len(cand) != 1:
            print(f"[aviso] {len(cand)} fases coinciden con '{a.stage_name}'")
    if not stage:
        raise SystemExit("No pude elegir la fase regular sin ambiguedad; usa --stage-id")
    print(f"Fase elegida: {stage['name']} (id {stage['id']})")

    fixtures = c.get(f"/stages/{stage['id']}", {"include": "fixtures.state"})["data"].get("fixtures") or []
    done = [f for f in fixtures if ((f.get("state") or {}).get("developer_name") in FINISHED)]
    print(f"Partidos en la fase: {len(fixtures)} · terminados: {len(done)}")
    if a.plan:
        print(f"Peticiones hechas: {c.calls}. Nada mas descargado (--plan).")
        return

    c.refresh = False  # un partido terminado no cambia: siempre de cache
    rows = defaultdict(lambda: {"minutes_by_team": Counter(), "minutes_by_pos": Counter(),
                                "sums": defaultdict(float), "pct_w": 0.0, "pct_wsum": 0.0})
    seen_types, no_details = set(), []
    include = "participants;lineups.player;lineups.detailedPosition;lineups.details"
    for i, f in enumerate(sorted(done, key=lambda x: x.get("starting_at") or ""), 1):
        fx = c.get(f"/fixtures/{f['id']}", {"include": include})["data"]
        teams = {p["id"]: p["name"] for p in fx.get("participants") or []}
        lineups = fx.get("lineups") or []
        if not any(l.get("details") for l in lineups):
            no_details.append(fx.get("name") or str(f["id"]))
            continue
        for l in lineups:
            det = {}
            for d in l.get("details") or []:
                v = value_of(d)
                if v is not None:
                    det[d["type_id"]] = det.get(d["type_id"], 0) + v
            mins = det.get(T["minutes"], 0)
            if mins <= 0:
                continue  # en la banca sin jugar
            seen_types.update(det)
            r = rows[l["player_id"]]
            r["name"] = (l.get("player") or {}).get("display_name") or l.get("player_name")
            r["minutes_by_team"][teams.get(l.get("team_id"), str(l.get("team_id")))] += mins
            pos = (l.get("detailedposition") or l.get("detailedPosition") or {}).get("name") or "Unknown"
            r["minutes_by_pos"][pos] += mins
            for k, tid in T.items():
                if tid in det:
                    r["sums"][k] += det[tid]
            if T["accurate_passes_pct"] in det:
                r["pct_w"] += det[T["accurate_passes_pct"]] * mins
                r["pct_wsum"] += mins
        if i % 20 == 0:
            print(f"  {i}/{len(done)} partidos procesados (peticiones a la API: {c.calls})")

    if no_details:
        print(f"[aviso] {len(no_details)} partidos sin estadisticas por jugador; no se suman: "
              + ", ".join(no_details[:10]) + (" ..." if len(no_details) > 10 else ""))
    missing = [k for k, tid in T.items() if tid not in seen_types]
    for k in missing:
        print(f"[aviso] el tipo '{k}' (id {T[k]}) no aparece en ningun partido")

    def col(r, k):
        # NaN si el tipo no existe en toda la descarga; 0 si existe pero el jugador no lo registro
        return float("nan") if k in missing else r["sums"].get(k, 0.0)

    out = []
    for pid, r in rows.items():
        mins = sum(r["minutes_by_team"].values())
        pos_main = r["minutes_by_pos"].most_common(1)[0][0]
        cb_min = sum(m for p, m in r["minutes_by_pos"].items() if p.lower() in CB_NAMES)
        if r["sums"].get("passes"):
            pct = 100 * r["sums"].get("accurate_passes", 0) / r["sums"]["passes"]
        elif r["pct_wsum"]:
            pct = r["pct_w"] / r["pct_wsum"]
        else:
            pct = float("nan")
        err_parts = [k for k in ("error_lead_to_shot", "error_lead_to_goal") if k not in missing]
        out.append({
            "player": r["name"], "player_id": pid,
            "team": " / ".join(t for t, _ in r["minutes_by_team"].most_common()),
            "position": "CB" if pos_main.lower() in CB_NAMES else pos_main,
            "position_detail_main": pos_main, "cb_minutes": cb_min,
            "minutes": mins,
            "tackles_won": col(r, "tackles_won"), "aerials_won": col(r, "aerials_won"),
            "clearances": col(r, "clearances"), "interceptions": col(r, "interceptions"),
            "duels_won": col(r, "duels_won"), "dribbled_past": col(r, "dribbled_past"),
            "pass_completion_pct": round(pct, 2) if pct == pct else pct,
            "recoveries": col(r, "recoveries"),
            "errors": sum(r["sums"].get(k, 0.0) for k in err_parts) if err_parts else float("nan"),
            "error_lead_to_shot": col(r, "error_lead_to_shot"),
            "error_lead_to_goal": col(r, "error_lead_to_goal"),
            "n_teams": len(r["minutes_by_team"]),
            "phase": a.phase_label,
        })
    df = pd.DataFrame(out)
    if df.empty:
        raise SystemExit("No se obtuvo ningun jugador con minutos")
    if not a.all_positions:
        df = df[df["position"] == "CB"]
    extra = [c_ for c_ in df.columns if c_ not in OUT_COLS]
    df = df[OUT_COLS + extra].sort_values("minutes", ascending=False)
    df.to_csv(a.out, index=False)

    meta = {
        "fuente": "Sportmonks Football API v3 (https://api.sportmonks.com/v3/football)",
        "fecha_extraccion_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "liga": f"{league['name']} (id {league['id']})",
        "temporada": f"{season['name']} (id {season_id})",
        "fase": f"{stage['name']} (id {stage['id']})",
        "partidos_en_fase": len(fixtures), "partidos_terminados": len(done),
        "partidos_sin_estadisticas": len(no_details),
        "tipos_ausentes": missing,
        "jugadores_escritos": int(len(df)),
        "jugadores_con_varios_equipos": int((df["n_teams"] > 1).sum()),
        "peticiones_api_esta_corrida": c.calls,
    }
    meta_path = a.out.rsplit(".", 1)[0] + "_fuente.json"
    Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"Guardado: {a.out} ({len(df)} jugadores) y {meta_path}")
    print(f"Peticiones a la API en esta corrida: {c.calls}")


if __name__ == "__main__":
    sys.exit(main())
