"""Radares de Choque y Cobertura para comparar centrales (percentil por metrica).

Uso:
    python radar_centrales.py stopper_vs_cover_apertura2026_scores.csv \
        --players "Joaquim" "Federico Pereira" --tag "Apertura 2026" --out radar.png

Lee el CSV de puntajes que genera stopper_vs_cover.py (columnas pct_<metrica>,
percentil 0-100 dentro del grupo, ya invertido en las metricas donde menos es
mejor) y dibuja dos radares lado a lado: Choque y Cobertura. Solo aparecen los
ejes de las metricas que realmente se usaron (las omitidas no tienen pct_).
"""
import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from stopper_vs_cover import COVER, STOPPER, SANS, load_crests

COLORS = ["#a970f5", "#4fb3ea", "#f59e0b"]  # morado, azul, ambar
INK, MUTED, GRID = "#2d2f3a", "#7a7f8f", "#c9c9cf"
LABELS = {
    "tackles_won": "Entradas\nganadas", "aerials_won": "Duelos\naéreos",
    "clearances": "Despejes", "interceptions": "Intercepciones",
    "duels_won": "Duelos\nganados", "dribbled_past": "Evita\nregates",
    "pass_completion_pct": "Retención\n(% de pase)", "recoveries": "Recuperaciones",
    "errors": "Evita\nerrores",
}


def radar(ax, labels, series, title):
    n = len(labels)
    ang = np.pi / 2 - np.arange(n) * 2 * np.pi / n  # primer eje arriba, sentido horario
    ax.set_aspect("equal")
    ax.axis("off")
    # rejilla poligonal (4 anillos: 25/50/75/100) y radios
    for k, lvl in enumerate((0.25, 0.5, 0.75, 1.0)):
        xs, ys = lvl * np.cos(ang), lvl * np.sin(ang)
        ax.fill(xs, ys, color="#eef0f5" if k % 2 else "white", zorder=0)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=GRID, lw=1.1 if lvl == 1 else 0.8,
                zorder=1)
    for a in ang:
        ax.plot([0, np.cos(a)], [0, np.sin(a)], color=GRID, lw=0.8, zorder=1)
    # el primer jugador se dibuja al final para que quede encima
    for (name, vals), color in reversed(list(zip(series, COLORS))):
        r = np.clip(np.asarray(vals, float) / 100, 0.03, 1)
        xs, ys = r * np.cos(ang), r * np.sin(ang)
        ax.fill(xs, ys, color=color, alpha=0.32, zorder=2)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=color, lw=2.2, zorder=3)
        ax.scatter(xs, ys, s=28, color=color, zorder=4)
    for a, lab in zip(ang, labels):
        x, y = 1.2 * np.cos(a), 1.2 * np.sin(a)
        ha = "center" if abs(np.cos(a)) < 0.2 else ("left" if np.cos(a) > 0 else "right")
        va = "center" if abs(np.sin(a)) < 0.2 else ("bottom" if np.sin(a) > 0 else "top")
        ax.text(x, y, lab, ha=ha, va=va, fontsize=11, color=INK, family=SANS,
                fontweight=500, linespacing=1.15)
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.6, 1.6)
    ax.set_title(title, fontsize=17, fontweight="bold", color=INK, family=SANS, pad=6)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores")
    ap.add_argument("--players", nargs="+", required=True, help="2 o 3 nombres exactos")
    ap.add_argument("--tag", default="Apertura 2026", help="texto gris junto a cada nombre")
    ap.add_argument("--crests-dir", default="escudos")
    ap.add_argument("--source", default="", help="nota al pie")
    ap.add_argument("--out", default="radar_centrales.png")
    a = ap.parse_args()
    if not 2 <= len(a.players) <= 3:
        ap.error("compara 2 o 3 jugadores")

    df = pd.read_csv(a.scores)
    missing = [p for p in a.players if p not in set(df["player"])]
    if missing:
        raise SystemExit(f"No estan en {a.scores}: {', '.join(missing)}")
    rows = [df[df["player"] == p].iloc[0] for p in a.players]

    fig = plt.figure(figsize=(13, 7.4), facecolor="white")
    panels = []
    for i, (metrics, title) in enumerate(((STOPPER, "Choque"), (COVER, "Cobertura"))):
        cols = [c for c, _, _ in metrics if f"pct_{c}" in df.columns]
        if len(cols) < 3:
            print(f"[aviso] {title}: solo {len(cols)} metricas; un radar necesita 3+")
            continue
        panels.append((cols, title))
    for i, (cols, title) in enumerate(panels):
        ax = fig.add_axes([0.02 + i * 0.49, 0.2, 0.47, 0.72])
        radar(ax, [LABELS.get(c, c) for c in cols],
              [(r["player"], [r[f"pct_{c}"] for c in cols]) for r in rows], title)
        for r in rows:
            print(f"{title:10s} {r['player']:20s} "
                  + "  ".join(f"{c}={r[f'pct_{c}']:.0f}" for c in cols))

    # Leyenda: punto de color + escudo + nombre + etiqueta gris
    fig.add_artist(plt.Line2D([0.06, 0.94], [0.135, 0.135], color="#d4d4da", lw=1))
    crests = load_crests([r.get("team", "") for r in rows], a.crests_dir, px=120)
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    from matplotlib.patches import Ellipse
    fw, fh = fig.get_size_inches()
    x = 0.5 - 0.17 * len(rows)
    for r, color in zip(rows, COLORS):
        fig.add_artist(Ellipse((x, 0.075), 0.011, 0.011 * fw / fh,
                               transform=fig.transFigure, color=color))
        x += 0.016
        if r.get("team", "") in crests:
            fig.add_artist(AnnotationBbox(OffsetImage(crests[r["team"]], zoom=0.17), (x + 0.012, 0.075),
                                          xycoords="figure fraction", frameon=False))
            x += 0.03
        t = fig.text(x, 0.075, r["player"], fontsize=17, color=INK, family=SANS, va="center")
        fig.canvas.draw()
        x = t.get_window_extent().transformed(fig.transFigure.inverted()).x1 + 0.008
        t = fig.text(x, 0.072, f"· {a.tag}", fontsize=12.5, color=MUTED, family=SANS, va="center")
        fig.canvas.draw()
        x = t.get_window_extent().transformed(fig.transFigure.inverted()).x1 + 0.04
    note = "Percentil dentro del grupo de centrales (0 = peor, 100 = mejor; las métricas negativas van invertidas)"
    if a.source:
        note += f" · {a.source}"
    fig.text(0.5, 0.018, note, fontsize=8, color=MUTED, family=SANS, ha="center")
    fig.savefig(a.out, dpi=200, facecolor="white")
    print(f"Guardado: {a.out}")


if __name__ == "__main__":
    sys.exit(main())
