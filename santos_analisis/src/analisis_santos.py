#!/usr/bin/env python3
"""
Santos Laguna, Apertura 2026: ¿mejora real o suerte/rival/eventos?

Ejecuta todo el análisis desde ./data y escribe en ./output:
  - tablas.xlsx (todas las tablas)
  - *.png (gráficas)
  - resultados.json (cifras clave usadas en informe.md)
  - informe.md (generado a partir de las cifras calculadas)

Uso (desde la carpeta santos_analisis):
    python3 src/analisis_santos.py

Semilla fija: SEED. N/D se trata como dato ausente, nunca como cero
(salvo donde se indica explícitamente, como sensibilidad).
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
import ruptures as rpt  # noqa: E402
from scipy.stats import poisson  # noqa: E402

SEED = 20261120
N_SIM = 200_000          # simulaciones Poisson por partido
N_BOOT = 10_000          # remuestreos bootstrap
N_PERM = 10_000          # permutaciones (solo descriptivas)
XG_PENAL = 0.79          # xG que FotMob/Opta asigna a un penal (verificado en los datos)

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT = BASE / "output"
OUT.mkdir(parents=True, exist_ok=True)

SANTOS = "Santos Laguna"
B1 = list(range(1, 8))      # J1–J7
B2 = list(range(8, 14))     # J8–J13
B3 = list(range(14, 17))    # J14–J16
B23 = list(range(8, 17))    # J8–J16
BLOQUES = {"J1–J7": B1, "J8–J13": B2, "J8–J16": B23, "J14–J16": B3}

# Paleta (dataviz skill, instancia de referencia, modo claro)
C_FAVOR = "#2a78d6"   # azul: Santos / a favor
C_CONTRA = "#eb6834"  # naranja: rival / en contra
C_TER = "#1baf7a"     # aqua: tercera serie
C_GRIS = "#8a8984"
C_TXT = "#0b0b0b"
C_TXT2 = "#52514e"
C_GRID = "#e4e3df"
C_SURF = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": C_SURF, "axes.facecolor": C_SURF, "savefig.facecolor": C_SURF,
    "axes.edgecolor": C_GRID, "axes.labelcolor": C_TXT2, "xtick.color": C_TXT2,
    "ytick.color": C_TXT2, "text.color": C_TXT, "axes.grid": True, "grid.color": C_GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "lines.linewidth": 2, "axes.axisbelow": True,
})

TABLAS: dict[str, pd.DataFrame] = {}
R: dict = {}  # cifras clave para el informe


def tabla(nombre: str, df: pd.DataFrame) -> pd.DataFrame:
    TABLAS[nombre[:31]] = df
    return df


def rnd(x, d=2):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), d)


# ---------------------------------------------------------------------------
# 0. Carga y validación
# ---------------------------------------------------------------------------
def leer(nombre: str) -> pd.DataFrame:
    # UTF-8 con BOM; todo como texto para poder contar N/D antes de convertir
    return pd.read_csv(DATA / nombre, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def a_num(df: pd.DataFrame, cols: list[str], archivo: str, problemas: list) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        s = df[c].str.strip()
        conv = pd.to_numeric(s.where(s != "N/D"), errors="coerce")
        malos = s[(s != "N/D") & (s != "") & conv.isna()]
        if len(malos):
            problemas.append(f"{archivo}.{c}: {len(malos)} valores no numéricos distintos de N/D: {malos.unique()[:5]}")
        vacios = (s == "").sum()
        if vacios:
            problemas.append(f"{archivo}.{c}: {vacios} celdas vacías")
        df[c] = conv
    return df


def minuto(m: str) -> float:
    """'45+7' -> 45.07 (ordena antes que 46); '90+6' -> 90.06."""
    m = str(m).strip()
    if "+" in m:
        b, a = m.split("+")
        return int(b) + int(a) / 100
    return float(m)


def validar():
    problemas: list[str] = []
    crudos = {n: leer(n) for n in ["partidos_santos.csv", "eventos_partido.csv", "jugadores_partido.csv",
                                   "resultados_liga.csv", "contexto_santos.csv", "linea_base.csv"]}
    # Conteo de N/D por campo
    nd = []
    for n, df in crudos.items():
        for c in df.columns:
            k = int((df[c].str.strip() == "N/D").sum())
            if k:
                nd.append({"archivo": n, "campo": c, "filas_ND": k, "filas_total": len(df)})
    tabla("0_ND_por_campo", pd.DataFrame(nd))

    filas = pd.DataFrame([{"archivo": n, "filas": len(d), "columnas": d.shape[1]} for n, d in crudos.items()])

    p = a_num(crudos["partidos_santos.csv"], [
        "jornada", "goles_santos", "goles_rival", "puntos", "posesion_santos", "tiros_santos",
        "tiros_puerta_santos", "tiros_rival", "tiros_puerta_rival", "xg_santos", "xg_rival",
        "xg_santos_sin_penales", "xg_rival_sin_penales", "grandes_ocasiones_santos",
        "grandes_ocasiones_rival", "ppda_santos", "penales_a_favor", "penales_en_contra",
        "autogoles_a_favor", "goles_primer_tiempo_santos", "goles_primer_tiempo_rival"],
        "partidos_santos", problemas)
    p["fecha"] = pd.to_datetime(p["fecha"], errors="coerce")
    p["jornada"] = p["jornada"].astype(int)
    e = crudos["eventos_partido.csv"].copy()
    e["jornada"] = e["jornada"].astype(int)
    e["min_num"] = e["minuto"].map(minuto)
    j = a_num(crudos["jugadores_partido.csv"], ["jornada", "minutos", "goles", "asistencias", "tiros", "xg", "xa",
                                                "calificacion_fotmob"], "jugadores_partido", problemas)
    j["jornada"] = j["jornada"].astype(int)
    lg = a_num(crudos["resultados_liga.csv"], ["jornada", "goles_local", "goles_visitante", "xg_local",
                                               "xg_visitante"], "resultados_liga", problemas)
    lg["fecha"] = pd.to_datetime(lg["fecha"], errors="coerce")
    lg["jornada"] = lg["jornada"].astype(int)
    ctx = crudos["contexto_santos.csv"].copy()
    ctx["fecha"] = pd.to_datetime(ctx["fecha"], errors="coerce")
    lb = a_num(crudos["linea_base.csv"], ["partidos", "puntos", "goles_favor", "goles_contra", "xg_favor",
                                          "xg_contra"], "linea_base", problemas)

    chk = []

    def ok(nombre, cond, detalle=""):
        chk.append({"verificacion": nombre, "resultado": "OK" if cond else "FALLA", "detalle": detalle})
        return cond

    # Tipos / fechas
    ok("Fechas válidas (partidos, liga, contexto)",
       p["fecha"].notna().all() and lg["fecha"].notna().all() and ctx["fecha"].notna().all())
    # Duplicados
    ok("partidos: jornada única", not p["jornada"].duplicated().any())
    ok("jugadores: (jornada, jugador) único", not j.duplicated(["jornada", "jugador"]).any(),
       f"{j.duplicated(['jornada', 'jugador']).sum()} duplicados")
    ok("eventos: filas no duplicadas", not e.duplicated().any(), f"{e.duplicated().sum()} duplicados")
    ok("liga: (jornada, local, visitante) único", not lg.duplicated(["jornada", "local", "visitante"]).any())
    ok("contexto: filas no duplicadas", not ctx.duplicated().any())
    # Jornadas
    falt = sorted(set(range(1, 17)) - set(p["jornada"]))
    ok("partidos: J1–J16 completas", not falt, f"faltan {falt}" if falt else "16 jornadas")
    por_j = lg.groupby("jornada").size()
    ok("liga: 9 partidos en cada jornada 1–16", (por_j == 9).all() and len(por_j) == 16,
       f"{len(lg)} partidos")
    equipos = pd.concat([lg["local"], lg["visitante"]])
    ok("liga: 18 equipos, 16 partidos cada uno",
       equipos.nunique() == 18 and (equipos.value_counts() == 16).all())
    ok("liga: cada equipo juega una vez por jornada",
       all(pd.concat([g["local"], g["visitante"]]).is_unique for _, g in lg.groupby("jornada")))
    # Coherencia interna de partidos
    res = np.where(p.goles_santos > p.goles_rival, "G", np.where(p.goles_santos == p.goles_rival, "E", "P"))
    ok("partidos: resultado coherente con marcador", (res == p.resultado).all())
    pts = np.select([res == "G", res == "E"], [3, 1], 0)
    ok("partidos: puntos coherentes", (pts == p.puntos).all())
    ok("partidos: xG sin penales <= xG", (p.xg_santos_sin_penales <= p.xg_santos + 1e-9).all()
       and (p.xg_rival_sin_penales <= p.xg_rival + 1e-9).all())
    d_pen_s = (p.xg_santos - p.xg_santos_sin_penales - XG_PENAL * p.penales_a_favor).abs().max()
    d_pen_r = (p.xg_rival - p.xg_rival_sin_penales - XG_PENAL * p.penales_en_contra).abs().max()
    ok("partidos: xG − npxG = 0.79 × penales (±0.02)", max(d_pen_s, d_pen_r) <= 0.021,
       f"desviación máx. {max(d_pen_s, d_pen_r):.3f}")
    # Eventos vs marcador
    gs, gr = [], []
    for jj, g in e.groupby("jornada"):
        s = ((g.equipo == SANTOS) & g.tipo_evento.isin(["gol", "penal_gol"])).sum() + \
            ((g.equipo != SANTOS) & (g.tipo_evento == "autogol")).sum()
        r = ((g.equipo != SANTOS) & g.tipo_evento.isin(["gol", "penal_gol"])).sum() + \
            ((g.equipo == SANTOS) & (g.tipo_evento == "autogol")).sum()
        gs.append((jj, s, r))
    ge = pd.DataFrame(gs, columns=["jornada", "gs_ev", "gr_ev"]).set_index("jornada")
    pm = p.set_index("jornada").join(ge).fillna({"gs_ev": 0, "gr_ev": 0})
    ok("eventos: goles coinciden con marcador final",
       ((pm.gs_ev == pm.goles_santos) & (pm.gr_ev == pm.goles_rival)).all())
    # Penales y autogoles de eventos vs columnas
    pen_s = e[(e.equipo == SANTOS) & e.tipo_evento.isin(["penal_gol", "penal_fallado"])].groupby("jornada").size()
    pen_r = e[(e.equipo != SANTOS) & e.tipo_evento.isin(["penal_gol", "penal_fallado"])].groupby("jornada").size()
    ok("eventos: penales coinciden con columnas",
       (pen_s.reindex(p.jornada, fill_value=0).values == p.penales_a_favor.values).all()
       and (pen_r.reindex(p.jornada, fill_value=0).values == p.penales_en_contra.values).all())
    # Jugadores
    tit = j[j.titular == "S"].groupby("jornada").size()
    ok("jugadores: 11 titulares por partido", (tit == 11).all() and len(tit) == 16)
    og_f = p.set_index("jornada").autogoles_a_favor
    gj = j.groupby("jornada").goles.sum()
    ok("jugadores: goles individuales + autogoles a favor = goles Santos",
       ((gj + og_f) == p.set_index("jornada").goles_santos).all())
    # Liga vs partidos de Santos
    ls = lg[(lg.local == SANTOS) | (lg.visitante == SANTOS)].copy()
    ls["gs"] = np.where(ls.local == SANTOS, ls.goles_local, ls.goles_visitante)
    ls["gr"] = np.where(ls.local == SANTOS, ls.goles_visitante, ls.goles_local)
    ls["xg_s"] = np.where(ls.local == SANTOS, ls.xg_local, ls.xg_visitante)
    ls["xg_r"] = np.where(ls.local == SANTOS, ls.xg_visitante, ls.xg_local)
    ls = ls.set_index("jornada").sort_index()
    pp = p.set_index("jornada")
    ok("liga vs partidos_santos: goles y xG idénticos",
       (ls.gs == pp.goles_santos).all() and (ls.gr == pp.goles_rival).all()
       and np.allclose(ls.xg_s, pp.xg_santos) and np.allclose(ls.xg_r, pp.xg_rival))
    ok("PPDA disponible", p.ppda_santos.notna().any(), "16/16 N/D: el PPDA queda fuera del análisis")

    # Anclas solicitadas
    a1 = pp.loc[B1]
    a2 = pp.loc[B2]
    anclas = pd.DataFrame([
        {"ancla": "Puntos J1–J7 = 1", "calculado": int(a1.puntos.sum()), "esperado": 1},
        {"ancla": "Puntos J8–J13 = 18", "calculado": int(a2.puntos.sum()), "esperado": 18},
        {"ancla": "GF J1–J7 = 4", "calculado": int(a1.goles_santos.sum()), "esperado": 4},
        {"ancla": "GC J1–J7 = 12", "calculado": int(a1.goles_rival.sum()), "esperado": 12},
        {"ancla": "GF J8–J13 = 15", "calculado": int(a2.goles_santos.sum()), "esperado": 15},
        {"ancla": "GC J8–J13 = 4", "calculado": int(a2.goles_rival.sum()), "esperado": 4},
        {"ancla": "Victorias J8–J13 = 6", "calculado": int((a2.resultado == "G").sum()), "esperado": 6},
    ])
    anclas["coincide"] = anclas.calculado == anclas.esperado
    tabla("0_anclas", anclas)
    tabla("0_verificaciones", pd.DataFrame(chk))
    tabla("0_archivos", filas)
    if problemas:
        tabla("0_problemas_tipos", pd.DataFrame({"problema": problemas}))
    if not anclas.coincide.all():
        print(anclas.to_string())
        sys.exit("ALTO: los datos ancla no coinciden. Revisar antes de continuar.")
    criticos = [c for c in chk if c["resultado"] == "FALLA" and c["verificacion"] != "PPDA disponible"]
    R["validacion"] = {"fallas": criticos, "problemas_tipos": problemas, "nd": nd}
    return p, e, j, lg, ctx, lb


# ---------------------------------------------------------------------------
# Utilidades estadísticas
# ---------------------------------------------------------------------------
def boot_ci(x: np.ndarray, rng, n=N_BOOT, alpha=0.05):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    m = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return x.mean(), np.quantile(m, alpha / 2), np.quantile(m, 1 - alpha / 2)


def boot_diff(a, b, rng, n=N_BOOT, alpha=0.05):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ma = rng.choice(a, size=(n, len(a)), replace=True).mean(axis=1)
    mb = rng.choice(b, size=(n, len(b)), replace=True).mean(axis=1)
    d = mb - ma
    return b.mean() - a.mean(), np.quantile(d, alpha / 2), np.quantile(d, 1 - alpha / 2), (d <= 0).mean()


def sim_partido(lam_f, lam_c, rng, n=N_SIM):
    gf = rng.poisson(lam_f, n)
    gc = rng.poisson(lam_c, n)
    pts = np.where(gf > gc, 3, np.where(gf == gc, 1, 0))
    return pts


def xpts_analitico(lam_f, lam_c, kmax=15):
    k = np.arange(kmax + 1)
    pf = poisson.pmf(k, lam_f)
    pc = poisson.pmf(k, lam_c)
    M = np.outer(pf, pc)
    pw = np.tril(M, -1).sum()
    pdraw = np.trace(M)
    return 3 * pw + pdraw, pw, pdraw, 1 - pw - pdraw


# ---------------------------------------------------------------------------
# 1. Punto de quiebre
# ---------------------------------------------------------------------------
def punto_quiebre(p, rng):
    x = (p.xg_santos_sin_penales - p.xg_rival_sin_penales).values
    jorn = p.jornada.values
    out = {}
    for nombre, mask in {"J1–J13": jorn <= 13, "J1–J16": jorn <= 16}.items():
        xs = x[mask]
        js = jorn[mask]
        cus = np.cumsum(xs - xs.mean())
        k_min = int(js[np.argmin(cus)])  # último partido del régimen bajo
        rango = cus.max() - cus.min()
        perm = np.array([np.ptp(np.cumsum(s - s.mean())) for s in
                         (rng.permutation(xs) for _ in range(N_PERM))])
        out[nombre] = {"cusum": cus, "jornadas": js, "ultimo_bajo": k_min,
                       "inicio_alto": k_min + 1, "rango": rango, "p_perm": (perm >= rango).mean()}
    # Tabla CUSUM
    cus_df = pd.DataFrame({"jornada": jorn, "dif_npxg": x,
                           "cusum_J1_J16": out["J1–J16"]["cusum"]})
    cus_df["cusum_J1_J13"] = np.r_[out["J1–J13"]["cusum"], [np.nan] * 3]
    tabla("1_cusum", cus_df.round(3))

    # Cortes únicos exhaustivos (media antes / después, SSE)
    filas = []
    for nombre, n in [("J1–J13", 13), ("J1–J16", 16)]:
        xs = x[:n]
        sse0 = ((xs - xs.mean()) ** 2).sum()
        for k in range(2, n - 1):  # después empieza en J(k+1); mínimo 2 partidos por lado
            a, b = xs[:k], xs[k:]
            sse = ((a - a.mean()) ** 2).sum() + ((b - b.mean()) ** 2).sum()
            filas.append({"serie": nombre, "corte_inicia_en": f"J{k + 1}", "media_antes": a.mean(),
                          "media_despues": b.mean(), "salto": b.mean() - a.mean(), "SSE": sse,
                          "reduccion_SSE_%": 100 * (1 - sse / sse0)})
    cortes = pd.DataFrame(filas)
    cortes["mejor"] = cortes.groupby("serie").SSE.transform("min") == cortes.SSE
    tabla("1_cortes_unicos", cortes.round(3))

    # Cortes alternativos J7/J8/J9 (bloque "antes" termina un partido antes)
    alt = []
    for ini in [7, 8, 9]:
        a = x[: ini - 1]
        b = x[ini - 1: 13]
        b16 = x[ini - 1: 16]
        d, lo, hi, _ = boot_diff(a, b, rng)
        alt.append({"corte": f"J1–J{ini - 1} vs J{ini}–J13", "n_antes": len(a), "n_despues": len(b),
                    "media_antes": a.mean(), "media_despues": b.mean(), "salto": d, "IC95_lo": lo,
                    "IC95_hi": hi, "media_despues_hasta_J16": b16.mean()})
    tabla("1_cortes_alternativos", pd.DataFrame(alt).round(3))

    # PELT / Binseg (ruptures), modelo l2 (cambio en la media)
    sig2 = np.var(np.diff(x)) / 2  # varianza robusta a cambios de nivel
    pelt = []
    for nombre, n in [("J1–J13", 13), ("J1–J16", 16)]:
        xs = x[:n].reshape(-1, 1)
        for etiqueta, pen in [("BIC (σ²·log n)", sig2 * np.log(n)), ("2·BIC", 2 * sig2 * np.log(n)),
                              ("AIC (2σ²)", 2 * sig2)]:
            bk = rpt.Pelt(model="l2", min_size=2, jump=1).fit(xs).predict(pen=pen)
            pelt.append({"serie": nombre, "metodo": "PELT l2", "penalizacion": etiqueta,
                         "pen": round(pen, 3), "quiebres_inician_en": ", ".join(f"J{b + 1}" for b in bk[:-1]) or "ninguno"})
        bk = rpt.Binseg(model="l2", min_size=2, jump=1).fit(xs).predict(n_bkps=1)
        pelt.append({"serie": nombre, "metodo": "Binseg l2", "penalizacion": "1 quiebre fijo", "pen": None,
                     "quiebres_inician_en": f"J{bk[0] + 1}"})
    # Señales separadas: npxG a favor y en contra
    for col, lab in [("xg_santos_sin_penales", "npxG a favor"), ("xg_rival_sin_penales", "npxG en contra")]:
        xs = p[col].values[:13].reshape(-1, 1)
        bk = rpt.Binseg(model="l2", min_size=2, jump=1).fit(xs).predict(n_bkps=1)
        pelt.append({"serie": f"{lab} J1–J13", "metodo": "Binseg l2", "penalizacion": "1 quiebre fijo",
                     "pen": None, "quiebres_inician_en": f"J{bk[0] + 1}"})
    tabla("1_pelt_binseg", pd.DataFrame(pelt))

    R["quiebre"] = {
        "cusum_ultimo_bajo_13": out["J1–J13"]["ultimo_bajo"], "cusum_ultimo_bajo_16": out["J1–J16"]["ultimo_bajo"],
        "p_perm_13": rnd(out["J1–J13"]["p_perm"], 3), "p_perm_16": rnd(out["J1–J16"]["p_perm"], 3),
        "mejor_corte_13": cortes[(cortes.serie == "J1–J13") & cortes.mejor].corte_inicia_en.iloc[0],
        "mejor_corte_16": cortes[(cortes.serie == "J1–J16") & cortes.mejor].corte_inicia_en.iloc[0],
        "pelt": pelt, "alternativos": pd.DataFrame(alt).round(3).to_dict("records"),
        "cortes_13": cortes[cortes.serie == "J1–J13"].round(3).to_dict("records"),
    }

    # --- Gráfica CUSUM
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.1]})
    ax = axes[0]
    cols = [C_FAVOR if v >= 0 else C_CONTRA for v in x]
    ax.bar(jorn, x, color=cols, width=0.6, edgecolor=C_SURF, linewidth=2)
    ax.axhline(0, color=C_TXT2, lw=0.8)
    ax.set_ylabel("npxG Santos − npxG rival")
    ax.set_title("Diferencia de xG sin penales por partido")
    for b, lab in [(7.5, "J8"), (13.5, "J14")]:
        ax.axvline(b, color=C_GRIS, ls="--", lw=1)
    ax = axes[1]
    c16 = out["J1–J16"]["cusum"]
    c13 = out["J1–J13"]["cusum"]
    ax.plot(jorn, c16, color=C_FAVOR, marker="o", ms=5, label="CUSUM J1–J16")
    ax.plot(jorn[:13], c13, color=C_TER, marker="s", ms=5, ls="-", label="CUSUM J1–J13")
    kb = out["J1–J13"]["ultimo_bajo"]
    ax.axvline(kb + 0.5, color=C_GRIS, ls="--", lw=1)
    ax.annotate(f"mínimo CUSUM: J{kb}\n(quiebre ≈ inicio J{kb + 1})", xy=(kb, c13[kb - 1]),
                xytext=(kb + 1.6, c13[kb - 1] + 0.3), fontsize=9, color=C_TXT2,
                arrowprops=dict(arrowstyle="-", color=C_GRIS))
    ax.axhline(0, color=C_TXT2, lw=0.8)
    ax.set_ylabel("Suma acumulada de desvíos")
    ax.set_xlabel("Jornada")
    ax.set_title("CUSUM de la diferencia de npxG (desvío respecto a la media de cada serie)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_xticks(jorn)
    fig.tight_layout()
    fig.savefig(OUT / "01_cusum_xg.png", dpi=150)
    plt.close(fig)
    return x


# ---------------------------------------------------------------------------
# 2. Antes vs después
# ---------------------------------------------------------------------------
METRICAS = [
    ("npxg_favor", "npxG a favor"), ("npxg_contra", "npxG en contra"), ("dif_npxg", "Diferencia npxG"),
    ("xg_santos", "xG a favor (con penales)"), ("xg_rival", "xG en contra (con penales)"),
    ("tiros_santos", "Tiros"), ("tiros_rival", "Tiros rival"),
    ("tiros_puerta_santos", "Tiros a puerta"), ("tiros_puerta_rival", "Tiros a puerta rival"),
    ("posesion_santos", "Posesión %"), ("grandes_ocasiones_santos", "Grandes ocasiones"),
    ("grandes_ocasiones_rival", "Grandes ocasiones rival"), ("npxg_por_tiro", "npxG por tiro"),
    ("ppda_santos", "PPDA"), ("goles_santos", "Goles a favor"), ("goles_rival", "Goles en contra"),
    ("puntos", "Puntos"),
]


def antes_despues(p, rng):
    p = p.copy()
    p["npxg_favor"] = p.xg_santos_sin_penales
    p["npxg_contra"] = p.xg_rival_sin_penales
    p["dif_npxg"] = p.npxg_favor - p.npxg_contra
    p["npxg_por_tiro"] = p.npxg_favor / (p.tiros_santos - p.penales_a_favor)
    filas, difs = [], []
    for col, lab in METRICAS:
        for bn, bj in BLOQUES.items():
            v = p.loc[p.jornada.isin(bj), col].values
            m, lo, hi = boot_ci(v, rng)
            filas.append({"metrica": lab, "bloque": bn, "n": int(np.sum(~np.isnan(v))), "media": m,
                          "IC95_lo": lo, "IC95_hi": hi})
        a = p.loc[p.jornada.isin(B1), col].values
        if np.isnan(a).all():
            difs.append({"metrica": lab, "comparacion": "N/D", "diferencia": np.nan})
            continue
        for bn in ["J8–J13", "J8–J16"]:
            b = p.loc[p.jornada.isin(BLOQUES[bn]), col].values
            d, lo, hi, pneg = boot_diff(a, b, rng)
            # Permutación (descriptiva; n muy pequeño)
            ab = np.r_[a, b]
            obs = b.mean() - a.mean()
            perm = []
            for _ in range(N_PERM):
                s = rng.permutation(ab)
                perm.append(s[len(a):].mean() - s[:len(a)].mean())
            pperm = (np.abs(perm) >= abs(obs) - 1e-12).mean()
            difs.append({"metrica": lab, "comparacion": f"{bn} − J1–J7", "diferencia": d, "IC95_lo": lo,
                         "IC95_hi": hi, "p_permutacion_2c (descriptivo)": pperm,
                         "prop_boot_<=0": pneg})
    t = tabla("2_bloques_medias_IC", pd.DataFrame(filas).round(3))
    td = tabla("2_diferencias_IC", pd.DataFrame(difs).round(3))
    R["bloques"] = t.to_dict("records")
    R["difs"] = td.to_dict("records")

    # Gráfica xG por jornada con media móvil
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for (lo_, hi_), lab in [((0.5, 7.5), "J1–J7"), ((7.5, 13.5), "J8–J13"), ((13.5, 16.5), "J14–J16")]:
        ax.axvspan(lo_, hi_, color=C_GRID if lab == "J8–J13" else C_SURF, alpha=0.6, lw=0)
        ax.text((lo_ + hi_) / 2, 4.55, lab, ha="center", color=C_TXT2, fontsize=9)
    ax.plot(p.jornada, p.npxg_favor, color=C_FAVOR, lw=0, marker="o", ms=7, alpha=0.55)
    ax.plot(p.jornada, p.npxg_contra, color=C_CONTRA, lw=0, marker="o", ms=7, alpha=0.55)
    mf = p.npxg_favor.rolling(3, min_periods=3).mean()
    mc = p.npxg_contra.rolling(3, min_periods=3).mean()
    ax.plot(p.jornada, mf, color=C_FAVOR, label="npxG a favor (media móvil 3)")
    ax.plot(p.jornada, mc, color=C_CONTRA, label="npxG en contra (media móvil 3)")
    ax.text(16.15, mf.iloc[-1], "a favor", color=C_TXT2, va="center", fontsize=9)
    ax.text(16.15, mc.iloc[-1], "en contra", color=C_TXT2, va="center", fontsize=9)
    ax.set_xlim(0.5, 17.3)
    ax.set_ylim(0, 4.8)
    ax.set_xticks(p.jornada)
    ax.set_xlabel("Jornada")
    ax.set_ylabel("xG sin penales")
    ax.set_title("xG sin penales a favor y en contra por jornada (puntos) y media móvil de 3 partidos")
    ax.legend(frameon=False, loc="upper left", fontsize=9, bbox_to_anchor=(0.0, 0.93))
    fig.tight_layout()
    fig.savefig(OUT / "02_xg_por_jornada.png", dpi=150)
    plt.close(fig)

    # Gráfica bootstrap (pequeños múltiplos, cada uno con su eje)
    sel = ["npxG a favor", "npxG en contra", "Diferencia npxG", "Tiros a puerta", "Posesión %", "Grandes ocasiones"]
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.6))
    orden = ["J1–J7", "J8–J13", "J8–J16", "J14–J16"]
    colb = {"J1–J7": C_CONTRA, "J8–J13": C_FAVOR, "J8–J16": C_TER, "J14–J16": C_GRIS}
    for ax, m in zip(axes.ravel(), sel):
        sub = t[t.metrica == m].set_index("bloque").loc[orden]
        for i, (bn, r) in enumerate(sub.iterrows()):
            ax.errorbar(i, r.media, yerr=[[r.media - r.IC95_lo], [r.IC95_hi - r.media]], fmt="o",
                        color=colb[bn], ms=8, capsize=4, lw=2)
            ax.text(i + 0.12, r.media, f"{r.media:.2f}", fontsize=8, color=C_TXT2, va="center")
        ax.set_xticks(range(4))
        ax.set_xticklabels(orden, fontsize=8)
        ax.set_title(m, fontsize=10)
        ax.set_xlim(-0.4, 3.6)
    fig.suptitle("Media por partido e IC95% bootstrap (percentil, 10 000 remuestreos)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "02b_bloques_bootstrap.png", dpi=150)
    plt.close(fig)
    return p


# ---------------------------------------------------------------------------
# 3. Suerte vs calidad (xPts)
# ---------------------------------------------------------------------------
def suerte(p, e, rng):
    p = p.copy()
    filas = []
    sims = {}
    for _, r in p.iterrows():
        pts_np = sim_partido(r.npxg_favor, r.npxg_contra, rng)
        pts_tot = sim_partido(r.xg_santos, r.xg_rival, rng)
        sims[r.jornada] = pts_np
        xa, pw, pd_, pl = xpts_analitico(r.npxg_favor, r.npxg_contra)
        filas.append({"jornada": r.jornada, "rival": r.rival, "marcador": f"{int(r.goles_santos)}-{int(r.goles_rival)}",
                      "puntos": r.puntos, "npxg_favor": r.npxg_favor, "npxg_contra": r.npxg_contra,
                      "xPts_npxG_sim": pts_np.mean(), "xPts_npxG_analitico": xa, "P_gana": pw, "P_empata": pd_,
                      "P_pierde": pl, "xPts_xG_total_sim": pts_tot.mean()})
    xp = pd.DataFrame(filas)
    # Goles sin penales ni autogoles vs npxG
    ev = e.copy()
    gol_s_np = ev[(ev.equipo == SANTOS) & (ev.tipo_evento == "gol")].groupby("jornada").size()
    gol_r_np = ev[(ev.equipo != SANTOS) & (ev.tipo_evento == "gol")].groupby("jornada").size()
    xp["goles_np_favor"] = gol_s_np.reindex(xp.jornada, fill_value=0).values
    xp["goles_np_contra"] = gol_r_np.reindex(xp.jornada, fill_value=0).values
    xp["GF_np_menos_npxG"] = xp.goles_np_favor - xp.npxg_favor
    xp["GC_np_menos_npxGC"] = xp.goles_np_contra - xp.npxg_contra
    xp["GF_menos_xG"] = p.goles_santos.values - p.xg_santos.values
    xp["GC_menos_xGC"] = p.goles_rival.values - p.xg_rival.values
    xp["puntos_menos_xPts"] = xp.puntos - xp.xPts_npxG_sim
    tabla("3_xpts_por_partido", xp.round(3))

    res = []
    for bn, bj in BLOQUES.items():
        s = xp[xp.jornada.isin(bj)]
        tot = np.sum([sims[k] for k in bj], axis=0)
        res.append({"bloque": bn, "partidos": len(s), "puntos": s.puntos.sum(), "xPts_npxG": s.xPts_npxG_sim.sum(),
                    "xPts_npxG_IC90_lo": np.quantile(tot, 0.05), "xPts_npxG_IC90_hi": np.quantile(tot, 0.95),
                    "P(puntos_sim >= reales)": (tot >= s.puntos.sum()).mean(),
                    "P(puntos_sim <= reales)": (tot <= s.puntos.sum()).mean(),
                    "xPts_xG_total": s.xPts_xG_total_sim.sum(), "puntos_menos_xPts": s.puntos.sum() - s.xPts_npxG_sim.sum(),
                    "GF_np": s.goles_np_favor.sum(), "npxG_favor": s.npxg_favor.sum(),
                    "GF_np_menos_npxG": s.GF_np_menos_npxG.sum(), "GC_np": s.goles_np_contra.sum(),
                    "npxG_contra": s.npxg_contra.sum(), "GC_np_menos_npxGC": s.GC_np_menos_npxGC.sum(),
                    "GF_total_menos_xG": s.GF_menos_xG.sum(), "GC_total_menos_xGC": s.GC_menos_xGC.sum()})
    rb = tabla("3_xpts_por_bloque", pd.DataFrame(res).round(3))
    R["xpts"] = rb.to_dict("records")
    R["xpts_partido"] = xp.round(3).to_dict("records")

    # Gráfica: puntos acumulados reales vs xPts con banda 90%
    paths = np.cumsum(np.vstack([sims[k][:20000] for k in sorted(sims)]), axis=0)
    lo = np.quantile(paths, 0.05, axis=1)
    hi = np.quantile(paths, 0.95, axis=1)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    jj = xp.jornada.values
    ax.fill_between(jj, lo, hi, color=C_FAVOR, alpha=0.12, lw=0, label="Banda 90% simulada (npxG)")
    ax.plot(jj, xp.xPts_npxG_sim.cumsum(), color=C_FAVOR, marker="o", ms=5, label="xPts acumulados (npxG)")
    ax.plot(jj, xp.puntos.cumsum(), color=C_CONTRA, marker="o", ms=5, label="Puntos reales acumulados")
    ax.text(16.2, xp.puntos.cumsum().iloc[-1], f"reales {int(xp.puntos.sum())}", color=C_TXT2, va="center", fontsize=9)
    ax.text(16.2, xp.xPts_npxG_sim.cumsum().iloc[-1], f"xPts {xp.xPts_npxG_sim.sum():.1f}", color=C_TXT2,
            va="center", fontsize=9)
    for b in [7.5, 13.5]:
        ax.axvline(b, color=C_GRIS, ls="--", lw=1)
    ax.set_xticks(jj)
    ax.set_xlim(0.5, 17.5)
    ax.set_xlabel("Jornada")
    ax.set_ylabel("Puntos acumulados")
    ax.set_title("Puntos reales vs puntos esperados (Poisson sobre xG sin penales)")
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "03_xpts_vs_reales.png", dpi=150)
    plt.close(fig)
    return xp, sims


# ---------------------------------------------------------------------------
# 5a. Fuerza de rival (necesaria también para la regresión a la media)
# ---------------------------------------------------------------------------
def tabla_larga(lg):
    a = pd.DataFrame({"jornada": lg.jornada, "fecha": lg.fecha, "equipo": lg.local, "rival": lg.visitante,
                      "gf": lg.goles_local, "gc": lg.goles_visitante, "xgf": lg.xg_local, "xgc": lg.xg_visitante})
    b = pd.DataFrame({"jornada": lg.jornada, "fecha": lg.fecha, "equipo": lg.visitante, "rival": lg.local,
                      "gf": lg.goles_visitante, "gc": lg.goles_local, "xgf": lg.xg_visitante, "xgc": lg.xg_local})
    L = pd.concat([a, b], ignore_index=True)
    L["pts"] = np.select([L.gf > L.gc, L.gf == L.gc], [3, 1], 0)
    L["xgd"] = L.xgf - L.xgc
    return L


def fuerza_rival(p, lg):
    L = tabla_larga(lg)
    mu = L.xgf.mean()
    filas = []
    for _, r in p.iterrows():
        o = r.rival
        om = L[(L.equipo == o) & (L.rival != SANTOS)]
        pre = om[om.fecha < r.fecha]
        filas.append({"jornada": r.jornada, "fecha": r.fecha.date(), "rival": o, "local_visita": r.local_visita,
                      "rival_PJ_previos": len(pre),
                      "rival_ppg_previo": pre.pts.mean() if len(pre) else np.nan,
                      "rival_xgd_pp_previo": pre.xgd.mean() if len(pre) else np.nan,
                      "rival_ppg_temporada_sin_Santos": om.pts.mean(),
                      "rival_xgd_pp_temporada_sin_Santos": om.xgd.mean(),
                      "rival_xgf_pp_sin_Santos": om.xgf.mean(), "rival_xgc_pp_sin_Santos": om.xgc.mean(),
                      "opp_ataque_rel": om.xgf.mean() / mu, "opp_defensa_rel": om.xgc.mean() / mu})
    fr = pd.DataFrame(filas)
    tabla("5_fuerza_rival_partido", fr.round(3))
    res = []
    for bn, bj in BLOQUES.items():
        s = fr[fr.jornada.isin(bj)]
        res.append({"bloque": bn, "rival_ppg_previo (media)": s.rival_ppg_previo.mean(),
                    "n_con_previo": int(s.rival_ppg_previo.notna().sum()),
                    "rival_xgd_pp_previo (media)": s.rival_xgd_pp_previo.mean(),
                    "rival_ppg_temporada_sin_Santos": s.rival_ppg_temporada_sin_Santos.mean(),
                    "rival_xgd_pp_temporada_sin_Santos": s.rival_xgd_pp_temporada_sin_Santos.mean(),
                    "local_%": 100 * (s.local_visita == "L").mean()})
    rb = tabla("5_fuerza_rival_bloque", pd.DataFrame(res).round(3))
    R["rival"] = rb.to_dict("records")
    R["mu_liga_xg"] = rnd(mu, 3)

    # Tabla general (contexto)
    tg = L.groupby("equipo").agg(PJ=("pts", "size"), pts=("pts", "sum"), gf=("gf", "sum"), gc=("gc", "sum"),
                                 xgf=("xgf", "sum"), xgc=("xgc", "sum")).sort_values("pts", ascending=False)
    tg["xgd_pp"] = (tg.xgf - tg.xgc) / tg.PJ
    tabla("5_tabla_liga_J1_J16", tg.reset_index().round(3))

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    cols = [C_CONTRA if jj <= 7 else (C_FAVOR if jj <= 13 else C_GRIS) for jj in fr.jornada]
    ax.bar(fr.jornada, fr.rival_ppg_temporada_sin_Santos, color=cols, width=0.6, edgecolor=C_SURF, lw=2)
    ax.plot(fr.jornada, fr.rival_ppg_previo, color=C_TXT2, lw=0, marker="D", ms=6,
            label="ppg del rival antes del partido")
    for bn, xx, c in [("J1–J7", 4, C_CONTRA), ("J8–J13", 10.5, C_FAVOR), ("J14–J16", 15, C_GRIS)]:
        m = rb.set_index("bloque").loc[bn, "rival_ppg_temporada_sin_Santos"]
        ax.text(xx, 2.55, f"{bn}: {m:.2f} ppg", ha="center", fontsize=9, color=C_TXT2)
    ax.set_ylim(0, 2.75)
    ax.set_xticks(fr.jornada)
    ax.set_xticklabels([f"J{k}\n{n.replace('Atlético de San Luis', 'San Luis').replace('Querétaro FC', 'Querétaro').replace('CF América', 'América')}"
                        for k, n in zip(fr.jornada, fr.rival)], rotation=60, fontsize=8)
    ax.set_xlabel("Jornada")
    ax.set_ylabel("Puntos por partido del rival")
    ax.set_title("Fuerza del rival: ppg J1–J16 sin el partido vs Santos (barras) y ppg previo (rombos)")
    ax.legend(frameon=False, loc="upper right", fontsize=9, bbox_to_anchor=(1, 0.93))
    fig.tight_layout()
    fig.savefig(OUT / "05_fuerza_rival.png", dpi=150)
    plt.close(fig)
    return fr, L, mu


# ---------------------------------------------------------------------------
# 4. Regresión a la media
# ---------------------------------------------------------------------------
def regresion_media(p, fr, L, mu, lb, xp, rng):
    pj = p.set_index("jornada")
    f = fr.set_index("jornada")
    # Fuerza de Santos ajustada por rival (multiplicativa)
    # Unidades relativas: 1 = producción de un equipo medio contra un rival medio
    att = pj.npxg_favor / (f.opp_defensa_rel * mu)
    dfn = pj.npxg_contra / (f.opp_ataque_rel * mu)
    ajust = pd.DataFrame({"jornada": pj.index, "npxg_favor": pj.npxg_favor, "opp_defensa_rel": f.opp_defensa_rel,
                          "npxg_favor_ajustado": att * mu, "npxg_contra": pj.npxg_contra,
                          "opp_ataque_rel": f.opp_ataque_rel, "npxg_contra_ajustado": dfn * mu})
    ajust["dif_ajustada"] = ajust.npxg_favor_ajustado - ajust.npxg_contra_ajustado
    tabla("4_npxg_ajustado_rival", ajust.round(3).reset_index(drop=True))
    att1, def1 = att.loc[B1].mean(), dfn.loc[B1].mean()

    # Confiabilidad del xG a 7 partidos en la liga (varianza verdadera vs ruido)
    rel = {}
    for col in ["xgf", "xgc", "xgd"]:
        g = L.groupby("equipo")[col]
        s2w = g.var(ddof=1).mean()
        vb = g.mean().var(ddof=1)
        n_i = g.size().mean()
        vt = max(vb - s2w / n_i, 0)
        rel[col] = {"var_ruido_partido": s2w, "var_entre_equipos": vb, "var_verdadera": vt,
                    "peso_7_partidos": vt / (vt + s2w / 7) if vt > 0 else 0.0,
                    "peso_6_partidos": vt / (vt + s2w / 6) if vt > 0 else 0.0}
    tabla("4_confiabilidad_xg_liga", pd.DataFrame(rel).T.reset_index().rename(columns={"index": "medida"}).round(4))

    # Prior: línea base histórica (FotMob, xG total, a 1 decimal)
    lbp = lb.set_index("torneo")
    base_xgf = lbp.xg_favor.sum() / lbp.partidos.sum()
    base_xgc = lbp.xg_contra.sum() / lbp.partidos.sum()
    base_ppg = lbp.puntos.sum() / lbp.partidos.sum()
    w_f, w_c = rel["xgf"]["peso_7_partidos"], rel["xgc"]["peso_7_partidos"]
    att_s = base_xgf / mu + w_f * (att1 - base_xgf / mu)
    def_s = base_xgc / mu + w_c * (def1 - base_xgc / mu)

    def esperar(lf, lc):
        return sum(xpts_analitico(a, b)[0] for a, b in zip(lf, lc))

    r_b2 = pj.loc[B2]
    f2 = f.loc[B2]
    m1f, m1c = pj.loc[B1].npxg_favor.mean(), pj.loc[B1].npxg_contra.mean()
    escen = []
    escen.append({"escenario": "A. Ritmo real J1–J7 (1 pt/7) llevado a 6 partidos", "puntos_J8_J13": 6 / 7,
                  "detalle": "Puntos reales J1–J7 × 6/7"})
    escen.append({"escenario": "B. xPts de J1–J7 llevado a 6 partidos (sin suerte, mismos rivales fuertes)",
                  "puntos_J8_J13": xp[xp.jornada.isin(B1)].xPts_npxG_sim.sum() * 6 / 7,
                  "detalle": "xPts npxG J1–J7 × 6/7"})
    escen.append({"escenario": "C. npxG medio de J1–J7 vs rivales J8–J13 (sin ajuste por rival)",
                  "puntos_J8_J13": esperar([m1f] * 6, [m1c] * 6),
                  "detalle": f"λ favor {m1f:.2f}, λ contra {m1c:.2f}"})
    escen.append({"escenario": "D. Fuerza J1–J7 ajustada por rival, aplicada a rivales J8–J13",
                  "puntos_J8_J13": esperar(att1 * f2.opp_defensa_rel * mu, def1 * f2.opp_ataque_rel * mu),
                  "detalle": f"ataque rel {att1 * 1:.2f}, defensa rel {def1:.2f} (1 = media liga)"})
    escen.append({"escenario": "E. Como D, con regresión a la media hacia la línea base histórica",
                  "puntos_J8_J13": esperar(att_s * f2.opp_defensa_rel * mu, def_s * f2.opp_ataque_rel * mu),
                  "detalle": f"pesos de confiabilidad 7 PJ: favor {w_f:.2f}, contra {w_c:.2f}; "
                             f"prior xGF {base_xgf:.2f}, xGC {base_xgc:.2f}"})
    escen.append({"escenario": "F. Línea base histórica pura (ppg Clausura 26 + Apertura 25) × 6",
                  "puntos_J8_J13": base_ppg * 6, "detalle": f"{base_ppg:.3f} ppg"})
    escen.append({"escenario": "G. xPts con el npxG real de J8–J13", "puntos_J8_J13":
                  xp[xp.jornada.isin(B2)].xPts_npxG_sim.sum(), "detalle": "Poisson por partido"})
    escen.append({"escenario": "H. Puntos reales J8–J13", "puntos_J8_J13": 18.0, "detalle": ""})

    # Persistencia de puntos y xG en la liga: J1–J7 -> J8–J13 (18 equipos)
    per = L.assign(bl=np.where(L.jornada <= 7, "a", np.where(L.jornada <= 13, "b", "c")))
    agg = per[per.bl != "c"].groupby(["equipo", "bl"]).agg(ppg=("pts", "mean"), xgd=("xgd", "mean")).unstack()
    x_ppg, y_ppg = agg[("ppg", "a")], agg[("ppg", "b")]
    x_xgd = agg[("xgd", "a")]
    otros = agg.index != SANTOS
    b1, a1 = np.polyfit(x_ppg[otros], y_ppg[otros], 1)
    b2, a2 = np.polyfit(x_xgd[otros], y_ppg[otros], 1)
    r_ppg = np.corrcoef(x_ppg[otros], y_ppg[otros])[0, 1]
    r_xgd = np.corrcoef(x_xgd[otros], y_ppg[otros])[0, 1]
    pred1 = (a1 + b1 * x_ppg[SANTOS]) * 6
    pred2 = (a2 + b2 * x_xgd[SANTOS]) * 6
    escen.insert(6, {"escenario": "I. Regresión liga (17 rivales): ppg J8–J13 ~ ppg J1–J7",
                     "puntos_J8_J13": pred1, "detalle": f"pendiente {b1:.2f}, r={r_ppg:.2f}"})
    escen.insert(7, {"escenario": "J. Regresión liga (17 rivales): ppg J8–J13 ~ xGD/PJ J1–J7",
                     "puntos_J8_J13": pred2, "detalle": f"pendiente {b2:.2f}, r={r_xgd:.2f}; xG total"})
    es = tabla("4_escenarios_regresion", pd.DataFrame(escen).round(2))
    tabla("4_persistencia_liga", agg.reset_index().set_axis(
        ["equipo", "ppg_J1_J7", "ppg_J8_J13", "xgd_J1_J7", "xgd_J8_J13"], axis=1).round(3))

    R["regresion"] = {"escenarios": es.to_dict("records"), "w_f": rnd(w_f, 3), "w_c": rnd(w_c, 3),
                      "att1": rnd(att1, 3), "def1": rnd(def1, 3), "att_s": rnd(att_s, 3), "def_s": rnd(def_s, 3),
                      "base_xgf": rnd(base_xgf, 3), "base_xgc": rnd(base_xgc, 3), "base_ppg": rnd(base_ppg, 3),
                      "r_ppg": rnd(r_ppg, 3), "r_xgd": rnd(r_xgd, 3), "b_ppg": rnd(b1, 3),
                      "ajuste_bloque": {bn: {"fav": rnd(ajust[ajust.jornada.isin(bj)].npxg_favor_ajustado.mean()),
                                             "con": rnd(ajust[ajust.jornada.isin(bj)].npxg_contra_ajustado.mean()),
                                             "dif": rnd(ajust[ajust.jornada.isin(bj)].dif_ajustada.mean())}
                                        for bn, bj in BLOQUES.items()}}
    return es, ajust, att1, def1, f


# ---------------------------------------------------------------------------
# 5b. Eventos: expulsiones, penales, autogoles
# ---------------------------------------------------------------------------
def eventos(p, e, xp):
    filas = []
    for _, r in p.iterrows():
        g = e[e.jornada == r.jornada]
        rojas_r = g[(g.equipo != SANTOS) & g.tipo_evento.isin(["roja", "amarilla_segunda"])]
        primera_roja = rojas_r.min_num.min() if len(rojas_r) else np.nan

        def goles(con_pen_og: bool, hasta=np.inf):
            gg = g[g.min_num < hasta]
            tipos = ["gol", "penal_gol"] if con_pen_og else ["gol"]
            s = ((gg.equipo == SANTOS) & gg.tipo_evento.isin(tipos)).sum()
            rr = ((gg.equipo != SANTOS) & gg.tipo_evento.isin(tipos)).sum()
            if con_pen_og:  # autogol: 'equipo' es el del jugador que lo cometió
                s += ((gg.equipo != SANTOS) & (gg.tipo_evento == "autogol")).sum()
                rr += ((gg.equipo == SANTOS) & (gg.tipo_evento == "autogol")).sum()
            return int(s), int(rr)

        gs, gr = goles(True)
        s1, r1 = goles(False)
        s2, r2 = goles(False, hasta=primera_roja if not np.isnan(primera_roja) else np.inf)
        pts = lambda a, b: 3 if a > b else (1 if a == b else 0)  # noqa: E731
        filas.append({
            "jornada": r.jornada, "rival": r.rival, "marcador_real": f"{gs}-{gr}", "puntos_reales": pts(gs, gr),
            "expulsion_rival_min": r.expulsion_rival, "penales_favor": int(r.penales_a_favor),
            "penales_contra": int(r.penales_en_contra), "autogoles_favor": int(r.autogoles_a_favor),
            "marcador_sin_penales_ni_autogoles": f"{s1}-{r1}", "puntos_sin_pen_og": pts(s1, r1),
            "marcador_hasta_1a_roja_rival_sin_pen_og": f"{s2}-{r2}" if not np.isnan(primera_roja) else f"{s1}-{r1}",
            "puntos_sin_pen_og_ni_post_roja": pts(s2, r2),
            "xPts_npxG": xp.set_index("jornada").loc[r.jornada, "xPts_npxG_sim"],
            "con_evento": bool(r.penales_a_favor or r.penales_en_contra or r.autogoles_a_favor or not np.isnan(primera_roja)),
        })
    ev = pd.DataFrame(filas)
    tabla("5_eventos_por_partido", ev.round(3))
    res = []
    for bn, bj in BLOQUES.items():
        s = ev[ev.jornada.isin(bj)]
        sin = s[~s.con_evento]
        res.append({"bloque": bn, "puntos_reales": s.puntos_reales.sum(), "puntos_sin_penales_ni_autogoles":
                    s.puntos_sin_pen_og.sum(), "puntos_sin_pen_og_ni_goles_tras_roja": s.puntos_sin_pen_og_ni_post_roja.sum(),
                    "xPts_npxG": s.xPts_npxG.sum(), "partidos_con_evento": int(s.con_evento.sum()),
                    "partidos_sin_evento": len(sin), "puntos_en_partidos_sin_evento": sin.puntos_reales.sum(),
                    "xPts_en_partidos_sin_evento": sin.xPts_npxG.sum()})
    eb = tabla("5_eventos_por_bloque", pd.DataFrame(res).round(2))
    R["eventos"] = {"partido": ev.round(3).to_dict("records"), "bloque": eb.to_dict("records")}

    # Gráfica escenarios de puntos J8–J13
    s = eb.set_index("bloque").loc["J8–J13"]
    vals = [s.puntos_reales, s.puntos_sin_penales_ni_autogoles, s.puntos_sin_pen_og_ni_goles_tras_roja, s.xPts_npxG]
    labs = ["Reales", "Sin goles de penal\nni autogoles", "Además, sin goles\ntras roja rival", "xPts\n(npxG, Poisson)"]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bars = ax.bar(range(4), vals, color=[C_CONTRA, C_FAVOR, C_FAVOR, C_TER], width=0.55, edgecolor=C_SURF, lw=2)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}", ha="center", color=C_TXT, fontsize=10)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labs, fontsize=9)
    ax.set_ylabel("Puntos en J8–J13 (máx. 18)")
    ax.set_ylim(0, 20)
    ax.set_title("J8–J13: la racha rehecha sin el efecto de eventos")
    fig.tight_layout()
    fig.savefig(OUT / "05b_racha_sin_eventos.png", dpi=150)
    plt.close(fig)
    return ev


# ---------------------------------------------------------------------------
# 6. Jugadores
# ---------------------------------------------------------------------------
def jugadores(p, e, j):
    j = j.copy()
    pen = e[(e.equipo == SANTOS) & e.tipo_evento.isin(["penal_gol", "penal_fallado"])] \
        .groupby(["jornada", "jugador"]).size().rename("pen_intentos")
    j = j.merge(pen, left_on=["jornada", "jugador"], right_index=True, how="left").fillna({"pen_intentos": 0})
    j["npxg"] = j.xg - XG_PENAL * j.pen_intentos
    j.loc[j.npxg < 0, "npxg"] = 0.0  # redondeo
    j["titular_b"] = (j.titular == "S").astype(int)
    pens_sin_xg = j[(j.pen_intentos > 0) & j.xg.isna()]
    # Cobertura: suma de npxG individual registrado vs npxG del equipo
    cov = j.groupby("jornada").agg(npxg_jugadores=("npxg", "sum"), filas_xg_ND=("xg", lambda s: s.isna().sum()))
    cov["npxg_equipo"] = p.set_index("jornada").xg_santos_sin_penales
    cov["no_atribuido"] = cov.npxg_equipo - cov.npxg_jugadores
    tabla("6_cobertura_xg_jugadores", cov.reset_index().round(3))

    def bloque(df, bj):
        s = df[df.jornada.isin(bj)]
        g = s.groupby("jugador").agg(posicion=("posicion", lambda x: x.mode().iloc[0]), PJ=("jornada", "size"),
                                     titular=("titular_b", "sum"), minutos=("minutos", "sum"), goles=("goles", "sum"),
                                     asist=("asistencias", "sum"), npxg=("npxg", "sum"),
                                     xa=("xa", "sum"), filas_xg_ND=("xg", lambda x: int(x.isna().sum())),
                                     calif_media=("calificacion_fotmob", "mean"))
        g["npxg_p90"] = g.npxg / g.minutos * 90
        g["xa_p90"] = g.xa / g.minutos * 90
        g["npxg_por_partido_equipo"] = g.npxg / len(bj)
        g["cuota_minutos_%"] = 100 * g.minutos / (90 * len(bj))
        return g

    g1, g2, g3 = bloque(j, B1), bloque(j, B2), bloque(j, B3)
    comp = g1.add_suffix("_J1_J7").join(g2.add_suffix("_J8_J13"), how="outer").join(
        g3[["minutos", "titular", "npxg", "goles"]].add_suffix("_J14_J16"), how="outer")
    comp["posicion"] = comp.posicion_J8_J13.fillna(comp.posicion_J1_J7).fillna("—")
    for c in ["minutos", "titular", "npxg", "goles", "PJ", "xa"]:
        for sfx in ["_J1_J7", "_J8_J13"]:
            comp[c + sfx] = comp[c + sfx].fillna(0)
    comp["delta_npxg_por_partido_equipo"] = comp.npxg_J8_J13 / 6 - comp.npxg_J1_J7 / 7
    comp["delta_xa_por_partido_equipo"] = comp.xa_J8_J13 / 6 - comp.xa_J1_J7 / 7
    comp["delta_minutos_por_partido"] = comp.minutos_J8_J13 / 6 - comp.minutos_J1_J7 / 7

    # Tipo de cambio: composición (entra/sale del once) vs mismo jugador
    def tipo(r):
        a, b = r.minutos_J1_J7, r.minutos_J8_J13
        if a < 90 and b >= 90:
            return "entra (nuevo o sin minutos en J1–J7)"
        if a >= 90 and b < 90:
            return "sale (sin minutos relevantes en J8–J13)"
        if a < 90 and b < 90:
            return "marginal en ambos"
        return "continúa"
    comp["tipo_cambio"] = comp.apply(tipo, axis=1)
    # Para los que continúan: efecto minutos vs efecto producción por 90
    s1 = comp.minutos_J1_J7 / (90 * 7)
    s2 = comp.minutos_J8_J13 / (90 * 6)
    r1 = (comp.npxg_J1_J7 / comp.minutos_J1_J7 * 90).replace([np.inf], np.nan).fillna(0)
    r2 = (comp.npxg_J8_J13 / comp.minutos_J8_J13 * 90).replace([np.inf], np.nan).fillna(0)
    comp["efecto_minutos"] = np.where(comp.tipo_cambio == "continúa", (s2 - s1) * r1, np.nan)
    comp["efecto_produccion_p90"] = np.where(comp.tipo_cambio == "continúa", s2 * (r2 - r1), np.nan)
    comp = comp.drop(columns=[c for c in comp.columns if c.startswith("posicion_")])
    comp = comp.sort_values("delta_npxg_por_partido_equipo", ascending=False)
    tabla("6_jugadores_comparacion", comp.reset_index().round(3))

    team_delta = p[p.jornada.isin(B2)].xg_santos_sin_penales.mean() - p[p.jornada.isin(B1)].xg_santos_sin_penales.mean()
    noat1 = cov.loc[B1, "no_atribuido"].mean()
    noat2 = cov.loc[B2, "no_atribuido"].mean()
    dec = comp.groupby("tipo_cambio").delta_npxg_por_partido_equipo.sum()
    dec_tab = pd.DataFrame({"componente": list(dec.index) + ["no atribuido (N/D en ficha de jugador)", "TOTAL = Δ npxG equipo"],
                            "delta_npxg_por_partido": list(dec.values) + [noat2 - noat1, team_delta]})
    cont = comp[comp.tipo_cambio == "continúa"]
    dec_tab = pd.concat([dec_tab, pd.DataFrame([
        {"componente": "  de 'continúa': efecto más/menos minutos", "delta_npxg_por_partido": cont.efecto_minutos.sum()},
        {"componente": "  de 'continúa': efecto producción por 90", "delta_npxg_por_partido": cont.efecto_produccion_p90.sum()}])])
    dec_tab["%_del_total"] = 100 * dec_tab.delta_npxg_por_partido / team_delta
    tabla("6_descomposicion_once", dec_tab.round(3))

    # Estabilidad del once y línea defensiva
    xi = {k: set(v.jugador) for k, v in j[j.titular == "S"].groupby("jornada")}
    est = []
    for k in range(1, 17):
        est.append({"jornada": k, "formacion": p.set_index("jornada").loc[k, "formacion_santos"],
                    "cambios_vs_once_anterior": len(xi[k] - xi[k - 1]) if k > 1 else np.nan,
                    "defensas_titulares": ", ".join(sorted(j[(j.jornada == k) & (j.titular == "S") &
                                                             (j.posicion == "Defensa")].jugador)),
                    "n_defensas_titulares": int(((j.jornada == k) & (j.titular == "S") & (j.posicion == "Defensa")).sum())})
    est = tabla("6_estabilidad_once", pd.DataFrame(est))

    # Foco: jugadores solicitados + línea defensiva
    foco_n = ["Tahiel Jiménez", "Eduardo Aguirre", "Fran Villalba", "Ezequiel Bullaude", "Carlos Acevedo",
              "Esteban Lozano", "Facundo Cáseres", "Mauricio Cuevas", "Felipe Sánchez", "Franco Pardo",
              "Efraín Orona", "Emmanuel Echeverría", "Jonathan Pérez", "Javier Abella", "Carlos Gruezo",
              "Lucas Di Yorio", "Diego González", "Kevin Palacios"]
    cols = ["posicion", "PJ_J1_J7", "titular_J1_J7", "minutos_J1_J7", "goles_J1_J7", "npxg_J1_J7", "npxg_p90_J1_J7",
            "PJ_J8_J13", "titular_J8_J13", "minutos_J8_J13", "goles_J8_J13", "npxg_J8_J13", "npxg_p90_J8_J13",
            "calif_media_J1_J7", "calif_media_J8_J13", "delta_npxg_por_partido_equipo", "tipo_cambio"]
    foco = comp.loc[[n for n in foco_n if n in comp.index], cols]
    tabla("6_jugadores_foco", foco.reset_index().round(3))

    # Acevedo: goles recibidos vs xG en contra
    pr = p.set_index("jornada")
    acev = []
    for bn, bj in BLOQUES.items():
        s = pr.loc[bj]
        acev.append({"bloque": bn, "goles_recibidos": s.goles_rival.sum(), "xG_en_contra_con_pen": s.xg_rival.sum(),
                     "xG_menos_goles (proxy de paradas, no es xGOT)": s.xg_rival.sum() - s.goles_rival.sum(),
                     "tiros_puerta_rival_pp": s.tiros_puerta_rival.mean(),
                     "calif_media_Acevedo": j[(j.jugador == "Carlos Acevedo") & j.jornada.isin(bj)].calificacion_fotmob.mean()})
    tabla("6_acevedo", pd.DataFrame(acev).round(3))

    R["jugadores"] = {"team_delta": rnd(team_delta, 3), "descomp": dec_tab.round(3).to_dict("records"),
                      "foco": foco.reset_index().round(2).to_dict("records"),
                      "acevedo": pd.DataFrame(acev).round(2).to_dict("records"),
                      "cambios_once_B1": rnd(est[est.jornada.isin(B1)].cambios_vs_once_anterior.mean(), 2),
                      "cambios_once_B2": rnd(est[est.jornada.isin(B2)].cambios_vs_once_anterior.mean(), 2),
                      "pens_sin_xg": len(pens_sin_xg), "cobertura": cov.round(3).reset_index().to_dict("records")}

    # Gráfica contribución por jugador
    top = comp[comp.delta_npxg_por_partido_equipo.abs() >= 0.02].delta_npxg_por_partido_equipo.sort_values()
    top = pd.concat([top, pd.Series({"(no atribuido: N/D)": noat2 - noat1})]).sort_values()
    fig, ax = plt.subplots(figsize=(8.5, 0.34 * len(top) + 1.6))
    cols_b = [C_GRIS if n.startswith("(") else (C_FAVOR if v >= 0 else C_CONTRA) for n, v in top.items()]
    ax.barh(range(len(top)), top.values, color=cols_b, height=0.62, edgecolor=C_SURF, lw=2)
    for i, (n, v) in enumerate(top.items()):
        tc = comp.tipo_cambio.get(n, "")
        mark = " *" if str(tc).startswith("entra") else (" †" if str(tc).startswith("sale") else "")
        ax.text(v + (0.01 if v >= 0 else -0.01), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right",
                fontsize=8.5, color=C_TXT2)
        top.rename(index={n: n + mark}, inplace=False)
    ax.set_yticks(range(len(top)))
    lbl = []
    for n in top.index:
        tc = str(comp.tipo_cambio.get(n, ""))
        lbl.append(n + (" *" if tc.startswith("entra") else (" †" if tc.startswith("sale") else "")))
    ax.set_yticklabels(lbl, fontsize=9)
    ax.axvline(0, color=C_TXT2, lw=0.8)
    ax.set_xlabel("Δ npxG aportado por partido del equipo (J8–J13 − J1–J7)")
    ax.set_title(f"Contribución por jugador al cambio de npxG a favor (Δ equipo = {team_delta:+.2f}/partido)")
    ax.text(0.99, 0.02, "* entra al once   † sale del once", transform=ax.transAxes, ha="right", fontsize=8.5,
            color=C_TXT2)
    xmax = max(abs(top.min()), abs(top.max())) * 1.3
    ax.set_xlim(-xmax, xmax)
    fig.tight_layout()
    fig.savefig(OUT / "06_contribucion_jugadores.png", dpi=150)
    plt.close(fig)
    return comp, est


# ---------------------------------------------------------------------------
# 7. Contexto cualitativo
# ---------------------------------------------------------------------------
def contexto(p, ctx):
    fechas = p[["jornada", "fecha"]].sort_values("fecha")
    ini_quiebre, fin_quiebre = p.set_index("jornada").fecha.loc[7], p.set_index("jornada").fecha.loc[9]

    def jornada_de(f):
        prev = fechas[fechas.fecha <= f]
        if prev.empty:
            return "pretemporada"
        k = int(prev.jornada.iloc[-1])
        return f"J{k}" if prev.fecha.iloc[-1] == f else f"tras J{k}"

    c = ctx.copy().sort_values("fecha")
    c["momento"] = c.fecha.map(jornada_de)
    c["ventana_quiebre_J7_J9"] = (c.fecha >= ini_quiebre - pd.Timedelta(days=6)) & (c.fecha <= fin_quiebre)
    c["fecha"] = c.fecha.dt.date
    c = c[["fecha", "momento", "tipo", "jugador_o_persona", "descripcion", "ventana_quiebre_J7_J9", "fuente_url"]]
    tabla("7_contexto_linea_tiempo", c)
    # Formación vs rendimiento
    q = p.copy()
    q["dif"] = q.xg_santos_sin_penales - q.xg_rival_sin_penales
    form = q.groupby("formacion_santos").agg(partidos=("jornada", "size"), jornadas=("jornada", lambda s: ", ".join(f"J{x}" for x in s)),
                                             npxg_favor=("xg_santos_sin_penales", "mean"),
                                             npxg_contra=("xg_rival_sin_penales", "mean"), dif=("dif", "mean"),
                                             ppg=("puntos", "mean"), local_pct=("local_visita", lambda s: 100 * (s == "L").mean()))
    tabla("7_formacion_rendimiento", form.reset_index().round(3))
    # Formación por localía dentro de J8–J16
    loc = q[q.jornada >= 8].groupby(["formacion_santos", "local_visita"]).size().unstack(fill_value=0)
    tabla("7_formacion_x_localia_J8_J16", loc.reset_index())
    R["contexto"] = {"ventana": c[c.ventana_quiebre_J7_J9].drop(columns="fuente_url").astype(str).to_dict("records"),
                     "formacion": form.reset_index().round(2).to_dict("records"),
                     "form_loc": loc.reset_index().to_dict("records")}
    return c


# ---------------------------------------------------------------------------
# Descomposición final y gráfica waterfall
# ---------------------------------------------------------------------------
def descomposicion(es, xp, ev):
    E = es.set_index("escenario").puntos_J8_J13
    k = lambda pref: E[[i for i in E.index if i.startswith(pref)][0]]  # noqa: E731
    A, B, D, G, H = k("A."), k("B."), k("D."), k("G."), k("H.")
    eb = ev[ev.jornada.isin(B2)]
    # Porción del salto de xPts asociada a partidos con roja rival (J9, J12, J13)
    roja = eb[eb.expulsion_rival_min != "N"].jornada.tolist()
    xg_roja = xp[xp.jornada.isin(roja)].xPts_npxG_sim.sum()
    pasos = [
        ("Ritmo real J1–J7 (×6/7)", A),
        ("Mala suerte J1–J7 que se corrige (rebote)", B - A),
        ("Calendario: rivales más débiles", D - B),
        ("Mejora de npxG (sin penales)", G - D),
        ("Sobre-rendimiento vs xPts en J8–J13", H - G),
    ]
    d = pd.DataFrame(pasos, columns=["componente", "puntos"])
    d["%_del_salto"] = 100 * d.puntos / (H - A)
    d.loc[0, "%_del_salto"] = np.nan
    d = pd.concat([d, pd.DataFrame([{"componente": "Puntos reales J8–J13", "puntos": H, "%_del_salto": np.nan}])])
    tabla("8_descomposicion_salto", d.round(2))
    R["descomp"] = d.round(2).to_dict("records")
    R["descomp_roja"] = {"jornadas": roja, "xpts_en_partidos_roja": rnd(xg_roja, 2)}

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    cum = 0
    for i, (lab, v) in enumerate(pasos + [("Puntos reales J8–J13", H)]):
        if i == 0 or i == len(pasos):
            ax.bar(i, v, color=C_GRIS, width=0.6, edgecolor=C_SURF, lw=2)
            y = v
            cum = v if i == 0 else cum
        else:
            ax.bar(i, v, bottom=cum, color=C_FAVOR if v >= 0 else C_CONTRA, width=0.6, edgecolor=C_SURF, lw=2)
            cum += v
            y = cum if v >= 0 else cum - v
        ax.text(i, max(y, cum) + 0.35, f"{v:+.1f}" if 0 < i < len(pasos) else f"{v:.1f}", ha="center", fontsize=10)
    ax.set_xticks(range(len(pasos) + 1))
    ax.set_xticklabels(["Ritmo\nJ1–J7", "Rebote\n(suerte J1–J7)", "Calendario\n(rival)", "Mejora\nnpxG",
                        "Sobre-\nrendimiento", "Reales\nJ8–J13"], fontsize=9)
    ax.set_ylabel("Puntos en 6 partidos")
    ax.set_ylim(0, 20.5)
    ax.set_title("De 0.9 a 18 puntos: descomposición aproximada del salto (modelo Poisson npxG)")
    fig.tight_layout()
    fig.savefig(OUT / "08_descomposicion_salto.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    rng = np.random.default_rng(SEED)
    p, e, j, lg, ctx, lb = validar()
    print("Validación OK. Anclas coinciden.")
    punto_quiebre(p, rng)
    p2 = antes_despues(p, rng)
    xp, sims = suerte(p2, e, rng)
    fr, L, mu = fuerza_rival(p2, lg)
    es, ajust, att1, def1, f = regresion_media(p2, fr, L, mu, lb, xp, rng)
    ev = eventos(p2, e, xp)
    jugadores(p2, e, j)
    contexto(p2, ctx)
    descomposicion(es, xp, ev)

    with pd.ExcelWriter(OUT / "tablas.xlsx", engine="openpyxl") as w:
        indice = pd.DataFrame({"hoja": list(TABLAS.keys())})
        indice.to_excel(w, sheet_name="indice", index=False)
        for n, df in TABLAS.items():
            df.to_excel(w, sheet_name=n, index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(
                    max(len(str(c.value)) if c.value is not None else 0 for c in col) + 2, 60)
    with open(OUT / "resultados.json", "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1, default=str)
    print(f"Listo: {len(TABLAS)} tablas en output/tablas.xlsx; PNG y resultados.json en output/")


if __name__ == "__main__":
    main()
