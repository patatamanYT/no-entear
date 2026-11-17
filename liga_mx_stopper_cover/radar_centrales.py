"""Radares de Choque y Cobertura para comparar centrales (percentil por metrica).

Uso:
    python radar_centrales.py stopper_vs_cover_apertura2026_scores.csv \
        --players "Joaquim" "Federico Pereira" --tag "Apertura 26"

Genera DOS imagenes, una por rol (sufijos _choque.png y _cobertura.png):
radar sobre fondo blanco, y debajo una franja entre dos lineas con la leyenda
(punto de color, nombre y etiqueta gris).

Lee el CSV de puntajes de stopper_vs_cover.py: el grupo de comparacion son
sus filas (los centrales evaluados) y usa sus columnas de datos. Los ejes del
radar (RADAR, abajo) son propios, como en la referencia, y pueden incluir
columnas que no entran en el puntaje del rol (tackles, bloqueos, faltas, % de
duelos). Cada eje es el percentil 0-100 del jugador dentro del grupo; los
conteos van por 90' y las metricas negativas se invierten. Un eje sin datos
para al menos --min-coverage del grupo se omite (no se inventa).

Por 90' de las columnas extra (tackles, blocked_shots, fouls_committed) se usa
minutes_fotmob cuando existe, porque esas columnas pueden ir a otra jornada.
"""
import argparse
import re
import sys
import unicodedata

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from stopper_vs_cover import load_crests

# Ejes de cada radar: (columna, tipo, invertir, etiqueta)
RADAR = {
    "choque": [
        ("tackles", "count", False, "Entradas"),
        ("interceptions", "count", False, "Intercepciones"),
        ("clearances", "count", False, "Despejes"),
        ("aerials_won", "count", False, "Duelos\naéreos"),
        ("duels_won_pct", "rate", False, "Éxito en\nduelos"),
        ("blocked_shots", "count", False, "Bloqueos"),
    ],
    "cobertura": [
        ("dribbled_past", "count", True, "Evita\nregates"),
        ("pass_completion_pct", "rate", False, "Retención\nde balón"),
        ("recoveries", "count", False, "Recuperaciones"),
        ("fouls_committed", "count", True, "Evita\nfaltas"),
        ("errors", "count", True, "Evita\nerrores"),
    ],
}
EXTRA_MIN = {"tackles", "blocked_shots", "fouls_committed"}  # usan minutes_fotmob si existe


def radar_percentiles(df, metrics, min_coverage):
    """Devuelve (lista de ejes usados, DataFrame de percentiles), avisando omisiones."""
    used, pcts = [], {}
    for col, kind, inv, label in metrics:
        if col not in df.columns or df[col].notna().mean() < min_coverage:
            cov = 0 if col not in df.columns else df[col].notna().mean()
            print(f"[aviso] eje '{col}' omitido (cobertura {cov:.0%})")
            continue
        mins = df["minutes"]
        if col in EXTRA_MIN and "minutes_fotmob" in df.columns:
            mins = df["minutes_fotmob"].fillna(df["minutes"])
        v = df[col] / (mins / 90) if kind == "count" else df[col]
        p = v.rank(pct=True) * 100
        pcts[col] = 100 - p if inv else p
        used.append((col, label))
    return used, pd.DataFrame(pcts)

