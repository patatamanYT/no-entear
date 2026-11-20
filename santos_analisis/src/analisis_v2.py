#!/usr/bin/env python3
"""
Santos Laguna, Apertura 2026 — v2: datos adicionales (portero, defensa, construcción, roles, disponibilidad).

Prueba las hipótesis pre-registradas en output/v2/hipotesis_preregistradas.md y escribe en output/v2/:
  tablas_v2.xlsx (incluye hoja 'filas_usadas_ND'), PNG y resultados_v2.json.
No modifica nada de output/ (v1).

Uso (desde santos_analisis/):  python3 src/analisis_v2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import poisson  # noqa: E402

SEED = 20261120
N_BOOT = 10_000
SANTOS = "Santos Laguna"
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT = BASE / "output" / "v2"
OUT.mkdir(parents=True, exist_ok=True)

B1, B2, B3 = list(range(1, 8)), list(range(8, 14)), list(range(14, 17))
B23 = list(range(8, 17))
BLOQUES = {"J1–J7": B1, "J8–J13": B2, "J14–J16": B3, "J8–J16": B23}
PROHIBIDAS = ["entradas_ganadas", "perdidas_de_balon", "pases_progresivos", "pases_clave",
              "conducciones_progresivas", "salidas_exitosas", "grandes_ocasiones_creadas",
              "regates_exitosos", "centros_precisos", "faltas_recibidas"]
INCONSISTENTES_PARADAS = [6, 15]
# Tabla "jornadas sin participación" del README de datos adicionales (no del CSV de eventos)
SIN_PARTICIPACION = {
    "Efraín Orona": [1, 2, 3, 5, 9, 14, 15, 16],
    "Diego González": [12, 15, 16],
}
PARCIAL = {"Efraín Orona": {13: "salió lesionado al 21"}, "Diego González": {14: "jugó completo, lesionado durante el partido"}}

C_FAVOR, C_CONTRA, C_TER, C_GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
C_TXT, C_TXT2, C_GRID, C_SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COLB = {"J1–J7": C_CONTRA, "J8–J13": C_FAVOR, "J14–J16": C_GRIS, "J8–J16": C_TER}
plt.rcParams.update({
    "figure.facecolor": C_SURF, "axes.facecolor": C_SURF, "savefig.facecolor": C_SURF,
    "axes.edgecolor": C_GRID, "axes.labelcolor": C_TXT2, "xtick.color": C_TXT2, "ytick.color": C_TXT2,
    "text.color": C_TXT, "axes.grid": True, "grid.color": C_GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "lines.linewidth": 2, "axes.axisbelow": True,
})

TABLAS: dict[str, pd.DataFrame] = {}
FILAS: list[dict] = []   # registro de filas usadas / excluidas por prueba
R: dict = {}


def tabla(n, df):
    TABLAS[n[:31]] = df
    return df


def log_filas(prueba, metrica, alcance, usadas, excl_nd, excl_regla=0, nota=""):
    FILAS.append({"prueba": prueba, "metrica": metrica, "alcance": alcance, "filas_usadas": int(usadas),
                  "filas_excluidas_ND": int(excl_nd), "filas_excluidas_por_regla": int(excl_regla), "nota": nota})


def leer(n):
    return pd.read_csv(DATA / n, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def num(df, cols):
    df = df.copy()
    for c in cols:
        s = df[c].str.strip()
        conv = pd.to_numeric(s.where(s != "N/D"), errors="coerce")
        bad = s[(s != "N/D") & conv.isna()]
        if len(bad):
            sys.exit(f"ALTO: {c} tiene valores no numéricos distintos de N/D: {bad.unique()[:5]}")
        df[c] = conv
    return df


# ---------------------------------------------------------------------------
# Bootstrap por partidos con razón de sumas
# ---------------------------------------------------------------------------
class Boot:
    def __init__(self, rng):
        self.rng = rng
        self.idx = {}

    def indices(self, n):
        # Mismos índices de remuestreo para todos los estadísticos con el mismo n (reproducible)
        if n not in self.idx:
            self.idx[n] = self.rng.integers(0, n, size=(N_BOOT, n))
        return self.idx[n]

    def ratio(self, numv, denv, scale=1.0):
        numv, denv = np.asarray(numv, float), np.asarray(denv, float)
        est = numv.sum() / denv.sum() * scale if denv.sum() else np.nan
        if len(numv) < 2:
            return est, np.nan, np.nan, np.full(N_BOOT, est)
        ix = self.indices(len(numv))
        with np.errstate(divide="ignore", invalid="ignore"):
            s = numv[ix].sum(1) / denv[ix].sum(1) * scale
        return est, np.nanquantile(s, 0.025), np.nanquantile(s, 0.975), s


def ci_diff(sa, sb):
    d = sb - sa
    return np.nanquantile(d, 0.025), np.nanquantile(d, 0.975)


def stat_bloques(bt, M, numc, denc, scale=1.0, bloques=BLOQUES, base="J1–J7"):
    """M: tabla por jornada con columnas numc y denc. Devuelve filas por bloque y diferencias vs base."""
    out, samples = [], {}
    for bn, bj in bloques.items():
        s = M[M.jornada.isin(bj)].dropna(subset=[numc, denc])
        est, lo, hi, smp = bt.ratio(s[numc], s[denc], scale)
        samples[bn] = smp
        out.append({"bloque": bn, "n_partidos": len(s), "valor": est, "IC95_lo": lo, "IC95_hi": hi})
    for r in out:
        if r["bloque"] != base:
            lo, hi = ci_diff(samples[base], samples[r["bloque"]])
            base_v = [x for x in out if x["bloque"] == base][0]["valor"]
            r.update({"dif_vs_J1_J7": r["valor"] - base_v, "dif_IC95_lo": lo, "dif_IC95_hi": hi})
    return out


def variantes():
    """Cortes alternativos y leave-one-out sobre J8–J13."""
    v = [(f"corte J{c}: J1–J{c - 1} vs J{c}–J13", list(range(1, c)), list(range(c, 14))) for c in [7, 8, 9]]
    v += [(f"J1–J7 vs J8–J13 sin J{k}", B1, [x for x in B2 if x != k]) for k in B2]
    return v


# ---------------------------------------------------------------------------
# PASO 0 — Validación
# ---------------------------------------------------------------------------
def validar():
    base_p = num(leer("partidos_santos.csv"), ["jornada", "goles_santos", "goles_rival", "xg_santos", "xg_rival",
                                                "xg_santos_sin_penales", "xg_rival_sin_penales", "tiros_rival",
                                                "tiros_puerta_rival", "posesion_santos", "puntos", "penales_en_contra",
                                                "penales_a_favor"])
    base_j = num(leer("jugadores_partido.csv"), ["jornada", "minutos", "xg"])
    gk = num(leer("portero_partido.csv"), ["jornada", "minutos", "goles_recibidos", "tiros_a_puerta_recibidos", "paradas",
                                          "xgot_en_contra", "goles_evitados", "xg_en_contra", "penales_recibidos",
                                          "penales_atajados", "pases_largos_precisos"])
    dcols = ["jornada", "minutos", "duelos_ganados", "duelos_totales", "duelos_aereos_ganados", "duelos_aereos_totales",
             "recuperaciones", "intercepciones", "despejes", "bloqueos_de_tiro", "entradas_totales", "faltas_cometidas"]
    de = num(leer("defensa_jugador_partido.csv"), dcols)
    ccols = ["jornada", "minutos", "pases_completados", "pases_intentados", "pases_largos_precisos", "ocasiones_creadas",
             "xa", "toques_area_rival"]
    co = num(leer("construccion_jugador_partido.csv"), ccols)
    ro = leer("posicion_rol_partido.csv")
    ro["jornada"] = ro.jornada.astype(int)
    di = leer("disponibilidad_jugadores.csv")
    crudos = {"portero_partido.csv": leer("portero_partido.csv"), "defensa_jugador_partido.csv": leer("defensa_jugador_partido.csv"),
              "construccion_jugador_partido.csv": leer("construccion_jugador_partido.csv"),
              "posicion_rol_partido.csv": leer("posicion_rol_partido.csv"), "disponibilidad_jugadores.csv": di}
    for d in (base_p, base_j, gk, de, co):
        d["jornada"] = d["jornada"].astype(int)

    # % N/D por campo
    nd = []
    for n, d in crudos.items():
        for c in d.columns:
            k = int((d[c].str.strip() == "N/D").sum())
            nd.append({"archivo": n, "campo": c, "filas_ND": k, "filas": len(d), "%_ND": round(100 * k / len(d), 2),
                       "uso": "PROHIBIDA (no se usa)" if c in PROHIBIDAS else ("" if k == 0 else "se excluyen filas N/D")})
    tabla("0_ND_por_campo", pd.DataFrame(nd))

    chk = []

    def ok(nombre, cond, det=""):
        chk.append({"verificacion": nombre, "resultado": "OK" if cond else "FALLA", "detalle": det})

    key = ["jornada", "jugador"]
    gk_k = gk.rename(columns={"portero": "jugador"})
    for n, d in [("portero", gk_k), ("defensa", de), ("construccion", co), ("roles", ro)]:
        ok(f"{n}: clave (jornada, nombre) sin duplicados", not d.duplicated(key).any(), f"{d.duplicated(key).sum()} duplicados")
        m = d[key].merge(base_j[key], how="left", indicator=True)
        ok(f"{n}: todas las claves existen en jugadores_partido (nombre exacto)", (m._merge == "both").all(),
           f"{(m._merge != 'both').sum()} sin pareja")
    # cobertura
    campo = base_j[base_j.posicion != "Portero"]
    ok("defensa = todas las participaciones de jugadores de campo", len(de) == len(campo) and
       set(map(tuple, de[key].values)) == set(map(tuple, campo[key].values)), f"{len(de)} vs {len(campo)}")
    ok("construccion = todas las participaciones", set(map(tuple, co[key].values)) == set(map(tuple, base_j[key].values)),
       f"{len(co)} vs {len(base_j)}")
    tit = base_j[base_j.titular == "S"]
    ok("roles = titulares (titular=S)", set(map(tuple, ro[key].values)) == set(map(tuple, tit[key].values)), f"{len(ro)} filas")
    ok("roles: 11 por jornada", (ro.groupby("jornada").size() == 11).all())
    f_ro = ro.groupby("jornada").formacion_inicial.first()
    ok("roles: formación = formacion_santos de la base", (f_ro.values == base_p.set_index("jornada").formacion_santos.loc[f_ro.index].values).all())
    # minutos
    for n, d in [("portero", gk_k), ("defensa", de), ("construccion", co)]:
        m = d[key + ["minutos"]].merge(base_j[key + ["minutos"]], on=key, suffixes=("", "_base"))
        dif = (m.minutos != m.minutos_base).sum()
        ok(f"{n}: minutos = jugadores_partido", dif == 0, f"{dif} diferencias en {len(m)} filas")
    # portero vs base
    g = gk.set_index("jornada").sort_index()
    p = base_p.set_index("jornada").sort_index()
    ok("portero: 16 partidos, 90 min, mismo portero", len(g) == 16 and (g.minutos == 90).all() and g.portero.nunique() == 1,
       g.portero.iloc[0])
    ok("portero: goles recibidos = goles_rival (total 20)", (g.goles_recibidos == p.goles_rival).all() and g.goles_recibidos.sum() == 20,
       f"total {int(g.goles_recibidos.sum())}")
    ok("portero: xg_en_contra = xg_rival", np.allclose(g.xg_en_contra, p.xg_rival))
    ok("portero: tiros a puerta recibidos = tiros_puerta_rival", (g.tiros_a_puerta_recibidos == p.tiros_puerta_rival).all())
    ok("portero: goles_evitados = xGOT − goles (±0.01)", np.allclose(g.goles_evitados, g.xgot_en_contra - g.goles_recibidos, atol=0.011))
    ok("portero: penales recibidos = penales_en_contra", (g.penales_recibidos == p.penales_en_contra).all())
    # J10
    j10 = g.loc[10]
    coh = j10.xgot_en_contra == 0 and j10.tiros_a_puerta_recibidos == 0 and j10.goles_recibidos == 0 and j10.paradas == 0 \
        and p.loc[10, "tiros_puerta_rival"] == 0
    ok("J10 Pachuca: xGOT 0.00 coherente con 0 tiros a puerta, 0 paradas, 0 goles", coh,
       f"xGOT={j10.xgot_en_contra}, TaP={int(j10.tiros_a_puerta_recibidos)} (base {int(p.loc[10, 'tiros_puerta_rival'])}), "
       f"paradas={int(j10.paradas)}, goles={int(j10.goles_recibidos)}, xG en contra={j10.xg_en_contra} (Pachuca remató 11 veces, ninguna a puerta)")
    # inconsistencias paradas
    inc = g[(g.paradas + g.goles_recibidos) != g.tiros_a_puerta_recibidos].index.tolist()
    ok("paradas + goles = tiros a puerta salvo J6 y J15 (inconsistencias conocidas)", sorted(inc) == INCONSISTENTES_PARADAS,
       f"jornadas que no cuadran: {inc}")
    ok("disponibilidad: nombres existen en la base", di.jugador.isin(base_j.jugador).all())
    tabla("0_verificaciones", pd.DataFrame(chk))
    fallas = [c for c in chk if c["resultado"] == "FALLA"]
    if fallas:
        print(pd.DataFrame(fallas).to_string())
        sys.exit("ALTO: falló la validación de datos adicionales.")
    R["validacion"] = {"chk": chk, "J10": chk[[c["verificacion"].startswith("J10") for c in chk].index(True)]["detalle"]}
    return base_p, base_j, gk, de, co, ro, di


# ---------------------------------------------------------------------------
# H1 — Portero / definición rival
# ---------------------------------------------------------------------------
def h1(bt, p, gk):
    M = gk.merge(p[["jornada", "xg_rival_sin_penales", "penales_en_contra"]], on="jornada")
    M["uno"] = 1.0
    M["brecha"] = M.xg_en_contra - M.goles_recibidos
    M["definicion_rival"] = M.xg_en_contra - M.xgot_en_contra
    tabla("H1_portero_partido", M[["jornada", "goles_recibidos", "tiros_a_puerta_recibidos", "paradas", "xg_en_contra",
                                   "xgot_en_contra", "goles_evitados", "definicion_rival", "brecha", "penales_recibidos"]].round(3))

    def resumen(Mx, version):
        rows = []
        for bn, bj in BLOQUES.items():
            s = Mx[Mx.jornada.isin(bj)]
            if s.empty:
                continue
            ge, ge_lo, ge_hi, smp_ge = bt.ratio(s.goles_evitados, s.uno)
            ra, ra_lo, ra_hi, _ = bt.ratio(s.xgot_en_contra, s.xg_en_contra)
            br = s.brecha.sum()
            # participación de paradas en la brecha (solo si brecha > 0)
            ix = bt.indices(len(s)) if len(s) > 1 else None
            if ix is not None and br > 0:
                with np.errstate(divide="ignore", invalid="ignore"):
                    sh = s.goles_evitados.values[ix].sum(1) / s.brecha.values[ix].sum(1)
                sh = np.where(s.brecha.values[ix].sum(1) > 0, sh, np.nan)
                sh_lo, sh_hi = np.nanquantile(sh, 0.025), np.nanquantile(sh, 0.975)
            else:
                sh_lo = sh_hi = np.nan
            rows.append({"version": version, "bloque": bn, "partidos": len(s), "goles": s.goles_recibidos.sum(),
                         "xG_contra": s.xg_en_contra.sum(), "xGOT_contra": s.xgot_en_contra.sum(),
                         "xG_contra_pp": s.xg_en_contra.mean(), "xGOT_contra_pp": s.xgot_en_contra.mean(),
                         "goles_pp": s.goles_recibidos.mean(),
                         "goles_evitados_total": s.goles_evitados.sum(), "goles_evitados_pp": ge,
                         "GE_pp_IC95_lo": ge_lo, "GE_pp_IC95_hi": ge_hi,
                         "xGOT/xG": ra, "xGOT/xG_IC95_lo": ra_lo, "xGOT/xG_IC95_hi": ra_hi,
                         "brecha_xG_menos_goles": br, "parte_definicion_rival (xG−xGOT)": s.definicion_rival.sum(),
                         "parte_paradas (xGOT−goles)": s.goles_evitados.sum(),
                         "%_paradas_en_brecha": 100 * s.goles_evitados.sum() / br if br > 0 else np.nan,
                         "%_paradas_IC95_lo": 100 * sh_lo, "%_paradas_IC95_hi": 100 * sh_hi})
            exb = [x for x in Mx.attrs.get("excluidas", []) if x in bj]
            log_filas("H1", f"xGOT, goles evitados, xG ({version})", bn, len(s), 0, len(exb),
                      "sin N/D en estos campos" + (f"; excluidas por penal en contra: {', '.join(f'J{x}' for x in exb)}" if exb else ""))
        return rows

    Ma = M.copy()
    Ma.attrs["excluidas"] = []
    excl = M[M.penales_recibidos > 0].jornada.tolist()
    Mb = M[~M.jornada.isin(excl)].copy()
    Mb.attrs["excluidas"] = excl
    res = pd.DataFrame(resumen(Ma, "a) completa (con penales)") + resumen(Mb, f"b) sin partidos con penal en contra (excluye J{', J'.join(map(str, excl))})"))
    tabla("H1_resumen_bloques", res.round(3))

    # Tasa de paradas (excluye J6 y J15)
    sv = []
    for bn, bj in BLOQUES.items():
        s = M[M.jornada.isin(bj) & ~M.jornada.isin(INCONSISTENTES_PARADAS)]
        est, lo, hi, _ = bt.ratio(s.paradas, s.tiros_a_puerta_recibidos, 100)
        sv.append({"bloque": bn, "partidos_usados": len(s), "excluidos": ", ".join(f"J{x}" for x in INCONSISTENTES_PARADAS if x in bj),
                   "paradas": s.paradas.sum(), "tiros_a_puerta": s.tiros_a_puerta_recibidos.sum(),
                   "%_paradas": est, "IC95_lo": lo, "IC95_hi": hi})
        log_filas("H1", "tasa de paradas", bn, len(s), 0, len([x for x in INCONSISTENTES_PARADAS if x in bj]),
                  "J6 y J15 excluidas por inconsistencia conocida")
    tabla("H1_tasa_paradas", pd.DataFrame(sv).round(2))

    # Veredicto
    def veredicto(Mx, antes, despues):
        a = Mx[Mx.jornada.isin(antes)]
        d = Mx[Mx.jornada.isin(despues)]
        ge, lo, hi, _ = bt.ratio(d.goles_evitados, np.ones(len(d)))
        br = d.brecha.sum()
        sh = d.goles_evitados.sum() / br if br > 0 else np.nan
        ra_a = a.xgot_en_contra.sum() / a.xg_en_contra.sum()
        ra_d = d.xgot_en_contra.sum() / d.xg_en_contra.sum()
        if ge > 0 and lo > 0 and sh >= 0.5:
            v = "APOYADA"
        elif ge <= 0 or (sh <= 0.25 and ra_d < ra_a):
            v = "REFUTADA"
        else:
            v = "NO CONCLUYENTE"
        return {"GE_total_despues": d.goles_evitados.sum(), "GE_pp": ge, "GE_IC95_lo": lo, "GE_IC95_hi": hi,
                "brecha": br, "%_paradas": 100 * sh if not np.isnan(sh) else np.nan,
                "xGOT/xG_antes": ra_a, "xGOT/xG_despues": ra_d, "veredicto": v}

    sens = []
    for nombre, a, d in variantes():
        for ver, Mx in [("a", Ma), ("b", Mb)]:
            r = veredicto(Mx, a, d)
            r.update({"variante": nombre, "version": ver})
            sens.append(r)
    sens = tabla("H1_sensibilidad", pd.DataFrame(sens)[["variante", "version", "GE_total_despues", "GE_pp", "GE_IC95_lo",
                                                         "GE_IC95_hi", "brecha", "%_paradas", "xGOT/xG_antes",
                                                         "xGOT/xG_despues", "veredicto"]].round(3))
    principal = sens[(sens.variante.str.startswith("corte J8")) & (sens.version == "a")].iloc[0].to_dict()
    R["H1"] = {"resumen": res.round(3).to_dict("records"), "paradas": pd.DataFrame(sv).round(2).to_dict("records"),
               "principal": principal, "veredictos_variantes": sens.veredicto.value_counts().to_dict(),
               "sens": sens.round(3).to_dict("records")}

    # Gráfica
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    ra = res[res.version.str.startswith("a)")].set_index("bloque")
    orden = ["J1–J7", "J8–J13", "J14–J16", "J8–J16"]
    ax = axes[0]
    for k, (col, lab, c) in enumerate([("xG_contra_pp", "xG en contra", C_CONTRA), ("xGOT_contra_pp", "xGOT en contra", C_TER),
                                       ("goles_pp", "Goles recibidos", C_FAVOR)]):
        ys, los, his = [], [], []
        for bn in orden:
            s = M[M.jornada.isin(BLOQUES[bn])]
            colm = {"xG_contra_pp": "xg_en_contra", "xGOT_contra_pp": "xgot_en_contra", "goles_pp": "goles_recibidos"}[col]
            e, lo, hi, _ = bt.ratio(s[colm], s.uno)
            ys.append(e)
            los.append(e - lo)
            his.append(hi - e)
        xs = np.arange(4) + (k - 1) * 0.22
        ax.errorbar(xs, ys, yerr=[los, his], fmt="o", color=c, ms=7, capsize=3, lw=1.8, label=lab)
    ax.set_xticks(range(4))
    ax.set_xticklabels(orden, fontsize=9)
    ax.set_ylabel("Por partido (IC95 bootstrap)")
    ax.set_title("xG, xGOT y goles en contra")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax = axes[1]
    for i, bn in enumerate(orden):
        r = ra.loc[bn]
        ax.errorbar(i, r["xGOT/xG"], yerr=[[r["xGOT/xG"] - r["xGOT/xG_IC95_lo"]], [r["xGOT/xG_IC95_hi"] - r["xGOT/xG"]]],
                    fmt="o", color=COLB[bn], ms=8, capsize=4)
        ax.text(i + 0.1, r["xGOT/xG"], f"{r['xGOT/xG']:.2f}", fontsize=8.5, color=C_TXT2, va="center")
    ax.axhline(1, color=C_GRIS, ls="--", lw=1)
    ax.set_xticks(range(4))
    ax.set_xticklabels(orden, fontsize=9)
    ax.set_title("xGOT / xG en contra (calidad del remate rival)")
    ax = axes[2]
    rng_j = np.random.default_rng(SEED)
    for i, bn in enumerate(orden):
        s = M[M.jornada.isin(BLOQUES[bn])]
        ax.scatter(i + rng_j.uniform(-0.12, 0.12, len(s)), s.goles_evitados, color=COLB[bn], alpha=0.35, s=22)
        r = ra.loc[bn]
        ax.errorbar(i, r.goles_evitados_pp, yerr=[[r.goles_evitados_pp - r.GE_pp_IC95_lo], [r.GE_pp_IC95_hi - r.goles_evitados_pp]],
                    fmt="D", color=COLB[bn], ms=8, capsize=4)
        ax.text(i + 0.15, r.goles_evitados_pp, f"{r.goles_evitados_pp:+.2f}", fontsize=8.5, color=C_TXT2, va="center")
    ax.axhline(0, color=C_TXT2, lw=0.8)
    ax.set_xticks(range(4))
    ax.set_xticklabels(orden, fontsize=9)
    ax.set_title("Goles evitados por partido (xGOT − goles)")
    fig.suptitle("H1 — Acevedo vs definición rival (con penales; puntos = partidos, rombo = media e IC95)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "v2_H1_portero.png", dpi=150)
    plt.close(fig)
    return M


# ---------------------------------------------------------------------------
# H2 — Defensa
# ---------------------------------------------------------------------------
def shift_share(df, numc, denc, scale, jug_b1, jug_b2, min_col="minutos"):
    """Descompone el cambio de una razón de sumas (B1→B2) en 'mismos jugadores' y 'nombres/mezcla'."""
    a = df[df.jornada.isin(jug_b1)].groupby("jugador")[[numc, denc, min_col]].sum()
    b = df[df.jornada.isin(jug_b2)].groupby("jugador")[[numc, denc, min_col]].sum()
    R1 = a[numc].sum() / a[denc].sum() * scale
    R2 = b[numc].sum() / b[denc].sum() * scale
    ambos = a.index[(a[min_col] >= 90)].intersection(b.index[(b[min_col] >= 90)])
    ambos = [j for j in ambos if a.loc[j, denc] > 0 and b.loc[j, denc] > 0]
    w2 = b[denc] / b[denc].sum()
    r1 = a[numc] / a[denc] * scale
    r2 = b[numc] / b[denc] * scale
    dentro = float(sum(w2[j] * (r2[j] - r1[j]) for j in ambos))
    return R1, R2, dentro, (R2 - R1) - dentro, ambos


def h2(bt, p, de):
    dm = de[de.posicion.isin(["Defensa", "Mediocampista"])].copy()
    log_filas("H2", "universo (Defensa + Mediocampista)", "J1–J16", len(dm), 0, len(de) - len(dm),
              "excluidas por regla: filas con posicion Delantero")
    duel_ok = dm.duelos_ganados.notna() & dm.duelos_totales.notna()
    for bn, bj in BLOQUES.items():
        s = dm[dm.jornada.isin(bj)]
        log_filas("H2", "% duelos ganados", bn, int((duel_ok & dm.jornada.isin(bj)).sum()),
                  int((~duel_ok & dm.jornada.isin(bj)).sum()), 0, "filas con duelos_ganados o duelos_totales N/D excluidas")
        log_filas("H2", "aéreos, recuperaciones, intercepciones, despejes, bloqueos", bn, len(s), 0, 0, "sin N/D")
    dmd = dm[duel_ok]
    agg = dm.groupby("jornada").agg(min_dm=("minutos", "sum"), aer_g=("duelos_aereos_ganados", "sum"),
                                    aer_t=("duelos_aereos_totales", "sum"), rec=("recuperaciones", "sum"),
                                    inter=("intercepciones", "sum"), desp=("despejes", "sum"), bloq=("bloqueos_de_tiro", "sum"))
    agg = agg.join(dmd.groupby("jornada").agg(du_g=("duelos_ganados", "sum"), du_t=("duelos_totales", "sum"),
                                              filas_duelo=("jugador", "size")))
    M = p.set_index("jornada")[["xg_rival_sin_penales", "tiros_rival", "tiros_puerta_rival", "posesion_santos",
                                "local_visita"]].join(agg).reset_index()
    M["uno"] = 1.0
    M["pos_rival_10"] = (100 - M.posesion_santos) / 10
    M["vol"] = M.rec + M.inter + M.desp + M.bloq
    tabla("H2_por_partido", M.round(3))

    defs = [  # (nombre, num, den, escala, tipo)
        ("npxG en contra por partido", "xg_rival_sin_penales", "uno", 1, "resultado"),
        ("Tiros a puerta del rival por partido", "tiros_puerta_rival", "uno", 1, "resultado"),
        ("Tiros del rival por partido", "tiros_rival", "uno", 1, "contexto"),
        ("Posesión de Santos %", "posesion_santos", "uno", 1, "contexto"),
        ("% duelos ganados (DEF+MED)", "du_g", "du_t", 100, "ejecucion"),
        ("% duelos aéreos ganados (DEF+MED)", "aer_g", "aer_t", 100, "ejecucion"),
        ("Recuperaciones por 90 (por jugador)", "rec", "min_dm", 90, "volumen"),
        ("Intercepciones por 90", "inter", "min_dm", 90, "volumen"),
        ("Despejes por 90", "desp", "min_dm", 90, "volumen"),
        ("Bloqueos por 90", "bloq", "min_dm", 90, "volumen"),
        ("Acciones defensivas* por tiro rival", "vol", "tiros_rival", 1, "volumen"),
        ("Acciones defensivas* por 10 pts de posesión rival", "vol", "pos_rival_10", 1, "volumen"),
        ("Despejes + bloqueos por tiro rival", None, "tiros_rival", 1, "volumen"),
    ]
    M["desp_bloq"] = M.desp + M.bloq
    filas = []
    for nombre, n_, d_, sc, tipo in defs:
        n_ = n_ or "desp_bloq"
        for r in stat_bloques(bt, M, n_, d_, sc):
            r.update({"metrica": nombre, "tipo": tipo})
            filas.append(r)
    res = tabla("H2_bloques", pd.DataFrame(filas)[["tipo", "metrica", "bloque", "n_partidos", "valor", "IC95_lo", "IC95_hi",
                                                    "dif_vs_J1_J7", "dif_IC95_lo", "dif_IC95_hi"]].round(3))

    # Sensibilidad (dirección con cortes J7/J9 y LOO) para resultado y ejecución
    sens = []
    for nombre, n_, d_, sc, tipo in defs:
        if tipo not in ("resultado", "ejecucion"):
            continue
        for var, a, d in variantes():
            sa = M[M.jornada.isin(a)]
            sd = M[M.jornada.isin(d)]
            ea, _, _, sma = bt.ratio(sa[n_], sa[d_], sc)
            ed, _, _, smd = bt.ratio(sd[n_], sd[d_], sc)
            lo, hi = ci_diff(sma, smd)
            mejora = (ed - ea) < 0 if tipo == "resultado" else (ed - ea) > 0
            excl0 = (hi < 0) if tipo == "resultado" else (lo > 0)
            sens.append({"metrica": nombre, "tipo": tipo, "variante": var, "antes": ea, "despues": ed, "dif": ed - ea,
                         "IC95_lo": lo, "IC95_hi": hi, "mejora_puntual": mejora, "mejora_IC_excluye_0": excl0})
    sens = tabla("H2_sensibilidad", pd.DataFrame(sens).round(3))
    main = sens[sens.variante.str.startswith("corte J8")]
    res_ok = main[(main.tipo == "resultado") & main.mejora_IC_excluye_0]
    eje_ok = main[(main.tipo == "ejecucion") & main.mejora_IC_excluye_0]
    cortes79 = sens[sens.variante.str.startswith("corte J7") | sens.variante.str.startswith("corte J9")]
    dir_estable = all(cortes79[cortes79.metrica == m].mejora_puntual.all() for m in list(res_ok.metrica) + list(eje_ok.metrica)) \
        if len(res_ok) and len(eje_ok) else False
    res_mej = main[(main.tipo == "resultado")].mejora_puntual
    eje_peor = main[(main.tipo == "ejecucion")].dif < 0
    if len(res_ok) and len(eje_ok) and dir_estable:
        v = "APOYADA"
    elif (not res_mej.any()) or eje_peor.all():
        v = "REFUTADA"
    else:
        v = "NO CONCLUYENTE"

    # Shift-share
    ss = []
    dm2 = dm.copy()
    dm2["uno_min"] = dm2.minutos
    for nombre, n_, d_, sc, src in [("% duelos ganados", "duelos_ganados", "duelos_totales", 100, dmd),
                                    ("% duelos aéreos ganados", "duelos_aereos_ganados", "duelos_aereos_totales", 100, dm),
                                    ("Recuperaciones por 90", "recuperaciones", "minutos", 90, dm),
                                    ("Intercepciones por 90", "intercepciones", "minutos", 90, dm),
                                    ("Despejes por 90", "despejes", "minutos", 90, dm),
                                    ("Bloqueos por 90", "bloqueos_de_tiro", "minutos", 90, dm)]:
        src = src.copy()
        src["min_aux"] = src.minutos
        if d_ == "minutos":
            src["den_aux"] = src.minutos
            d_use = "den_aux"
        else:
            d_use = d_
        R1, R2, dentro, comp, ambos = shift_share(src, n_, d_use, sc, B1, B2, min_col="min_aux")
        ss.append({"metrica": nombre, "J1–J7": R1, "J8–J13": R2, "cambio": R2 - R1, "mismos_jugadores": dentro,
                   "nombres_y_mezcla_de_minutos": comp, "n_mismos_jugadores": len(ambos), "mismos": ", ".join(ambos)})
    ss = tabla("H2_shift_share", pd.DataFrame(ss).round(3))

    # por jugador
    pj = []
    for bn in ["J1–J7", "J8–J13"]:
        s = dm[dm.jornada.isin(BLOQUES[bn])]
        sd = dmd[dmd.jornada.isin(BLOQUES[bn])]
        g = s.groupby("jugador").agg(posicion=("posicion", lambda x: x.mode().iloc[0]), minutos=("minutos", "sum"),
                                     aer_g=("duelos_aereos_ganados", "sum"), aer_t=("duelos_aereos_totales", "sum"),
                                     rec=("recuperaciones", "sum"), inter=("intercepciones", "sum"),
                                     desp=("despejes", "sum"), bloq=("bloqueos_de_tiro", "sum"))
        gd = sd.groupby("jugador").agg(du_g=("duelos_ganados", "sum"), du_t=("duelos_totales", "sum"),
                                       filas_duelo=("jugador", "size"))
        g = g.join(gd)
        g["filas_duelo_ND"] = s.groupby("jugador").size() - g.filas_duelo.fillna(0)
        g["%duelos"] = 100 * g.du_g / g.du_t
        g["%aereos"] = 100 * g.aer_g / g.aer_t
        for c in ["rec", "inter", "desp", "bloq"]:
            g[c + "_p90"] = g[c] / g.minutos * 90
        g["bloque"] = bn
        pj.append(g.reset_index())
    pj = tabla("H2_por_jugador", pd.concat(pj).round(2))
    R["H2"] = {"bloques": res.to_dict("records"), "veredicto": v, "shift_share": ss.to_dict("records"),
               "sens_resumen": sens.groupby(["metrica", "mejora_puntual"]).size().unstack(fill_value=0).reset_index().to_dict("records"),
               "res_ok": list(res_ok.metrica), "eje_ok": list(eje_ok.metrica), "dir_estable": dir_estable}

    # Gráfica
    sel = ["npxG en contra por partido", "Tiros a puerta del rival por partido", "% duelos ganados (DEF+MED)",
           "% duelos aéreos ganados (DEF+MED)", "Despejes + bloqueos por tiro rival", "Recuperaciones por 90 (por jugador)",
           "Intercepciones por 90", "Acciones defensivas* por 10 pts de posesión rival"]
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.2))
    orden = ["J1–J7", "J8–J13", "J14–J16", "J8–J16"]
    for ax, m in zip(axes.ravel(), sel):
        sub = res[res.metrica == m].set_index("bloque").loc[orden]
        for i, (bn, r) in enumerate(sub.iterrows()):
            ax.errorbar(i, r.valor, yerr=[[r.valor - r.IC95_lo], [r.IC95_hi - r.valor]], fmt="o", color=COLB[bn], ms=7, capsize=3)
            ax.text(i + 0.12, r.valor, f"{r.valor:.2f}" if r.valor < 10 else f"{r.valor:.1f}", fontsize=7.5, color=C_TXT2, va="center")
        ax.set_xticks(range(4))
        ax.set_xticklabels(orden, fontsize=7.5)
        tipo = sub.tipo.iloc[0]
        ax.set_title(f"{m}\n[{tipo}]", fontsize=9)
    fig.suptitle("H2 — Defensa: resultado, ejecución y volumen (media e IC95 bootstrap por partidos)", fontweight="bold")
    fig.text(0.5, 0.005, "*Acciones defensivas = recuperaciones + intercepciones + despejes + bloqueos de DEF+MED. "
             "Más volumen puede indicar que se defendió más, no mejor.", ha="center", fontsize=8.5, color=C_TXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "v2_H2_defensa.png", dpi=150)
    plt.close(fig)
    return M


# ---------------------------------------------------------------------------
# H3 — Construcción de los mismos jugadores
# ---------------------------------------------------------------------------
def h3(bt, co):
    c = co[co.posicion != "Portero"].copy()
    m1 = c[c.jornada.isin(B1)].groupby("jugador").minutos.sum()
    m2 = c[c.jornada.isin(B2)].groupby("jugador").minutos.sum()
    grupo = sorted(set(m1[m1 >= 90].index) & set(m2[m2 >= 90].index))
    g = c[c.jugador.isin(grupo)]
    metr = [("Ocasiones creadas por 90", "ocasiones_creadas", 90, "principal"),
            ("Toques en área rival por 90", "toques_area_rival", 90, "principal"),
            ("% pases completados", None, 100, "secundaria"),
            ("Pases largos precisos por 90", "pases_largos_precisos", 90, "secundaria"),
            ("xA por 90 (solo filas con dato)", "xa", 90, "secundaria")]
    # tabla por partido para el grupo, por métrica (excluyendo filas N/D y sus minutos)
    Ms = {}
    for nombre, col, sc, tipo in metr:
        if col is None:
            gg = g.dropna(subset=["pases_completados", "pases_intentados"])
            M = gg.groupby("jornada").agg(num=("pases_completados", "sum"), den=("pases_intentados", "sum")).reset_index()
            excl = len(g) - len(gg)
        else:
            gg = g.dropna(subset=[col])
            M = gg.groupby("jornada").agg(num=(col, "sum"), den=("minutos", "sum")).reset_index()
            excl = len(g) - len(gg)
        Ms[nombre] = M
        for bn, bj in BLOQUES.items():
            log_filas("H3", nombre, bn, int(gg.jornada.isin(bj).sum()), int((g.jornada.isin(bj)).sum() - gg.jornada.isin(bj).sum()), 0,
                      f"grupo de {len(grupo)} jugadores con ≥90' en J1–J7 y en J8–J13; N/D excluidas con sus minutos")
    filas = []
    for nombre, col, sc, tipo in metr:
        for r in stat_bloques(bt, Ms[nombre], "num", "den", sc):
            r.update({"metrica": nombre, "tipo": tipo})
            filas.append(r)
    res = tabla("H3_bloques_grupo", pd.DataFrame(filas)[["tipo", "metrica", "bloque", "n_partidos", "valor", "IC95_lo", "IC95_hi",
                                                          "dif_vs_J1_J7", "dif_IC95_lo", "dif_IC95_hi"]].round(3))
    # xa N/D global
    xa_nd = int(co.xa.isna().sum())
    log_filas("H3", "xa (archivo completo)", "J1–J16", len(co) - xa_nd, xa_nd, 0, f"{100 * xa_nd / len(co):.1f}% N/D")
    # sensibilidad
    sens = []
    for nombre, col, sc, tipo in metr:
        M = Ms[nombre]
        for var, a, d in variantes():
            ea, _, _, sa = bt.ratio(M[M.jornada.isin(a)].num, M[M.jornada.isin(a)].den, sc)
            ed, _, _, sd = bt.ratio(M[M.jornada.isin(d)].num, M[M.jornada.isin(d)].den, sc)
            lo, hi = ci_diff(sa, sd)
            sens.append({"metrica": nombre, "tipo": tipo, "variante": var, "antes": ea, "despues": ed, "dif": ed - ea,
                         "IC95_lo": lo, "IC95_hi": hi, "sube_puntual": ed > ea, "sube_IC_excluye_0": lo > 0})
    sens = tabla("H3_sensibilidad", pd.DataFrame(sens).round(3))
    main = sens[sens.variante.str.startswith("corte J8") & (sens.tipo == "principal")]
    c79 = sens[(sens.variante.str.startswith("corte J7") | sens.variante.str.startswith("corte J9")) & (sens.tipo == "principal")]
    if main.sube_IC_excluye_0.all() and c79.sube_puntual.all():
        v = "APOYADA"
    elif not main.sube_puntual.any():
        v = "REFUTADA"
    else:
        v = "NO CONCLUYENTE"
    # por jugador
    pj = []
    for j in grupo:
        row = {"jugador": j}
        for bn in ["J1–J7", "J8–J13"]:
            s = g[(g.jugador == j) & g.jornada.isin(BLOQUES[bn])]
            row[f"min_{bn}"] = s.minutos.sum()
            for nombre, col, sc, tipo in metr:
                if col is None:
                    ss_ = s.dropna(subset=["pases_intentados"])
                    row[f"%pases_{bn}"] = 100 * ss_.pases_completados.sum() / ss_.pases_intentados.sum()
                else:
                    ss_ = s.dropna(subset=[col])
                    row[f"{col}_p90_{bn}"] = ss_[col].sum() / ss_.minutos.sum() * 90 if ss_.minutos.sum() else np.nan
                    row[f"{col}_filasND_{bn}"] = len(s) - len(ss_)
        pj.append(row)
    pj = pd.DataFrame(pj)
    for col in ["ocasiones_creadas", "toques_area_rival", "xa"]:
        pj[f"Δ_{col}_p90"] = pj[f"{col}_p90_J8–J13"] - pj[f"{col}_p90_J1–J7"]
    pj = tabla("H3_por_jugador", pj.round(3))
    R["H3"] = {"grupo": grupo, "bloques": res.to_dict("records"), "veredicto": v, "xa_nd": xa_nd,
               "sens_principal": sens[sens.tipo == "principal"].groupby("metrica").agg(
                   sube=("sube_puntual", "sum"), n=("sube_puntual", "size"), ic_excl0=("sube_IC_excluye_0", "sum")).reset_index().to_dict("records"),
               "por_jugador": pj.to_dict("records")}

    # Gráfica: agregados con IC + por jugador (dumbbell) para las principales
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.3, 1.3]})
    orden = ["J1–J7", "J8–J13", "J14–J16"]
    for ax, m in zip(axes[:2], ["Ocasiones creadas por 90", "Toques en área rival por 90"]):
        sub = res[res.metrica == m].set_index("bloque").loc[orden]
        for i, (bn, r) in enumerate(sub.iterrows()):
            ax.errorbar(i, r.valor, yerr=[[r.valor - r.IC95_lo], [r.IC95_hi - r.valor]], fmt="o", color=COLB[bn], ms=8, capsize=4)
            ax.text(i + 0.12, r.valor, f"{r.valor:.2f}", fontsize=8.5, color=C_TXT2, va="center")
        ax.set_xticks(range(3))
        ax.set_xticklabels(orden, fontsize=9)
        ax.set_title(f"{m}\n(grupo de {len(grupo)}, IC95)", fontsize=9.5)
    for ax, col, lab in [(axes[2], "ocasiones_creadas", "Ocasiones creadas /90"), (axes[3], "toques_area_rival", "Toques área rival /90")]:
        d = pj.sort_values(f"Δ_{col}_p90")
        y = np.arange(len(d))
        ax.hlines(y, d[f"{col}_p90_J1–J7"], d[f"{col}_p90_J8–J13"], color=C_GRID, lw=3)
        ax.scatter(d[f"{col}_p90_J1–J7"], y, color=C_CONTRA, s=40, label="J1–J7", zorder=3)
        ax.scatter(d[f"{col}_p90_J8–J13"], y, color=C_FAVOR, s=40, label="J8–J13", zorder=3)
        ax.set_yticks(y)
        ax.set_yticklabels(d.jugador, fontsize=8)
        ax.set_title(f"{lab} por jugador\n(rango J1–J7 → J8–J13)", fontsize=9.5)
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("H3 — Construcción de los jugadores presentes en ambos bloques", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "v2_H3_construccion.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# H4 — Formación y roles (descriptivo)
# ---------------------------------------------------------------------------
def h4(bt, p, ro):
    roles = ro.pivot(index="jugador", columns="jornada", values="posicion_en_formacion").fillna("—")
    roles.columns = [f"J{c}" for c in roles.columns]
    form = ro.groupby("jornada").formacion_inicial.first()
    roles.loc["(formación)"] = [form[int(c[1:])] for c in roles.columns]
    roles.loc["(local/visita)"] = [p.set_index("jornada").loc[int(c[1:]), "local_visita"] for c in roles.columns]
    tabla("H4_roles_por_jornada", roles.reset_index())
    nd_rol = int((ro.posicion_en_formacion == "N/D").sum())
    log_filas("H4", "posicion_en_formacion", "J1–J16", len(ro) - nd_rol, nd_rol, 0, "Villalba J4 N/D; 'central' sin lado")
    rc = ro[ro.posicion_en_formacion != "N/D"].groupby(["jugador", "formacion_inicial", "posicion_en_formacion"]).size() \
        .rename("titularidades").reset_index()
    tabla("H4_roles_por_formacion", rc)

    q = p.copy()
    q["dif"] = q.xg_santos_sin_penales - q.xg_rival_sin_penales
    q["bloque"] = np.where(q.jornada <= 7, "J1–J7", np.where(q.jornada <= 13, "J8–J13", "J14–J16"))
    rows = []
    for (f, lv), s in q.groupby(["formacion_santos", "local_visita"]):
        e, lo, hi, _ = bt.ratio(s.dif, np.ones(len(s)))
        rows.append({"formacion": f, "local_visita": lv, "partidos": len(s), "jornadas": ", ".join(f"J{x}" for x in s.jornada),
                     "npxG_favor": s.xg_santos_sin_penales.mean(), "npxG_contra": s.xg_rival_sin_penales.mean(),
                     "dif_npxG": e, "dif_min": s.dif.min(), "dif_max": s.dif.max(),
                     "IC95_lo (n≥3)": lo if len(s) >= 3 else np.nan, "IC95_hi (n≥3)": hi if len(s) >= 3 else np.nan,
                     "ppg": s.puntos.mean()})
    fl = tabla("H4_formacion_x_localia", pd.DataFrame(rows).round(3))
    fb = q.groupby(["formacion_santos", "local_visita", "bloque"]).agg(partidos=("jornada", "size"),
                                                                       jornadas=("jornada", lambda s: ", ".join(f"J{x}" for x in s)),
                                                                       dif_npxG=("dif", "mean"), ppg=("puntos", "mean")).reset_index()
    tabla("H4_formacion_localia_bloque", fb.round(3))

    # Regla pre-registrada
    viejas, nuevas = ["4-2-3-1", "5-3-2"], ["3-4-3", "5-4-1"]
    primera_nueva = int(q[q.formacion_santos.isin(nuevas)].jornada.min())
    ultima_vieja = int(q[q.formacion_santos.isin(viejas)].jornada.max())
    timing = 7 <= primera_nueva <= 9
    comp = {}
    for lv in ["L", "V"]:
        s = q[q.local_visita == lv]
        a, b = s[s.formacion_santos.isin(viejas)], s[s.formacion_santos.isin(nuevas)]
        comp[lv] = {"viejas_n": len(a), "viejas_dif": a.dif.mean(), "nuevas_n": len(b), "nuevas_dif": b.dif.mean(),
                    "nuevas_menos_viejas": b.dif.mean() - a.dif.mean()}
    mejor = [comp[lv]["nuevas_menos_viejas"] > 0 for lv in ["L", "V"]]
    if timing and all(mejor):
        v = "APOYADA (descriptiva)"
    elif not timing and not any(mejor):
        v = "REFUTADA"
    else:
        v = "NO CONCLUYENTE"
    R["H4"] = {"form_loc": fl.to_dict("records"), "form_bloque": fb.round(3).to_dict("records"), "primera_nueva": primera_nueva,
               "ultima_vieja": ultima_vieja, "timing": timing, "comp": comp, "veredicto": v, "nd_rol": nd_rol}
    # Roles clave
    clave = ["Ezequiel Bullaude", "Diego González", "Mauricio Cuevas", "Fran Villalba", "Eduardo Aguirre", "Tahiel Jiménez",
             "Esteban Lozano", "Facundo Cáseres", "Felipe Sánchez", "Franco Pardo", "Efraín Orona", "Kevin Palacios"]
    rk = ro[ro.jugador.isin(clave)].copy()
    rk["bloque"] = np.where(rk.jornada <= 7, "J1–J7", np.where(rk.jornada <= 13, "J8–J13", "J14–J16"))
    rkk = rk.groupby(["jugador", "bloque"]).posicion_en_formacion.apply(lambda s: ", ".join(f"{k}×{v}" for k, v in s.value_counts().items())) \
        .unstack().reindex(columns=["J1–J7", "J8–J13", "J14–J16"]).fillna("—")
    tabla("H4_roles_clave_por_bloque", rkk.reset_index())
    R["H4"]["roles_clave"] = rkk.reset_index().to_dict("records")

    # Gráfica: dif npxG por formación, separado por localía
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    fo = ["4-2-3-1", "5-3-2", "3-4-3", "5-4-1"]
    colf = {"J1–J7": C_CONTRA, "J8–J13": C_FAVOR, "J14–J16": C_GRIS}
    for ax, lv, tit in [(axes[0], "L", "Local"), (axes[1], "V", "Visita")]:
        s = q[q.local_visita == lv]
        for i, f in enumerate(fo):
            t = s[s.formacion_santos == f]
            if t.empty:
                ax.text(i, -2.6, "no usada", ha="center", fontsize=8, color=C_TXT2)
                continue
            for _, r in t.iterrows():
                ax.scatter(i + (hash(r.jornada) % 7 - 3) * 0.03, r.dif, color=colf[r.bloque], s=45, zorder=3)
                ax.text(i + 0.08 + (hash(r.jornada) % 7 - 3) * 0.03, r.dif, f"J{r.jornada}", fontsize=7, color=C_TXT2, va="center")
            ax.hlines(t.dif.mean(), i - 0.25, i + 0.25, color=C_TXT, lw=2)
            ax.vlines(i - 0.3, t.dif.min(), t.dif.max(), color=C_GRIS, lw=2)
        ax.axhline(0, color=C_TXT2, lw=0.8)
        ax.set_xticks(range(len(fo)))
        ax.set_xticklabels(fo)
        ax.set_title(f"{tit}")
    axes[0].set_ylabel("Diferencia de npxG por partido")
    for bn, c in colf.items():
        axes[1].scatter([], [], color=c, label=bn)
    axes[1].legend(frameon=False, fontsize=8.5, loc="lower left")
    fig.suptitle("H4 — Diferencia de npxG por formación inicial, separada por localía (línea = media; barra gris = rango)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "v2_H4_formacion_localia.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# H5 — Disponibilidad
# ---------------------------------------------------------------------------
def h5(bt, p, di, base_j):
    q = p.copy()
    q["dif"] = q.xg_santos_sin_penales - q.xg_rival_sin_penales
    tabla("H5_disponibilidad_csv", di)
    pres = []
    for j, aus in SIN_PARTICIPACION.items():
        for k in range(1, 17):
            estado = "sin participación" if k in aus else ("parcial: " + PARCIAL[j][k] if k in PARCIAL.get(j, {}) else "jugó")
            mins = base_j[(base_j.jugador == j) & (base_j.jornada == k)].minutos.sum()
            pres.append({"jugador": j, "jornada": k, "estado": estado, "minutos": mins})
    pres = tabla("H5_presencia", pd.DataFrame(pres))
    # control: tabla README coincide con minutos de la base
    incoh = pres[((pres.estado == "sin participación") & (pres.minutos > 0)) | ((pres.estado != "sin participación") & (pres.minutos == 0))]
    if len(incoh):
        sys.exit(f"ALTO: tabla del README no coincide con minutos de la base: {incoh}")
    filas, res_v = [], {}
    for j, aus in SIN_PARTICIPACION.items():
        for alcance, rango in [("J1–J13", range(1, 14)), ("J1–J16", range(1, 17)),
                               ("J1–J13 sin J13 (parcial)" if j == "Efraín Orona" else None, [x for x in range(1, 14) if x != 13])]:
            if alcance is None:
                continue
            s = q[q.jornada.isin(rango)]
            sin = s[s.jornada.isin(aus)]
            con = s[~s.jornada.isin(aus)]
            for col, lab in [("dif", "dif npxG"), ("xg_santos_sin_penales", "npxG favor"), ("xg_rival_sin_penales", "npxG contra")]:
                e1, lo1, hi1, s1 = bt.ratio(con[col], np.ones(len(con)))
                e0, lo0, hi0, s0 = bt.ratio(sin[col], np.ones(len(sin)))
                if len(sin) >= 2 and len(con) >= 2:
                    dlo, dhi = ci_diff(s1, s0)
                else:
                    dlo = dhi = np.nan
                filas.append({"jugador": j, "alcance": alcance, "medida": lab, "n_con": len(con), "con": e1, "con_IC95": f"{lo1:.2f} a {hi1:.2f}",
                              "n_sin": len(sin), "jornadas_sin": ", ".join(f"J{x}" for x in sin.jornada), "sin": e0,
                              "sin_IC95": f"{lo0:.2f} a {hi0:.2f}" if len(sin) >= 2 else "n<2",
                              "sin_menos_con": e0 - e1, "IC95_lo": dlo, "IC95_hi": dhi})
            log_filas("H5", f"con/sin {j}", alcance, len(s), 0, 0, "presencia según tabla del README")
        t = [f for f in filas if f["jugador"] == j and f["alcance"] == "J1–J13" and f["medida"] == "dif npxG"][0]
        if t["n_sin"] < 2:
            res_v[j] = "NO CONCLUYENTE (n sin el jugador en J1–J13 < 2)"
        elif t["sin_menos_con"] < 0:
            res_v[j] = "CONSISTENTE (como máximo; no concluyente)"
        else:
            res_v[j] = "NO CONSISTENTE en J1–J13"
    f = tabla("H5_con_sin", pd.DataFrame(filas).round(3))
    R["H5"] = {"tabla": f.to_dict("records"), "veredicto": res_v}

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    for ax, j in zip(axes, SIN_PARTICIPACION):
        sub = f[(f.jugador == j) & (f.medida == "dif npxG") & f.alcance.isin(["J1–J13", "J1–J16"])]
        for i, (_, r) in enumerate(sub.iterrows()):
            for k, (lab, est, ci, n, c) in enumerate([("con", r.con, r.con_IC95, r.n_con, C_FAVOR), ("sin", r.sin, r.sin_IC95, r.n_sin, C_CONTRA)]):
                x = i * 2.2 + k * 0.8
                if ci != "n<2":
                    lo, hi = map(float, ci.split(" a "))
                    ax.errorbar(x, est, yerr=[[est - lo], [hi - est]], fmt="o", color=c, ms=8, capsize=4)
                else:
                    ax.scatter(x, est, color=c, s=60, marker="x")
                ax.text(x + 0.1, est, f"{est:+.2f}\nn={n}", fontsize=7.5, color=C_TXT2, va="center")
        ax.set_xticks([0.4, 2.6])
        ax.set_xticklabels(["J1–J13", "J1–J16"])
        ax.axhline(0, color=C_TXT2, lw=0.8)
        ax.set_title(f"{j}: con (azul) vs sin (naranja)")
    axes[0].set_ylabel("Diferencia de npxG por partido (IC95; × = n<2)")
    fig.suptitle("H5 — Rendimiento con y sin Orona / Diego González (descriptivo)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "v2_H5_disponibilidad.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Descomposición del sobre-rendimiento
# ---------------------------------------------------------------------------
def pmf(lam, k=20):
    return poisson.pmf(np.arange(k + 1), lam)


def xp_ambos(lf, lc):
    M = np.outer(pmf(lf), pmf(lc))
    return 3 * np.tril(M, -1).sum() + np.trace(M)


def xp_gf_real(gf, lc):
    pc = pmf(lc)
    return 3 * pc[:gf].sum() + pc[gf] if gf <= 20 else 3.0


def xp_ga_real(lf, ga):
    pf = pmf(lf)
    return 3 * pf[ga + 1:].sum() + pf[ga]


def descomposicion(p, gk):
    M = p.merge(gk[["jornada", "xgot_en_contra"]], on="jornada")
    filas = []
    for _, r in M.iterrows():
        gf, ga = int(r.goles_santos), int(r.goles_rival)
        x0 = xp_ambos(r.xg_santos_sin_penales, r.xg_rival_sin_penales)
        x1 = xp_ambos(r.xg_santos, r.xg_rival)
        # Orden 1: ataque primero
        a2 = xp_gf_real(gf, r.xg_rival)
        a3 = xp_gf_real(gf, r.xgot_en_contra)
        # Orden 2: defensa primero
        b2 = xp_ambos(r.xg_santos, r.xgot_en_contra)
        b3 = xp_ga_real(r.xg_santos, ga)
        filas.append({"jornada": r.jornada, "puntos": r.puntos, "xPts_npxG": x0, "xPts_xG": x1,
                      "o1_GF_real_xGcontra": a2, "o1_GF_real_xGOTcontra": a3,
                      "o2_xG_favor_xGOTcontra": b2, "o2_xG_favor_GA_real": b3})
    D = tabla("D_xpts_cadena_partido", pd.DataFrame(filas).round(3))
    out = []
    for bn, bj in BLOQUES.items():
        s = D[D.jornada.isin(bj)].sum()
        pen = s.xPts_xG - s.xPts_npxG
        o1 = {"definicion_Santos": s.o1_GF_real_xGcontra - s.xPts_xG, "colocacion_rival": s.o1_GF_real_xGOTcontra - s.o1_GF_real_xGcontra,
              "paradas_Acevedo": s.puntos - s.o1_GF_real_xGOTcontra}
        o2 = {"colocacion_rival": s.o2_xG_favor_xGOTcontra - s.xPts_xG, "paradas_Acevedo": s.o2_xG_favor_GA_real - s.o2_xG_favor_xGOTcontra,
              "definicion_Santos": s.puntos - s.o2_xG_favor_GA_real}
        tot = s.puntos - s.xPts_npxG
        for comp in ["penales (xG − npxG)", "definicion_Santos", "colocacion_rival", "paradas_Acevedo"]:
            if comp.startswith("penales"):
                v1 = v2 = pen
            else:
                v1, v2 = o1[comp], o2[comp]
            out.append({"bloque": bn, "componente": comp, "orden_ataque_primero": v1, "orden_defensa_primero": v2,
                        "promedio": (v1 + v2) / 2, "min": min(v1, v2), "max": max(v1, v2),
                        "%_del_sobre_rendimiento (promedio)": 100 * (v1 + v2) / 2 / tot if tot else np.nan})
        out.append({"bloque": bn, "componente": "TOTAL puntos − xPts(npxG)", "orden_ataque_primero": tot,
                    "orden_defensa_primero": tot, "promedio": tot, "min": tot, "max": tot, "%_del_sobre_rendimiento (promedio)": 100.0})
    O = tabla("D_sobre_rendimiento", pd.DataFrame(out).round(3))
    R["descomp"] = O.to_dict("records")

    # Gráfica: componentes con rango por orden (J1–J7, J8–J13, J14–J16)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    comps = ["penales (xG − npxG)", "definicion_Santos", "colocacion_rival", "paradas_Acevedo"]
    labs = ["Penales", "Definición de Santos\n(goles vs xG)", "Colocación rival\n(xGOT vs xG)", "Paradas de Acevedo\n(goles vs xGOT)"]
    for k, bn in enumerate(["J1–J7", "J8–J13", "J14–J16"]):
        s = O[O.bloque == bn].set_index("componente")
        xs = np.arange(4) + (k - 1) * 0.25
        ys = s.loc[comps, "promedio"].values
        ax.bar(xs, ys, width=0.23, color=COLB[bn], edgecolor=C_SURF, lw=1.5, label=f"{bn} (total {s.loc['TOTAL puntos − xPts(npxG)', 'promedio']:+.1f})")
        ax.errorbar(xs, ys, yerr=[ys - s.loc[comps, "min"].values, s.loc[comps, "max"].values - ys], fmt="none", ecolor=C_TXT, capsize=3, lw=1.2)
    ax.axhline(0, color=C_TXT2, lw=0.8)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labs, fontsize=9)
    ax.set_ylabel("Puntos (reales − esperados)")
    ax.set_title("Desglose de puntos reales − xPts(npxG): promedio de los dos órdenes; barra de error = rango entre órdenes")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "v2_descomposicion_sobre_rendimiento.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    rng = np.random.default_rng(SEED)
    bt = Boot(rng)
    p, base_j, gk, de, co, ro, di = validar()
    print("Validación v2 OK.")
    h1(bt, p, gk)
    h2(bt, p, de)
    h3(bt, co)
    h4(bt, p, ro)
    h5(bt, p, di, base_j)
    descomposicion(p, gk)
    tabla("filas_usadas_ND", pd.DataFrame(FILAS))
    with pd.ExcelWriter(OUT / "tablas_v2.xlsx", engine="openpyxl") as w:
        pd.DataFrame({"hoja": list(TABLAS)}).to_excel(w, sheet_name="indice", index=False)
        for n, df in TABLAS.items():
            df.to_excel(w, sheet_name=n, index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(max(len(str(c.value or "")) for c in col) + 2, 60)
    with open(OUT / "resultados_v2.json", "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1, default=str)
    print(f"Listo: {len(TABLAS)} tablas en output/v2/tablas_v2.xlsx")


if __name__ == "__main__":
    main()
