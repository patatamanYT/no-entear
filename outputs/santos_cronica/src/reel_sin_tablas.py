"""Construye el Reel con reel.py cuando no están las tablas del análisis.

Toma cada cifra de la columna valor_exacto de verificacion_numeros.csv, que a su
vez se copió de tablas.xlsx y tablas_v2.xlsx. Con las tablas disponibles, usa
reel.py directamente: es la fuente principal.

    tsrct project create -p mi_reel.tsrct
    python src/reel_sin_tablas.py RUTA_A_TSRCT mi_reel.tsrct
"""
import csv
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "verificacion_numeros.csv"


def datos_verificados():
    rows = {r["dato"]: r["valor_exacto"].strip() for r in csv.DictReader(open(CSV, encoding="utf-8-sig"))}
    num = lambda k: float(rows[k])
    seq = rows["Tramos y resultados"].split()
    games = [(int(seq[i][1:]), seq[i + 1]) for i in range(0, len(seq), 2)]
    start_n, run_n = int(num("Jornadas del arranque")), int(num("Denominador de partidos y victorias"))
    assert [g for _, g in games[start_n:start_n + run_n]] == ["G"] * run_n
    juarez = rows["Primera victoria y tema en el Corona"].split("·")[1].strip()
    return dict(
        games=games,
        spans=[f"J1–J{start_n}", f"J{start_n + 1}–J{start_n + run_n}", f"J{start_n + run_n + 1}–J{len(games)}"],
        start=int(num("Puntos del arranque")), run=int(num("Puntos de la racha")),
        start_n=start_n, run_n=run_n,
        expected=num("Puntos esperados del arranque"),
        bounce=num("Parte del salto atribuida al rebote"),
        goals=int(num("Goles a favor")), pens=int(num("Goles de penal")),
        reds=int(num("Partidos con roja rival")),
        clean=int(num("Victorias sin penal, roja rival ni autogol")),
        without=int(num("Puntos al quitar goles de penal y autogoles")),
        shots_start=num("Tiros a puerta por partido (arranque)"),
        shots_run=num("Tiros a puerta por partido (racha)"),
        keeper_start=num("Puntos estimados por paradas (arranque)"),
        keeper_run=num("Puntos estimados por paradas (racha)"),
        placement=num("Colocación de los tiros rivales"),
        juarez=juarez,
        juarez_date=rows["Primera victoria y tema en el Corona"].split("·")[0].strip(),
        atlante_date=rows["Afición corea tras el triunfo ante Atlante al salir"].split("·")[0].strip(),
        improve=num("Parte estimada del salto por mejora en ataque"),
    )


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("reel", HERE / "reel.py")
    reel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reel)
    data = datos_verificados()
    reel.load_data = lambda root: data
    sys.argv = ["reel.py", sys.argv[1], sys.argv[2], str(HERE)]
    reel.main()
