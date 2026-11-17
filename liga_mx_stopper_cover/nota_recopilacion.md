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
