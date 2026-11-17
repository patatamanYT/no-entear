# Nota de recopilación · centrales_apertura2026_j16.csv

Nota que entregó el asistente de IA (Grok o Muse) junto con el CSV, copiada tal cual. Al final está la revisión contra el CSV.

## Nota original (punto 7 del prompt)

- **Fuente:** FotMob (fotmob.com), páginas de jugador de la temporada 2026/2027 Liga MX y su página de estadísticas de la liga. Es la misma fuente para minutos, aéreos ganados, despejes, intercepciones, duelos ganados, regateado, % de pases y recuperaciones en casi todas las filas. El "Tackles" de FotMob es el total de entradas, no las ganadas, así que tackles_won se tomó solo de FootyMetrics (footymetrics.com), y solo donde su total de entradas coincidía con el de FotMob y el snapshot era vigente a J16.
- **Hasta qué jornada:** Jornada 16, partidos hasta el 14 de noviembre de 2026. La J17 aún no se juega (21–22 nov). Excepciones: Daniel Piña, Felipe Sánchez y Jonathan Pérez llevan datos hasta J15, porque jugaron en J16 pero sus totales a J16 no se pudieron verificar sin estimar, así que no se sumó ese partido.
- **Fecha de consulta:** 16–17 de noviembre de 2026.
- **Alcance:** 76 defensas centrales, solo posición habitual CB en FotMob y con 90 minutos o más en fase regular. Nadie cambió de equipo dentro de la Liga MX durante el torneo, así que no hay filas "Equipo1 / Equipo2". Rodrigo Schlegel (Atlas, 630 min) salió del club el 11 de septiembre, sus números son finales. Gilberto Sepúlveda va solo con FC Juárez (0 min con Chivas).
- **Métricas no encontradas:** errors en los 76 jugadores, FotMob no publica errores que terminan en tiro o gol en el resumen de temporada. tackles_won vacío en 41 de 76, porque FootyMetrics estaba desactualizado o devolvió error 429. Además, 9 jugadores quedaron solo con minutos verificados: Santiago Bueno, Sebastián Cáceres, Gilberto Sepúlveda, Diego Reyes, Carlos Salcedo (solo minutos + tackles_won), Alán Montes (solo minutos + tackles_won), Cristóbal Alfaro y Diogo Bagüí.
- **Advertencias:** Luan (Toluca) quedó sin tackles_won porque FootyMetrics decía 6 ganadas y el total de FotMob es solo 4, una contradicción entre proveedores. Gustavo Sánchez (Atlante) quedó sin tackles_won ni aerials_won porque esos dos valores eran derivados/extrapolados, no verificados. Eduardo Tercero (Atlante) es la única fila con métricas de otra fuente: solo sus minutos son de FotMob, el resto viene de playmakerstats/thefishy, así lo indica su celda fuente. Amaury García (Cruz Azul) va con reserva: FotMob lo lista como central, pero otras fuentes lo clasifican como mediocampista y jugó 2 partidos como DM. La URL de Lucas Abascia (Querétaro) aparece con slug "undefined" en FotMob. Hay discrepancias menores de 1 minuto o 1 acción entre FotMob y otras fuentes en algunos jugadores; en todos los casos se usó FotMob.

## Revisión contra el CSV (17 nov 2026)

Comprobado:
- 76 filas.
- Mínimo de 122 minutos, así que se cumple "90 minutos o más".
- `errors` vacío en las 76 filas.
- `tackles_won` vacío en 41 filas.
- Ningún equipo con "/", que coincide con "nadie cambió de equipo".
- Las advertencias de Luan, Gustavo Sánchez y Tercero coinciden con sus celdas.

Discrepancia:
- La nota dice que **9** jugadores quedaron solo con minutos, pero lista **8** nombres, y el CSV también tiene 8.

Efecto en el análisis (`--min-minutes 450`):
- Por los huecos, quedan fuera Sepúlveda, Reyes, Salcedo, Tercero, F. Sánchez, Orona y Porozo.
- **Piña y F. Sánchez solo llegan a J15.** Como los minutos corresponden al mismo periodo, los valores por 90 son consistentes. F. Sánchez además queda excluido por huecos.
- **Amaury García (657 min) sí entra en el grupo** (Stopper 29, Cover 75), aunque quizá sea mediocampista. Para excluirlo, cambia su `position` en el CSV.
- **Schlegel (630 min) entra con números finales**, porque salió del club el 11 de septiembre.

## Verificación manual contra FotMob

**Joaquim (Tigres)**, captura de la app de FotMob enviada por el usuario el 17 nov 2026, estadísticas de la temporada:

| Métrica | CSV | FotMob | Resultado |
|---|---|---|---|
| clearances | 65 | 65 | coincide |
| interceptions | 15 | 15 | coincide |
| dribbled_past | 7 | 7 | coincide |
| recoveries | 26 | 26 | coincide |
| tackles_won | 10 | — (FotMob: 15 tackles **totales**) | coherente: ganadas ≤ totales |
| aerials_won | 38 | 38 | coincide |
| duels_won | 67 | 67 | coincide |
| pass_completion_pct | 79.8 | 79.8 % | coincide |

- **Resultado:** las 7 métricas que se usan en el análisis coinciden con FotMob (2 capturas más, 17 nov 2026).
- **Sin verificar:** solo minutes (1024), que no sale en las capturas.
- **Otros datos de FotMob para Joaquim:** duels won % 60.9 y aerial duels won % 66.7.
- **FotMob tiene otros datos que el CSV no trae:** tackles totales (15), blocked shots (9), fouls committed (10) y defensive contributions (104).

