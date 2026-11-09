# B.13 Exportar las probabilidades del modelo para el tablero (3 y 6 meses)
# Pegar como celda nueva al final de la Parte B de "Evidencia 2_6.ipynb" y ejecutar
# después de haber corrido todo el notebook. Genera predicciones_tablero.json,
# que se carga en el tablero con el botón "Cargar predicciones (.json)".
import json
from sklearn.base import clone
from sklearn.metrics import f1_score

# Modelo de 3 meses: la Red Neuronal ya entrenada (mejor partición, 70/30)
modelo3 = ajustados[(mejor["Partición"], mejor["Modelo"])]["modelo"]
p3 = modelo3.predict_proba(X)

# Modelo de 6 meses: misma configuración; objetivo = promedio de los meses de inventario de t+1 a t+6
g = df.groupby(["region", "product_id"])["meses_inv"]
df["meses_6m"] = pd.concat([g.shift(-h) for h in range(1, 7)], axis=1).mean(axis=1, skipna=False)
y6 = pd.cut(df.loc[d.index, "meses_6m"], [-np.inf, *cortes, np.inf], labels=False)
ok6 = y6.notna()

# Prueba temporal: entrenar con objetivos que terminan a más tardar en el mes 18 y probar con el mes 18,
# cuyo objetivo (meses 19 a 24) el modelo no vio
tr = ok6 & (d["t"] + 6 <= 18)
te = ok6 & (d["t"] == 18)
m6 = clone(modelo3).fit(X[tr], y6[tr].astype(int))
print("F1 macro del modelo a 6 meses (prueba temporal):",
      round(f1_score(y6[te].astype(int), m6.predict(X[te]), average="macro"), 3))

# Modelo final de 6 meses con todos los objetivos disponibles
m6 = clone(modelo3).fit(X[ok6], y6[ok6].astype(int))
p6 = m6.predict_proba(X)
assert p3.shape[1] == 4 and p6.shape[1] == 4

NOMBRES = {"Ciudad de México": "CDMX",
           "Zona Metropolitana de Monterrey": "Monterrey",
           "Zona Metropolitana de Guadalajara": "Guadalajara"}
demanda = pd.qcut(d["units_expected"], 3, labels=["Baja", "Media", "Alta"]).astype(str)
real3 = d["nivel_obj"].astype(int)
real6 = y6.fillna(-1).astype(int)

filas = []
for k, (i, r) in enumerate(d.iterrows()):
    filas.append([NOMBRES.get(r["region"], r["region"]), r["product_name"], int(r["year"]), int(r["mes"]),
                  demanda[i],
                  *[int(round(v * 1000)) for v in p3[k]],
                  *[int(round(v * 1000)) for v in p6[k]],
                  int(real3[i]), int(real6[i])])

columnas = ["region", "producto", "anio", "mes", "demanda",
            "p3_0", "p3_1", "p3_2", "p3_3", "p6_0", "p6_1", "p6_2", "p6_3", "real3", "real6"]
with open("predicciones_tablero.json", "w", encoding="utf-8") as f:
    json.dump({"version": 1, "niveles": NIVELES, "columnas": columnas, "filas": filas}, f, ensure_ascii=False)
print("Combinaciones exportadas:", len(filas))

try:
    from google.colab import files
    files.download("predicciones_tablero.json")
except ImportError:
    print("Archivo guardado junto al notebook: predicciones_tablero.json")