COLORS = ["#b98cf5", "#5ab9ef", "#f5b14c"]  # morado, azul, ambar
EDGES = ["#a26cf0", "#3fa9e8", "#e59a2a"]
INK, LABEL, MUTED, GRID, RULE = "#1f2233", "#3b3f52", "#7c8296", "#c4c4c9", "#c9c9d2"
FONT = ["Inter", "DejaVu Sans"]


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def draw(cols, labels, rows, tag, out, crests=None, note=""):
    n = len(cols)
    ang = np.pi / 2 - np.arange(n) * 2 * np.pi / n  # primer eje arriba, sentido horario
    fig = plt.figure(figsize=(6.8, 7.2), facecolor="white")
    ax = fig.add_axes([0.0, 0.3, 1.0, 0.68])
    ax.set_aspect("equal")
    ax.axis("off")

    # rejilla: 4 anillos poligonales + radios, gris claro, sin relleno
    for lvl in (0.25, 0.5, 0.75, 1.0):
        xs, ys = lvl * np.cos(ang), lvl * np.sin(ang)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=GRID, lw=1.0, zorder=1)
    for a in ang:
        ax.plot([0, np.cos(a)], [0, np.sin(a)], color=GRID, lw=1.0, zorder=1)

    # series (el primer jugador encima)
    for r, fc, ec in reversed(list(zip(rows, COLORS, EDGES))):
        v = np.clip(np.nan_to_num(np.array([r[c] for c in cols], float)) / 100, 0.04, 1)
        xs, ys = v * np.cos(ang), v * np.sin(ang)
        ax.fill(xs, ys, color=fc, alpha=0.38, lw=0, zorder=2)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=ec, lw=2.0, zorder=3)
        ax.scatter(xs, ys, s=22, color=ec, zorder=4, linewidths=0)

    for a, c, lab in zip(ang, cols, labels):
        cx, cy = np.cos(a), np.sin(a)
        ha = "center" if abs(cx) < 0.2 else ("left" if cx > 0 else "right")
        va = "center" if abs(cy) < 0.2 else ("bottom" if cy > 0 else "top")
        ax.text(1.17 * cx, 1.17 * cy, lab, ha=ha, va=va, fontsize=10.5,
                color=LABEL, family=FONT, fontweight=500, linespacing=1.25)
    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.35, 1.45)

    # franja vacia entre dos lineas y leyenda debajo
    for y in (0.255, 0.14):
        fig.add_artist(plt.Line2D([0, 1], [y, y], color=RULE, lw=1.2))
    from matplotlib.patches import Ellipse
    fw, fh = fig.get_size_inches()
    inv = fig.transFigure.inverted()
    items = []  # medir ancho total para centrar
    for r in rows:
        items.append((r, f"{r['name']}", f" · {tag}"))
    x = 0.0
    widths = []
    for r, name, t in items:
        tn = fig.text(0, -1, name, fontsize=15.5, family=FONT, fontweight=300)
        tt = fig.text(0, -1, t, fontsize=11.5, family=FONT)
        fig.canvas.draw()
        w = (tn.get_window_extent().width + tt.get_window_extent().width) / (fw * fig.dpi)
        widths.append(w)
        tn.remove()
        tt.remove()
    has_crest = [bool(crests) and r.get("team", "") in crests for r, _, _ in items]
    total = sum(widths) + 0.045 * len(items) + 0.05 * (len(items) - 1) + 0.035 * sum(has_crest)
    x = 0.5 - total / 2
    y = 0.075
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    for (r, name, t), fc, crest in zip(items, COLORS, has_crest):
        fig.add_artist(Ellipse((x + 0.011, y), 0.024, 0.024 * fw / fh,
                               transform=fig.transFigure, color=fc))
        x += 0.045
        if crest:
            fig.add_artist(AnnotationBbox(OffsetImage(crests[r["team"]], zoom=0.13),
                                          (x + 0.012, y), xycoords="figure fraction",
                                          frameon=False))
            x += 0.035
        tn = fig.text(x, y, name, fontsize=15.5, color=INK, family=FONT, fontweight=300,
                      va="center")
        fig.canvas.draw()
        x = tn.get_window_extent().transformed(inv).x1
        tt = fig.text(x, y - 0.002, t, fontsize=11.5, color=MUTED, family=FONT, va="center")
        fig.canvas.draw()
        x = tt.get_window_extent().transformed(inv).x1 + 0.05
    if note:
        fig.text(0.5, 0.015, note, fontsize=7, color=MUTED, family=FONT, ha="center")
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores")
    ap.add_argument("--players", nargs="+", required=True, help="2 o 3 nombres exactos")
    ap.add_argument("--tag", default="Apertura 26", help="texto gris junto a cada nombre")
    ap.add_argument("--out-prefix", default=None,
                    help="prefijo de salida (default: radar_<jugador1>_vs_<jugador2>)")
    ap.add_argument("--crests", action="store_true",
                    help="agrega el escudo del club en la leyenda (de --crests-dir)")
    ap.add_argument("--crests-dir", default="escudos")
    ap.add_argument("--note", default="", help="nota al pie opcional (fuente, etc.)")
    ap.add_argument("--min-coverage", type=float, default=0.8,
                    help="fraccion minima del grupo con dato para dibujar un eje")
    a = ap.parse_args()
    if not 2 <= len(a.players) <= 3:
        ap.error("compara 2 o 3 jugadores")

    df = pd.read_csv(a.scores)
    missing = [p for p in a.players if p not in set(df["player"])]
    if missing:
        raise SystemExit(f"No estan en {a.scores}: {', '.join(missing)}")
    teams = [df.loc[df["player"] == p, "team"].iloc[0] if "team" in df.columns else ""
             for p in a.players]
    crests = load_crests(teams, a.crests_dir, px=120) if a.crests else {}
    prefix = a.out_prefix or "radar_" + "_vs_".join(slug(p) for p in a.players)
    print(f"Grupo de comparacion: {len(df)} centrales de {a.scores}")

    for role, metrics in RADAR.items():
        used, pct = radar_percentiles(df, metrics, a.min_coverage)
        if len(used) < 3:
            print(f"[aviso] {role}: solo {len(used)} ejes; un radar necesita 3 o mas")
            continue
        cols = [c for c, _ in used]
        rows = []
        for p, t in zip(a.players, teams):
            i = df.index[df["player"] == p][0]
            r = {"name": p, "team": t, **{c: pct.at[i, c] for c in cols}}
            gaps = [c for c in cols if pd.isna(r[c])]
            if gaps:
                print(f"[aviso] {p} sin dato en {', '.join(gaps)}: se dibuja en el centro")
            rows.append(r)
            print(f"{role:10s} {p:20s} " + "  ".join(f"{c}={r[c]:.0f}" for c in cols
                                                      if not pd.isna(r[c])))
        draw(cols, [l for _, l in used], rows, a.tag, f"{prefix}_{role}.png", crests, a.note)


if __name__ == "__main__":
    sys.exit(main())