## Columnas extra (segunda pasada de la IA, 17 nov 2026)

- **Columnas nuevas:** `tackles`, `blocked_shots`, `fouls_committed`, `duels_won_pct`, `aerials_won_pct`, `minutes_fotmob` y `fuente_extra`, sacadas de FotMob a J16.
- **Revisión automática:** las columnas originales quedaron idénticas en las 76 filas. Joaquim coincide con la captura (15 / 9 / 10 / 60.9 / 66.7). Ningún `tackles` es menor que `tackles_won`, y los porcentajes están entre 0 y 100. Cobertura entre los centrales con 450' o más: 87–91%.
- **Celdas vacías:** 19 jugadores tienen al menos una celda nueva vacía. Entre los 48 evaluados, a Luis Romo y Bruno Méndez les faltan las 5, a Santiago Ramos le faltan 4 y a Gonzalo Piovi le falta `blocked_shots`. En el radar, su eje sale en el centro y el script avisa.
- **Minutos distintos:** Piña (620 → 710), F. Sánchez (1350 → 1440), J. Pérez (414 → 459) y Alfaro (236 → 234). Las columnas extra de Piña, Sánchez y Pérez son de J16, mientras que sus columnas originales son de J15. Por eso el radar divide las columnas extra entre `minutes_fotmob`.

## Tercera pasada (Grok, 17 nov 2026): huecos y formaciones

- **Revisión automática:** 42 celdas llenadas, todas antes vacías, y ningún valor existente modificado. Porcentajes entre 0 y 100.
- **Ya completos para la fórmula:** Sepúlveda, Romo, Bruno Méndez, Villanueva, Santiago Ramos, Felipe Sánchez, Orona, Tercero y Piovi.
- **Siguen incompletos:**
  - Porozo: falta `dribbled_past`, que FotMob no publica para él.
  - Salcedo y Reyes: les faltan 4 métricas cada uno. Sus datos nuevos son de **FootyMetrics**, no de FotMob, y los porcentajes de Reyes se calcularon a partir de totales (416/490 y 53/80). Con `--max-missing 1` quedan fuera del análisis.
- **Eduardo Tercero:** `dribbled_past` 12 y `recoveries` 62 se suman a métricas que venían de playmakerstats/thefishy. Su fila mezcla fuentes.
- **Formaciones:** `formaciones.csv` es el archivo de Grok, con fuente y nota por equipo. Corrigió 4 de las 7 estimaciones por minutos: Toluca es línea de 2, y Atlas, San Luis y Santos son línea de 3. Luis Romo jugó de central en sus 12 partidos.

## Diego Reyes y Carlos Salcedo, capturas de FotMob (usuario, 17 nov 2026)

- Se reemplazaron los valores de FootyMetrics por los de FotMob y se llenaron sus huecos. `fuente_extra` lo indica.
- **Diferencias FootyMetrics → FotMob:**
  - Reyes: tackles 20 → 19, interceptions 19 → 17, duels_won_pct 66.3 → 63.4 (el de FootyMetrics era calculado) y pass_completion_pct 84.9 → 85.0.
  - Salcedo: clearances 37 → 36.
- **Valores nuevos de FotMob:**
  - Reyes: blocked_shots 15, recoveries 42, dribbled_past 4, aerials_won 26, duels_won 52 y aerials_won_pct 55.3.
  - Salcedo: blocked_shots 3, recoveries 39, dribbled_past 5, aerials_won 13, duels_won 30 y aerials_won_pct 46.4.
- **Sin verificar:** minutes (Reyes 1327 y Salcedo 781), que no salen en las capturas.
- **Jugadores verificados a mano contra FotMob:** Joaquim, Diego Reyes y Carlos Salcedo.

## Aldo Cruz (San Luis), capturas de FotMob (usuario, 17 nov 2026)

- **Fila nueva:** Aldo Cruz no estaba en el CSV porque es lateral izquierdo de posición, pero fue tercer central titular de San Luis en J8–J16.
- **Valores de FotMob:** 996' (14 partidos, 10 de titular), tackles 8, interceptions 7, blocked_shots 5, fouls 4, recoveries 29, dribbled_past 4, clearances 46, duels_won 26, duels_won_pct 63.4, aerials_won 13, aerials_won_pct 72.2 y pass_completion_pct 87.3.
- **Ojo:** son totales de toda su temporada, incluidos los partidos que jugó de lateral.
- **Jugadores verificados a mano:** Joaquim, Diego Reyes, Carlos Salcedo y Aldo Cruz (este último cargado directamente desde FotMob).

## Jackson Porozo, capturas de FotMob (usuario, 17 nov 2026)

- **Coinciden con el CSV las 11 métricas visibles:** duels_won 75, duels_won_pct 73.5, aerials_won 45, aerials_won_pct 73.8, tackles 20, interceptions 21, blocked_shots 10, fouls_committed 8, recoveries 28, clearances 100 y pass_completion_pct 92.4.
- **"Dribbled past" no aparece** en su sección Defending; en otros jugadores sí sale, aunque valga poco (por ejemplo, Reyes 4). Es probable que FotMob oculte filas con valor 0, porque "Penalties conceded" tampoco sale en jugadores con 0. Pero no está confirmado, así que `dribbled_past` sigue vacío.
- **Si fuera 0:** su Cobertura pasaría de 87.5 a 96.4, y la de los demás cambiaría como máximo 3.6 puntos.
- **Jugadores verificados a mano:** Joaquim, Diego Reyes, Carlos Salcedo, Aldo Cruz y Jackson Porozo.
