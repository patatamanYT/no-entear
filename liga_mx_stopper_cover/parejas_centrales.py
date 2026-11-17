"""¿Se complementan los centrales titulares de cada equipo?

Uso:
    python parejas_centrales.py centrales_apertura2026_j16.csv parejas_scores.csv \
        --out parejas_centrales.png

- Titulares y cuantos (2 o 3): de formaciones.csv (team,centrales,origen,
  titulares,nota). `titulares` son nombres separados por " / ", escritos como
  en la columna player. Si un equipo no tiene titulares ahi, se usan los
  centrales con mas minutos; si no esta en el archivo, se estima la linea:
  3 si su tercer central tiene >= --back3-min minutos (default 720), si no 2.
  Con --write-formations se guarda esa estimacion para corregirla a mano.
  Un titular que no esta en el CSV de datos sale como "Sin datos".
- Perfil de cada central con su puntaje (scores CSV de stopper_vs_cover.py):
    Ambos       choque >= 60 y cobertura >= 60
    Choque      choque >= 55 y choque - cobertura >= 15
    Cobertura   cobertura >= 55 y cobertura - choque >= 15
    Equilibrado lo demas, con ambos >= 40
    Bajo        lo demas
    Sin datos   el jugador no tiene puntaje
- Veredicto de la linea:
    Completa            hay un central "Ambos"
    Se complementan     hay al menos un "Choque" y un "Cobertura"
    Solo choque         2+ "Choque" y ningun "Cobertura"
    Solo cobertura      2+ "Cobertura" y ningun "Choque"
    Datos incompletos   falta el puntaje de un titular y lo conocido no decide
    Sin complemento     lo demas
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch

from stopper_vs_cover import BG, EDGE, INK, MONO, MUTED, PANEL, SANS, load_crests

DISPLAY = {"UANL": "Tigres", "UNAM": "Pumas", "Atlético San Luis": "San Luis"}  # nombre en tarjeta
PROFILE_COLORS = {"Ambos": "#7c3aed", "Choque": "#ea580c", "Cobertura": "#16a34a",
                  "Equilibrado": "#64748b", "Bajo": "#b6b0a4", "Sin datos": "#d6d1c6"}
VERDICTS = [  # orden de la grafica, color
    ("Completa", "#7c3aed"), ("Se complementan", "#16a34a"),
    ("Solo choque", "#ea580c"), ("Solo cobertura", "#0d9488"),
    ("Sin complemento", "#64748b"), ("Datos incompletos", "#a8a29e"),
]


def profile(s, c):
    if pd.isna(s) or pd.isna(c):
        return "Sin datos"
    if s >= 60 and c >= 60:
        return "Ambos"
    if s >= 55 and s - c >= 15:
        return "Choque"
    if c >= 55 and c - s >= 15:
        return "Cobertura"
    return "Equilibrado" if min(s, c) >= 40 else "Bajo"


def verdict(profiles):
    known = [p for p in profiles if p != "Sin datos"]
    if "Ambos" in known:
        return "Completa"
    if "Choque" in known and "Cobertura" in known:
        return "Se complementan"
    if len(known) < len(profiles):
        return "Datos incompletos"
    if known.count("Choque") >= 2 and "Cobertura" not in known:
        return "Solo choque"
    if known.count("Cobertura") >= 2 and "Choque" not in known:
        return "Solo cobertura"
    return "Sin complemento"


MARGIN = 3  # puntos de percentil para marcar un veredicto "en el limite"


def alt_profiles(s, c, m=MARGIN):
    """Perfiles posibles si Ch y Cb se mueven hasta +-m puntos."""
    if pd.isna(s) or pd.isna(c):
        return {"Sin datos"}
    return {profile(min(100, max(0, s + ds)), min(100, max(0, c + dc)))
            for ds in (-m, 0, m) for dc in (-m, 0, m)}


def borderline(players):
    """True si alguna combinacion de perfiles alternativos cambia el veredicto."""
    from itertools import product
    base = verdict([p["profile"] for p in players])
    return any(verdict(list(combo)) != base
               for combo in product(*[sorted(alt_profiles(p["stopper"], p["cover"])) for p in players]))


def build(data, scores, formations, back3_min):
    sc = scores.set_index("player")[["stopper", "cover"]]
    out = []
    for team, g in data.sort_values("minutes", ascending=False).groupby("team"):
        named = []
        if team in formations:
            n, origin, named = formations[team]
        else:
            n = 3 if (g["minutes"] >= back3_min).sum() >= 3 else 2
            origin = f"estimado (3er central >= {back3_min}')" if n == 3 else "estimado"
        names = named or list(g.head(n)["player"])
        mins = dict(zip(g["player"], g["minutes"]))
        players = []
        for name in names:
            s, c = (sc.at[name, "stopper"], sc.at[name, "cover"]) \
                if name in sc.index else (float("nan"), float("nan"))
            players.append({"player": name, "minutes": int(mins.get(name, 0)), "stopper": s,
                            "cover": c, "profile": profile(s, c), "in_data": name in mins})
        out.append({"team": team, "n": n, "origin": origin, "players": players,
                    "verdict": verdict([p["profile"] for p in players]),
                    "borderline": borderline(players)})
    order = {v: i for i, (v, _) in enumerate(VERDICTS)}
    return sorted(out, key=lambda t: (order[t["verdict"]], t["team"]))


def draw(teams, a):
    cols, rows = 6, -(-len(teams) // 6)
    fig = plt.figure(figsize=(18, 4.0 + 3.25 * rows), facecolor=BG)
    H = fig.get_size_inches()[1]
    top = 1 - 2.6 / H                      # inicio de la rejilla (figura)
    ch, gap = 3.0 / H, 0.25 / H            # alto de tarjeta y separacion
    cw, gx, x0 = 0.148, 0.012, 0.035
    crests = load_crests([t["team"] for t in teams], a.crests_dir, px=120)

    fig.text(x0, 1 - 0.55 / H, a.header.upper(), fontsize=11, color=MUTED, family=MONO, va="center")
    fig.text(x0, 1 - 1.2 / H, a.title, fontsize=34, fontweight="heavy", color=INK, family=SANS, va="center")
    fig.text(x0, 1 - 1.8 / H, a.subtitle, fontsize=14, color="#6b665c", family=SANS, va="center")
    # leyenda de perfiles
    x = x0
    shown = {p["profile"] for t in teams for p in t["players"]}  # solo perfiles que aparecen
    for name in [n for n in ("Choque", "Cobertura", "Ambos", "Equilibrado", "Bajo", "Sin datos") if n in shown]:
        fig.patches.append(FancyBboxPatch((x, 1 - 2.22 / H - 0.006), 0.009, 0.012,
                                          boxstyle="round,pad=0,rounding_size=0.004",
                                          transform=fig.transFigure, fc=PROFILE_COLORS[name], ec="none"))
        t = fig.text(x + 0.013, 1 - 2.22 / H, name, fontsize=10.5, color=INK, family=SANS, va="center")
        fig.canvas.draw()
        x = t.get_window_extent().transformed(fig.transFigure.inverted()).x1 + 0.022

    for i, t in enumerate(teams):
        cx = x0 + (i % cols) * (cw + gx)
        cy = top - (i // cols + 1) * ch - (i // cols) * gap
        vcolor = dict(VERDICTS)[t["verdict"]]
        fig.patches.append(FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0,rounding_size=0.008",
                                          transform=fig.transFigure, fc=PANEL, ec=EDGE, lw=1.4))
        fig.patches.append(FancyBboxPatch((cx, cy), 0.005, ch, boxstyle="square,pad=0",
                                          transform=fig.transFigure, fc=vcolor, ec="none"))
        hy = cy + ch - 0.42 / H
        if t["team"] in crests:
            fig.add_artist(AnnotationBbox(OffsetImage(crests[t["team"]], zoom=0.2),
                                          (cx + 0.022, hy), xycoords="figure fraction", frameon=False))
        fig.text(cx + 0.042, hy + 0.06 / H, DISPLAY.get(t["team"], t["team"]), fontsize=12.5, fontweight="bold", color=INK,
                 family=SANS, va="center")
        fig.text(cx + 0.042, hy - 0.2 / H, f"Línea de {t['n']}" + (" (est.)" if "estimado" in str(t["origin"]) else ""),
                 fontsize=9, color=MUTED, family=SANS, va="center")
        for j, p in enumerate(t["players"]):
            py = hy - (0.72 + 0.44 * j) / H
            fig.patches.append(FancyBboxPatch((cx + 0.012, py - 0.007), 0.007, 0.014,
                                              boxstyle="round,pad=0,rounding_size=0.003",
                                              transform=fig.transFigure, fc=PROFILE_COLORS[p["profile"]], ec="none"))
            name = p["player"] if len(p["player"]) <= 19 else p["player"][:18] + "."
            fig.text(cx + 0.024, py + 0.07 / H, name, fontsize=10.5, color=INK, family=SANS,
                     fontweight="semibold", va="center")
            sub = (f"{p['profile']} · Ch {p['stopper']:.0f} · Cb {p['cover']:.0f}"
                   if p["profile"] != "Sin datos"
                   else ("Sin datos" if p["in_data"] else "Sin datos (no está en el CSV)"))
            fig.text(cx + 0.024, py - 0.13 / H, sub, fontsize=8.5, color=MUTED, family=SANS, va="center")
        fig.text(cx + cw / 2, cy + 0.22 / H, t["verdict"].upper() + (" *" if t["borderline"] else ""), fontsize=9.5, fontweight="bold",
                 color="white", family=SANS, ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.4,rounding_size=0.8", fc=vcolor, ec="none"))

    note = [
        "Línea y titulares: alineaciones J1–J16 (FotMob/FBref y otras), en formaciones.csv; "
        "(est.) = estimado por minutos.",
        f"* Veredicto en el límite: cambia si algún titular se mueve ±{MARGIN} puntos en Choque o Cobertura.",
        "Perfil: Ambos = Ch y Cb ≥ 60 · Choque = Ch ≥ 55 y 15+ sobre Cb · Cobertura = Cb ≥ 55 y 15+ sobre Ch · "
        "Ch/Cb = percentil Choque/Cobertura.",
    ]
    if a.source:
        note.append(f"Fuente: {a.source}")
    fig.text(x0, 0.012, "\n".join(note), fontsize=8, color=MUTED, family=MONO, va="bottom", linespacing=1.6)
    fig.savefig(a.out, dpi=170, facecolor=BG)
    plt.close(fig)
    print(f"Guardado: {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", help="CSV de datos (todos los centrales, con minutes y team)")
    ap.add_argument("scores", help="CSV de puntajes de stopper_vs_cover.py")
    ap.add_argument("--formations", default="formaciones.csv")
    ap.add_argument("--write-formations", action="store_true",
                    help="guarda la estimacion de linea de 2/3 en --formations y termina")
    ap.add_argument("--back3-min", type=int, default=720)
    ap.add_argument("--crests-dir", default="escudos")
    ap.add_argument("--header", default="Liga MX Apertura 2026 · Centrales")
    ap.add_argument("--title", default="¿Se complementan sus centrales?")
    ap.add_argument("--subtitle", default="Un central de choque al lado de uno de cobertura")
    ap.add_argument("--source", default="")
    ap.add_argument("--out", default="parejas_centrales.png")
    a = ap.parse_args()

    data = pd.read_csv(a.data)
    if "phase" in data.columns:
        data = data[data["phase"] == "Regular"]
    formations = {}
    if Path(a.formations).exists() and not a.write_formations:
        f = pd.read_csv(a.formations)
        tit = f["titulares"] if "titulares" in f.columns else pd.Series("", index=f.index)
        formations = {r.team: (int(r.centrales), r.origen,
                               [x.strip() for x in str(t).split("/") if x.strip()] if pd.notna(t) else [])
                      for r, t in zip(f.itertuples(), tit)}
    teams = build(data, pd.read_csv(a.scores), formations, a.back3_min)

    if a.write_formations:
        pd.DataFrame([{"team": t["team"], "centrales": t["n"], "origen": t["origin"]}
                      for t in teams]).sort_values("team").to_csv(a.formations, index=False)
        print(f"Formaciones estimadas guardadas en {a.formations}; corrige 'centrales' y 'origen' a mano")
        return

    for t in teams:
        print(f"{t['verdict'] + (' *' if t['borderline'] else ''):20s} {t['team']:18s} (línea de {t['n']}, {t['origin']}): "
              + " | ".join(f"{p['player']} [{p['profile']}"
                           + (f" {p['stopper']:.0f}/{p['cover']:.0f}]" if p["profile"] != "Sin datos" else "]")
                           for p in t["players"]))
    pd.DataFrame([{"team": t["team"], "linea": t["n"], "origen": t["origin"], "veredicto": t["verdict"],
                   "en_el_limite": t["borderline"],
                   **{f"central_{j + 1}": f"{p['player']} ({p['profile']})" for j, p in enumerate(t["players"])}}
                  for t in teams]).to_csv(a.out.rsplit(".", 1)[0] + ".csv", index=False)
    draw(teams, a)


if __name__ == "__main__":
    sys.exit(main())
