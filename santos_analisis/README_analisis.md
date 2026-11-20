# Análisis: Santos Laguna, Apertura 2026 — ¿mejora real o suerte?

## Estructura

```
santos_analisis/
├── data/                    # CSV originales + README de datos (sin modificar)
├── src/analisis_santos.py   # script único, reproducible
├── output/
│   ├── informe.md           # informe con resumen, hallazgos, tablas, gráficas y limitaciones
│   ├── tablas.xlsx          # todas las tablas calculadas (hoja "indice")
│   ├── resultados.json      # cifras clave en formato máquina
│   └── *.png                # gráficas
├── requirements.txt
└── README_analisis.md
```

## Cómo reproducir

Desde la carpeta `santos_analisis`:

```bash
pip install -r requirements.txt
```

```bash
python3 src/analisis_santos.py
```

El script:
1. **Valida** los CSV (tipos, duplicados, jornadas, N/D, coherencia entre archivos) y **se detiene** si los datos ancla
   (1 pt J1–J7, 18 pts J8–J13, 4–12 y 15–4 en goles) no coinciden.
2. Calcula las secciones 1–8 del informe y escribe tablas, gráficas y `resultados.json` en `output/`.

`informe.md` es la interpretación escrita de esas salidas; cada tabla del informe cita la hoja de `tablas.xlsx`
de la que proviene. Si cambian los datos, hay que volver a ejecutar el script y revisar el texto.

## Decisiones metodológicas

- **Semilla fija** `SEED = 20261120` (`numpy.random.default_rng`) para simulaciones, bootstrap y permutaciones.
- **Medida principal:** xG sin penales (`xg_*_sin_penales`). Penal = 0.79 xG (verificado: xG − npxG = 0.79 × penales).
- **N/D = ausente**, nunca cero. El PPDA (16/16 N/D) se reporta como no disponible.
- **xPts:** 200 000 simulaciones Poisson independientes por partido (λ = npxG a favor / en contra), contrastadas con el cálculo analítico.
- **Bootstrap:** percentil, 10 000 remuestreos de partidos dentro de cada bloque.
- **Punto de cambio:** CUSUM sobre la diferencia de npxG; `ruptures` PELT (modelo l2, penalizaciones BIC/2·BIC/AIC
  con σ² estimada de primeras diferencias) y Binseg con un quiebre; barrido exhaustivo de cortes únicos.
- **Fuerza de rival:** ppg y xGD por partido del rival, (a) antes de la fecha del partido y (b) en J1–J16, excluyendo
  siempre su partido contra Santos. Ajuste multiplicativo del npxG por la defensa y el ataque relativos del rival.
- **Regresión a la media:** pesos de confiabilidad del xG a 7 partidos estimados con la varianza entre y dentro de
  equipos de la liga; el prior es la línea base histórica de Santos (`linea_base.csv`).
- **npxG individual:** `xg` del jugador − 0.79 por penal ejecutado (según `eventos_partido.csv`).
