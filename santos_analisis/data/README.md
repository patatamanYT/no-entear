# Santos Laguna — Apertura 2026, jornadas 1–16

Corte: **2026-11-19**, zona horaria de referencia America/Mexico_City. Recolección mediante Firecrawl. Se excluyen Leagues Cup, partidos amistosos y J17 ante León, programada para el 21 de noviembre. Los resultados y las estadísticas corresponden al primer equipo varonil.

## Archivos

| Archivo | Filas de datos | Unidad de observación |
|---|---:|---|
| partidos_santos.csv | 16 | Partido de Santos, J1–J16 |
| eventos_partido.csv | 53 | Gol, penal fallado o expulsión; incluye dos expulsiones del cuerpo técnico |
| jugadores_partido.csv | 253 | Jugador de Santos que participó en un partido; excluye suplentes sin ingreso |
| resultados_liga.csv | 144 | Todos los partidos de las 16 jornadas: nueve por jornada |
| contexto_santos.csv | 37 | Refuerzo, debut en el torneo, baja, lesión, suspensión, formación o declaración |
| linea_base.csv | 2 | Fase regular completa de Clausura 2026 y Apertura 2025 |

Se conservaron las columnas solicitadas, sin columnas auxiliares. Los textos entre paréntesis de la solicitud se interpretaron como instrucciones, no como parte del nombre de columna. Por ello se usan, por ejemplo, `resultado`, `ppda_santos`, `expulsion_rival` y `calificacion_fotmob`.

CSV separados por comas, codificación UTF-8 con BOM, decimales con punto. El literal **N/D** significa que el valor no pudo obtenerse de forma verificable; no equivale a cero. Cada fila tiene `fuente_url`. Cuando intervienen varias páginas, sus URL se separan mediante ` | ` dentro de la misma celda.

## Fuentes y criterio de xG

**FotMob es la única fuente de todos los xG, xG sin penales y xA**, tanto de partidos como de jugadores y líneas base. No se mezclaron proveedores. La propia página identifica sus estadísticas como suministradas por Opta; la fuente consultada y consignada es FotMob.

