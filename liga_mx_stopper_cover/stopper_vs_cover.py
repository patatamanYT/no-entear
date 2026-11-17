"""Stopper CB vs Cover CB (Liga MX, fase regular).

Uso:
    python stopper_vs_cover.py datos.csv --min-minutes 450 --out grafica.png

CSV esperado (una fila por jugador, acumulado de la fase regular):
    player, team, position, minutes, <metricas...>
Opcional: columna `phase` si el CSV mezcla fase regular y liguilla
(usa --phase-col phase --phase-value Regular).
"""
import argparse

import matplotlib.pyplot as plt
import pandas as pd

# Metrica -> (columna, tipo, invertir)
#   tipo "count": se divide entre minutos/90
#   tipo "rate":  ya es porcentaje/tasa, se usa tal cual
#   invertir=True: menos es mejor
STOPPER = [
    ("tackles_won", "count", False),
    ("aerials_won", "count", False),
    ("clearances", "count", False),
    ("interceptions", "count", False),
    ("duels_won", "count", False),
]
COVER = [
    ("dribbled_past", "count", True),
    ("pass_completion_pct", "rate", False),  # retencion del balon
    ("recoveries", "count", False),
    ("errors", "count", True),
]


def pct_rank(s: pd.Series) -> pd.Series:
    return s.rank(pct=True) * 100


def role_score(df: pd.DataFrame, metrics) -> pd.Series:
    cols = []
    for col, kind, invert in metrics:
        if col not in df.columns:
            print(f"[aviso] falta la columna '{col}', se omite")
            continue
        v = df[col] / (df["minutes"] / 90) if kind == "count" else df[col]
        p = pct_rank(v)
        cols.append(100 - p if invert else p)
    if not cols:
        raise SystemExit("No hay metricas disponibles para este rol")
    raw = pd.concat(cols, axis=1).mean(axis=1)
    return pct_rank(raw)  # percentil final dentro del grupo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--min-minutes", type=int, default=450)
    ap.add_argument("--position-col", default="position")
    ap.add_argument("--position-value", default="CB")
    ap.add_argument("--phase-col", default=None)
    ap.add_argument("--phase-value", default="Regular")
    ap.add_argument("--out", default="stopper_vs_cover.png")
    a = ap.parse_args()

    df = pd.read_csv(a.csv)
    if a.phase_col:
        df = df[df[a.phase_col] == a.phase_value]
    df = df[df[a.position_col] == a.position_value]
    df = df[df["minutes"] >= a.min_minutes].copy()
    print(f"Centrales en el grupo: {len(df)}")

    df["stopper"] = role_score(df, STOPPER)
    df["cover"] = role_score(df, COVER)

    fig, ax = plt.subplots(figsize=(9, 8))
    T = 70  # umbral de los recuadros resaltados
    ax.axvspan(T, 100, ymin=T / 100, ymax=1, color="#7c3aed", alpha=0.10)
    ax.axvspan(0, 100 - T, ymin=T / 100, ymax=1, color="#16a34a", alpha=0.10)
    ax.axvspan(T, 100, ymin=0, ymax=1 - T / 100, color="#ea580c", alpha=0.10)
    ax.axhline(50, ls="--", c="gray", lw=1)
    ax.axvline(50, ls="--", c="gray", lw=1)
    ax.scatter(df["stopper"], df["cover"], s=40, color="#1f2937", zorder=3)

    texts = [ax.text(r.stopper + 1, r.cover + 1, r.player, fontsize=8)
             for r in df.itertuples()]
    try:
        from adjustText import adjust_text
        adjust_text(texts, ax=ax)
    except ImportError:
        pass  # sin adjustText las etiquetas pueden encimarse

    ax.set(xlim=(-3, 103), ylim=(-3, 103),
           xlabel="STOPPER CB →", ylabel="COVER CB →",
           title="Stopper CB vs Cover CB · Liga MX (fase regular)")
    fig.tight_layout()
    fig.savefig(a.out, dpi=150)
    df.sort_values("cover", ascending=False).to_csv(
        a.out.replace(".png", "_scores.csv"), index=False)
    print(f"Guardado: {a.out}")


if __name__ == "__main__":
    main()