- Partidos, eventos, formaciones y jugadores: las fichas individuales de FotMob enlazadas en cada fila. Se contrastaron el contenido visible y los datos estructurados incluidos en esas mismas páginas.
- Calendario de referencia: [partidos de Santos en FotMob](https://www.fotmob.com/teams/7857/fixtures/santos-laguna).
- Líneas base: [tabla histórica de FotMob](https://www.fotmob.com/leagues/230/table/liga-mx/players?season=2025-2026+-+Clausura), que contiene las secciones Clausura y Apertura, y sus páginas de xG específicas de cada torneo, enlazadas en `linea_base.csv`.
- Contexto: comunicados de **Club Santos Laguna** y notas/entrevistas de **Mediotiempo, TUDN, Milenio, Futbol Total, ABC Color, Infobae, RÉCORD y Excélsior**. Cada hecho tiene su enlace directo. Las declaraciones se parafrasearon.
- No se utilizaron valores de Sofascore, FBref, Transfermarkt o Liga MX para completar estadísticas ausentes.

## Convenciones importantes

- `local_visita`: **L** = local, **V** = visitante. `resultado`: G/E/P. Posesión expresada como porcentaje entre 0 y 100, sin el signo `%`.
- Fechas de partidos: fecha real obtenida del inicio UTC de la ficha y convertida al día del centro de México. El día coincide con la fecha local de las sedes incluidas, también en Tijuana. No se sustituyó por la fecha nominal de la jornada.
- **Querétaro–Monterrey, J7, se jugó el 2026-11-14**. Se incluye con esa fecha, aunque las otras fechas de J7 son anteriores. Los 144 encuentros incluidos aparecen terminados al corte.
- `formacion_santos`: dibujo inicial registrado por FotMob. No prueba que el equipo mantuviera esa estructura con y sin balón, ni identifica cambios durante el encuentro.
- `posicion` en jugadores: **posición habitual amplia que FotMob proporciona en la ficha del partido**: Portero, Defensa, Mediocampista o Delantero. No se dedujo una posición específica por su lugar gráfico en la alineación. Un jugador puede actuar en una zona distinta de su posición habitual.
- Minutos: valor publicado por FotMob; no se calcularon restando el minuto del cambio de 90. Calificación: escala publicada de FotMob, conservada a un decimal.
- `marcador_al_minuto_60`: siempre **Santos–rival**, sin importar la sede. Se reconstruye con los goles válidos registrados hasta el minuto 60, incluyendo el tiempo añadido del primer tiempo. Los goles de penal y los autogoles se cuentan una sola vez.
- `penales_a_favor` y `penales_en_contra`: intentos ejecutados, convertidos o fallados, según el registro de eventos. No incluye decisiones anuladas por VAR. Una concesión y su ejecución no son dos eventos separados.
- En un `autogol`, `equipo` identifica al equipo del jugador que lo cometió. `autogoles_a_favor` contabiliza los que benefician a Santos.
- `expulsion_santos` y `expulsion_rival`: **expulsiones de futbolistas**, con todos sus minutos en la celda. Una segunda amarilla se registra como `amarilla_segunda`, sin duplicarla como roja directa.
- `eventos_partido.csv` también conserva las rojas a **Renato Paiva, J3, 75**, y **Miguel Pinto Santos, J4, 90+7**. Son integrantes del cuerpo técnico; no implican inferioridad numérica en el campo y no se incluyen en las dos columnas de expulsiones de futbolistas.
- `asistente=N/D`: no hubo una asistencia atribuida por la fuente o no aplica, como en rojas y penales. No se inventa un asistente. Los totales individuales de goles/asistencias que el panel del portero omite se verificaron contra el registro completo de eventos.
- En contexto, se distingue en la descripción la fecha del partido, de presentación o de publicación. La fecha exacta de una decisión interna de continuidad que solo se relató retrospectivamente permanece indicada como N/D en la descripción.
- Los debuts son **la primera participación con Santos en este Apertura 2026**, dentro de J1–J16; no necesariamente su primer partido histórico con el club. Se incluyen los seis refuerzos presentados en julio y las incorporaciones posteriores de Esteban Lozano y Facundo Cáseres.

## Datos faltantes

| Archivo | Campo | Filas con N/D |
|---|---|---:|
| partidos_santos.csv | ppda_santos | 16 |
| eventos_partido.csv | asistente | 25 |
| jugadores_partido.csv | tiros | 132 |
| jugadores_partido.csv | xg | 130 |
| jugadores_partido.csv | xa | 78 |
| jugadores_partido.csv | calificacion_fotmob | 25 |

No hay otros N/D en las celdas de los seis CSV. La ausencia de una estadística individual en la página o de un valor numérico en sus datos estructurados **no se convirtió automáticamente en cero**. Esto afecta especialmente a futbolistas sin producción ofensiva registrada y porteros. Las sumas individuales de xG/xA/tiros con N/D no deben tratarse como totales completos del equipo. Para comparar equipos o tramos, utilizar los campos completos de `partidos_santos.csv`.

No se obtuvo PPDA publicado. El contexto no pretende ser un registro exhaustivo de todas las salidas, lesiones o sanciones del plantel: no se incluyeron rumores como bajas confirmadas. Tampoco se verificaron todas las fechas individuales de firma de los seis refuerzos iniciales; se informa su presentación colectiva del 14 de julio. La duración total de la suspensión de Paiva y la fecha exacta de las decisiones internas de respaldarlo no quedaron establecidas.

## Líneas base: totales y promedios

Para preservar los encabezados solicitados y permitir recalcular cualquier promedio, `linea_base.csv` contiene **totales de fase regular**, no promedios en las columnas de puntos/goles/xG. Santos no disputó liguilla en esos dos torneos; sus cifras no incorporan partidos adicionales.

| Torneo | PJ | Puntos | GF | GC | xGF FotMob | xGC FotMob |
|---|---:|---:|---:|---:|---:|---:|
| Clausura 2026 | 17 | 12 | 20 | 38 | 22.2 | 28.6 |
| Apertura 2025 | 17 | 20 | 22 | 28 | 20.3 | 32.0 |

Promedios por partido, calculados dividiendo cada total entre 17:

| Torneo | Puntos/PJ | GF/PJ | GC/PJ | xGF/PJ | xGC/PJ |
|---|---:|---:|---:|---:|---:|
| Clausura 2026 | 0.706 | 1.176 | 2.235 | 1.306 | 1.682 |
| Apertura 2025 | 1.176 | 1.294 | 1.647 | 1.194 | 1.882 |

Los xG históricos se publican a un decimal en las páginas agregadas; no se les atribuye una precisión mayor. Los xG de partidos se conservaron con la precisión mostrada en sus fichas.

## Verificaciones solicitadas

**Las tres comprobaciones de resultados se cumplen.**

| Tramo/partido | Comprobación |
|---|---|
| J1–J7 | 1 punto; seis derrotas, un empate; 4 GF, 12 GC |
| J8–J13 | Seis victorias contra Juárez, Toluca, Pachuca, San Luis, Querétaro y Pumas; 18 puntos; 15 GF, 4 GC |
| J14 | Derrota 1–4 ante Tijuana, 2026-10-25 |
| J15 | Victoria 1–0 ante Necaxa, 2026-11-01; el gol fue un autogol de Matías Espíndola |
| J16 | Victoria 2–0 ante Atlante, 2026-11-06 |
| Total J1–J16 | 25 puntos; ocho victorias, un empate, siete derrotas; 23 GF, 20 GC |

También se verificaron: claves únicas, once titulares de Santos por encuentro, goles de eventos contra marcadores finales y de primer tiempo, marcador al 60, goles individuales más autogoles a favor, y correspondencia entre el archivo de Santos y el archivo de liga. La tabla reconstruida con los 144 resultados reproduce PJ, puntos, GF y GC de los **18 clubes** de la tabla de FotMob.

## Inconsistencias encontradas y resolución

1. **Calendario histórico frente a tabla histórica del Clausura 2026.** El calendario de equipo consultado devuelve una secuencia de marcadores que no reproduce los totales de la tabla histórica. Además, abrir algunos enlaces antiguos por su fragmento `#matchId` devolvió la ficha más reciente del mismo cruce. Esas recuperaciones se descartaron para la línea base. Se utilizaron las páginas explícitas del Clausura 2025/2026: tabla 17 PJ, 12 puntos, 20–38 y agregados xG 22.2–28.6. El cierre 12 puntos, 20–38 está corroborado por [Sports Illustrated México](https://www.si.com/mx/liga-mx/joao-pedro-bicampeon-goleo-bueno-malo-feo-jornada-17-clausura-2026). No se mezclaron fichas actuales con partidos históricos.
2. **Diferencia de minutos en la crónica oficial de Pumas.** El club describe los goles de Aguirre y Pardo a los minutos 5 y 79; FotMob los registra a los minutos **6 y 80**. Se conservó FotMob en el registro uniforme de eventos. Nathan Silva en FotMob y Nathanael Ananias en la crónica oficial se refieren al defensor expulsado en ese partido.
3. **Día civil del partido ante Tijuana.** Algunas notas hablan del 26 de octubre. El inicio UTC cae en ese día, pero el partido se disputó el **25 de octubre en México**. Se usa 2026-10-25 en los resultados. El parte médico posterior de Diego González se fecha por separado.
4. **Presentación de julio y plantilla supuestamente cerrada.** La nota del 14 de julio indica seis refuerzos y plantel cerrado; después se anunciaron Lozano, el 31 de agosto, y Cáseres, el 4 de septiembre. Se conservan ambos momentos, sin suponer que los ocho llegaron en julio.
5. **Rojas del cuerpo técnico.** La lectura sin distinguir personas puede hacer parecer que Santos sufrió dos expulsiones de jugadores. Las dos corresponden a entrenadores. Se separó su efecto en las convenciones descritas arriba.
6. **Redondeo y proveedor.** La suma de xG de las fichas J1–J7 es 7.64. Una nota de Claro Sports publica 7.65 y para J8–J11 publica 9.71 frente a 9.72 en las fichas recuperadas. Se conservan las fichas de FotMob; no se utilizan cifras de la nota para completar o ajustar xG.

## Lectura inicial para el análisis

La mejora en resultados coincide con mayor producción ofensiva: Santos pasó de **1.09 a 2.66 xG por partido**, de **2.71 a 6.67 tiros a puerta** y de **1.43 a 4.33 grandes ocasiones**, al comparar J1–J7 con J8–J13. Los xG concedidos bajaron de 1.52 a 1.37 por partido, una reducción más moderada que la de goles recibidos.

La racha debe estudiarse junto con las incidencias: hubo expulsiones rivales en J9, J12 y J13; Santos ejecutó seis penales durante J8–J13, convirtió cuatro y falló dos. La continuidad directiva y las incorporaciones son contexto documentado, pero estos datos por sí solos no prueban qué proporción del cambio causó cada factor. Las formaciones alternan 3-4-3 y 5-4-1 durante la racha; no respaldan una explicación basada en un único cambio permanente de dibujo.

En el cierre J14–J16, Santos obtuvo seis puntos con **2.09 xG a favor y 8.25 en contra**. El 1–0 ante Necaxa llegó por autogol; ante Atlante registró 0.65–1.92 xG y dos expulsiones del rival. Conviene separar el rendimiento de la racha central de la sostenibilidad de las victorias posteriores.
