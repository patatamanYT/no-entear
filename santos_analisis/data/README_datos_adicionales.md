# Santos Laguna — datos adicionales, Apertura 2026 J1–J16

Corte: 2026-11-19. Se entregan los **cinco** archivos enumerados en la solicitud (7–11), aunque su introducción menciona tres. No se incluyen J17, otras competiciones ni análisis de hipótesis. Los CSV originales permanecen sin cambios.

## Archivos y claves

| Archivo | Filas | Cobertura |
|---|---:|---|
| portero_partido.csv | 16 | Carlos Acevedo, único portero con minutos en los 16 partidos |
| defensa_jugador_partido.csv | 237 | Todas las participaciones de jugadores de campo de la base |
| posicion_rol_partido.csv | 176 | Once titulares por partido, incluido el portero |
| disponibilidad_jugadores.csv | 12 | Episodios documentados de lesión, reaparición o salida del club; no es una matriz médica completa |
| construccion_jugador_partido.csv | 253 | Todas las participaciones de la base, incluido el portero |

Claves: `jornada` y el nombre **exacto** de `jugadores_partido.csv`; en el archivo del portero, el campo de nombre se llama `portero`, como se pidió. Los titulares coinciden con `titular=S` de la base. Las posiciones amplias de defensa/construcción se conservan tal como aparecían en la base; no se sustituyen por los roles tácticos.

Separador coma, codificación UTF-8 con BOM y punto decimal. El literal `N/D` nunca se interpreta como cero. Se agregó `fuente` a todos los archivos para identificar de forma explícita la mezcla de fuentes en disponibilidad. Cada fila contiene una o más URL directas; varias se separan por ` | `.

## Fuentes y recuperación

Las estadísticas y alineaciones proceden exclusivamente de **FotMob**, partido por partido, incluidos los datos estructurados que la misma página utiliza para mostrar los paneles individuales. Los números no se tomaron de promedios de temporada. Se reutilizaron las fichas recuperadas para la base y se volvieron a abrir las vistas de J6, J10 y J15 para comprobar los casos especiales del portero.

FotMob identifica sus estadísticas de estos encuentros como suministradas por **Opta**. Tanto el **xG** como el **xGOT** de este paquete proceden de FotMob y de los mismos encuentros; no se emplearon xG/xGOT de Sofascore u otro proveedor.

Para disponibilidad se usaron también comunicados de **Club Santos Laguna**, **Telediario**, **ABC Color** y **Futbol Total**, que reproducen comunicados o declaraciones; y una nota de **Bolavip**, que atribuye las molestias de Tahiel a Manolo Ibarrola. La columna `fuente` distingue estos casos. No se incluyeron rumores de fichajes ni lesiones de otros torneos como hechos del Apertura 2026.

## Verificaciones

- **Minutos:** 237/237 filas de defensa, 253/253 de construcción y 16/16 del portero coinciden exactamente con `jugadores_partido.csv`: **cero diferencias**. Se verificaron contra los minutos publicados, sin deducirlos de los cambios.
- **Goles recibidos:** 16/16 coinciden con `goles_rival` en `partidos_santos.csv`: **cero diferencias**, 20 goles en total.
- **xG:** 16/16 valores en contra coinciden con `xg_rival` de la base.
- **xGOT:** disponible para los 16 partidos, siempre FotMob. En 15 está en el panel de Acevedo. En **J10 ante Pachuca**, ese panel lo omite, pero el apartado del encuentro publica explícitamente **0.00 xGOT para Pachuca**. Ese cero se tomó de la fuente; no se dedujo del número de tiros ni de las paradas. La fila enlaza ambas vistas.
- **Goles evitados:** se conserva `Goals prevented` de FotMob en los 15 casos publicados. En J10 se aplica únicamente la identidad solicitada: xGOT publicado 0.00 menos goles recibidos publicados 0 = 0. No se construyó un modelo propio de xGOT. En los 16 casos, la resta cuadra con los valores entregados.
- **Claves:** no hay duplicados por jugador/jornada ni claves nuevas en defensa, construcción o roles. Todos los nombres de disponibilidad existen en la base.
- **Roles:** 176 filas y exactamente once por jornada. El archivo no tiene columna `minutos`: los minutos de reloj de entrada/salida no se equiparan automáticamente con los minutos estadísticos.

## Inconsistencias conservadas, sin corrección artificial

| Jornada | Tiros a puerta recibidos, FotMob | Paradas de Acevedo, FotMob | Goles recibidos | Observación |
|---|---:|---:|---:|---|
| 6, Tigres | 2 | 3 | 0 | La fuente publica más paradas que tiros a puerta |
| 15, Necaxa | 9 | 8 | 0 | Paradas más goles no reproduce el total de tiros a puerta |

Ambas discrepancias aparecen en la página del partido y se confirmaron al volver a abrirla. Se conservaron los valores publicados; no se sumó/restó una parada para hacerlos cuadrar. El origen exacto de la diferencia no quedó establecido: **no debe calcularse una tasa de paradas a partir de esas filas sin resolver primero la discrepancia**.

En J13, FotMob registra la salida por lesión de Orona al **21**, mientras la crónica del club citada en el paquete base la describe al **20**. Este archivo mantiene el reloj de FotMob. Los minutos acumulados publicados y el minuto de un cambio pueden seguir convenciones distintas —por ejemplo, 45 minutos jugados frente a cambio marcado al 46—; no se forzaron equivalencias.

## Diccionario y límites de interpretación

### Portero

`tiros_a_puerta_recibidos` procede de los tiros a puerta del rival en la vista del partido. Acevedo disputó los 90 minutos en todos los casos, por lo que no se repartieron estadísticas entre porteros. `xg_en_contra` y `xgot_en_contra` incluyen los penales del encuentro; no son versiones sin penal.

`penales_recibidos` cuenta ejecuciones rivales de penal, convertidas o falladas, del registro completo de eventos. `penales_atajados` identifica fallos cuyo resultado sea expresamente una parada. En J1–J16 los dos penales rivales registrados se convirtieron: las otras filas con cero significan ausencia de ejecuciones, no datos faltantes rellenados.

`salidas_exitosas` queda N/D: FotMob ofrece `Acted as sweeper`, `High claim` y `Punches`, pero no un total definido de **todas** las salidas exitosas. No se sumaron ni se renombraron métricas distintas. Los pases largos precisos son el numerador de `Accurate long balls`, sin convertir porcentajes en conteos estimados.

### Defensa

- `duelos_ganados`: `Duels won`; si falta ese total, solo se suma duelos terrestres y aéreos ganados cuando ambos conteos son explícitos.
- `duelos_totales`: suma de los denominadores explícitos de los duelos terrestres y aéreos. Si falta esa pareja, se utiliza ganados + perdidos únicamente cuando ambos totales existen. Las dos formas se contrastaron donde coexistían; no hubo diferencias.
- `duelos_aereos_ganados/totales`: numerador y denominador de `Aerial duels won`.
- `recuperaciones`, `intercepciones`, `despejes`, `bloqueos_de_tiro`: `Recoveries`, `Interceptions`, `Clearances`, `Blocks`. El último corresponde a bloqueos defensivos, **no** a los remates propios bloqueados (`Blocked shots`).
- `entradas_totales`: el conteo publicado como `Tackles`. La fuente no ofrece el desglose de entradas ganadas; `entradas_ganadas` queda N/D.
- `faltas_cometidas/recibidas`: `Fouls committed` y `Was fouled`. Algunas entradas de la fuente tienen una etiqueta sin valor numérico: se dejan N/D.
- `perdidas_de_balon`: N/D. `Dispossessed` registra desposesiones; no representa necesariamente todas las pérdidas por pases, controles y otras acciones. No se lo hizo pasar por el total solicitado.

### Construcción

`pases_completados/intentos` son el numerador y denominador de `Accurate passes`; pases largos y centros precisos son sus conteos explícitos. `ocasiones_creadas` usa `Chances created`, `grandes_ocasiones_creadas` usa `Big chances created`, `xa` usa `Expected assists (xA)`, `regates_exitosos` usa `Successful dribbles` y `toques_area_rival` usa `Touches in opposition box`.

No se equiparan **pases que rompen líneas** (`Line breaking passes`) con **pases progresivos**: la fuente no ofrece el segundo campo con esa definición. Tampoco se ofrecen conducciones progresivas. `pases_clave` queda N/D porque no se publica como métrica separada: no se copió `Chances created` ni se le restaron asistencias sin una definición explícita del proveedor. No se mezclaron estas columnas con datos de otro proveedor.

Que una estadística no figure, o que el objeto de la página no contenga un número, **no demuestra que valga cero**. Esto explica muchos N/D de xA, centros, regates y grandes ocasiones. Por ello no deben sumarse filas con N/D como si fueran ceros ni considerarse completas las sumas por equipo.

### Posición y salida

Se tradujeron las etiquetas de posición de FotMob asociadas al código de la posición inicial. La correspondencia se comprobó con las etiquetas explícitas del apartado de jugadores destacados de las fichas recuperadas. No se dedujo una posición por la edad, el nombre o la posición habitual.

Se distinguen lateral, carrilero, central, mediocentro defensivo, interior, medio de banda, mediapunta, extremo y delantero. Se conserva el lado cuando la etiqueta lo explicita. Un `CB` se entrega como `central`: no se inventa si era central derecho o izquierdo. No pudo confirmarse un código, correspondiente a **Fran Villalba, J4**; queda N/D.

Como el archivo solo contiene titulares, `minuto_entrada` es N/D en todas las filas: no es un ingreso desde el banquillo. `minuto_salida` es el reloj del evento de sustitución o expulsión; se conserva el añadido como `90+3`. Cuando termina el partido sin salir, queda N/D, no se fabrica una sustitución al 90.

Solo se asigna `motivo_salida=lesion` cuando FotMob marca explícitamente `injuredPlayerOut=true`. Se hallaron cuatro casos: Orona J10, Aguirre J12, Orona J13 y Jonathan Pérez J14. Un cambio sin esa marca **no prueba** que fuese táctico o por rendimiento; su motivo queda N/D. No hubo expulsiones de futbolistas de Santos en estos partidos.

### Disponibilidad

Cada fila es un episodio o una reaparición documentada. `tipo` conserva las categorías pedidas; una reaparición tras lesión se codifica `lesion` y se identifica expresamente en `detalle`, pues el esquema no incluye una categoría `regreso`.

`jornada_inicio` es la primera jornada afectada en Liga MX; puede ser el partido en que se lesiona y todavía acumula minutos. Si la lesión ocurrió en otra competición entre jornadas, se usa la primera jornada de Liga MX afectada. `jornada_fin` delimita el episodio por la siguiente participación comprobada, **no certifica una fecha médica de recuperación**. En las filas de reaparición, inicio y fin indican la jornada del regreso. N/D significa fin/alta no confirmado al corte; no equivale a una baja eterna.

- **Orona:** la lesión de J13 incluye participación parcial; la primera ausencia completa de ese episodio es J14. J14–J16 sin convocatoria, según las fichas.
- **Diego González:** se lesiona en J14, pero juega; no corresponde marcar todo J14 como partido sin él. Las primeras ausencias completas son J15 y J16.
- **Di Yorio:** lesión previa a J4. Reaparece en el banquillo de J16, pero no juega; se registra ese regreso a convocatoria por separado y no se inventa un alta médica.
- **Tahiel:** molestias previas a J16 atribuidas por una nota periodística; fue suplente y jugó 45 minutos. Es disponibilidad parcial, no ausencia del partido ni diagnóstico médico formal.
- **Gruezo:** baja del club anunciada entre J7 y J8. No se retrotrae la rescisión a su última aparición en Liga MX.

No se dedujo lesión, sanción o convocatoria de selección por el simple hecho de no jugar. No se encontró un evento suficientemente respaldado de suspensión o selección para incluirlo. La ausencia de filas de un jugador **no certifica salud plena**. La tabla de cobertura al final distingue quién jugó, quién figuró en convocatoria y qué causas siguen sin verificar.

## Reproducibilidad

La extracción y validación se conservaron en el espacio de trabajo en `work/crear_adicionales.py`, con el registro `work/adicionales_audit.json` y las fichas originales de FotMob. No hay muestreo ni operaciones aleatorias. Los CSV base se comprobaron mediante SHA-256 antes y después: permanecen sin cambios.

## N/D por campo

Los porcentajes siguientes usan todas las filas de cada archivo como denominador. Incluyen N/D estructurales —por ejemplo, entrada de un suplente en un archivo que solo contiene titulares—, no solo valores omitidos por la fuente.

### portero_partido.csv — 16 filas

| Campo | Filas N/D | % N/D |
|---|---:|---:|
| jornada | 0 | 0.00% |
| portero | 0 | 0.00% |
| minutos | 0 | 0.00% |
| goles_recibidos | 0 | 0.00% |
| tiros_a_puerta_recibidos | 0 | 0.00% |
| paradas | 0 | 0.00% |
| xgot_en_contra | 0 | 0.00% |
| goles_evitados | 0 | 0.00% |
| xg_en_contra | 0 | 0.00% |
| penales_recibidos | 0 | 0.00% |
| penales_atajados | 0 | 0.00% |
| salidas_exitosas | 16 | 100.00% |
| pases_largos_precisos | 0 | 0.00% |
| fuente_url | 0 | 0.00% |
| fuente | 0 | 0.00% |

### defensa_jugador_partido.csv — 237 filas

| Campo | Filas N/D | % N/D |
|---|---:|---:|
| jornada | 0 | 0.00% |
| jugador | 0 | 0.00% |
| posicion | 0 | 0.00% |
| minutos | 0 | 0.00% |
| duelos_ganados | 14 | 5.91% |
| duelos_totales | 18 | 7.59% |
| duelos_aereos_ganados | 0 | 0.00% |
| duelos_aereos_totales | 0 | 0.00% |
| recuperaciones | 0 | 0.00% |
| intercepciones | 0 | 0.00% |
| despejes | 0 | 0.00% |
| bloqueos_de_tiro | 0 | 0.00% |
| entradas_ganadas | 237 | 100.00% |
| entradas_totales | 0 | 0.00% |
| faltas_cometidas | 0 | 0.00% |
| faltas_recibidas | 122 | 51.48% |
| perdidas_de_balon | 237 | 100.00% |
| fuente_url | 0 | 0.00% |
| fuente | 0 | 0.00% |

### posicion_rol_partido.csv — 176 filas

| Campo | Filas N/D | % N/D |
|---|---:|---:|
| jornada | 0 | 0.00% |
| jugador | 0 | 0.00% |
| formacion_inicial | 0 | 0.00% |
| posicion_en_formacion | 1 | 0.57% |
| minuto_entrada | 176 | 100.00% |
| minuto_salida | 99 | 56.25% |
| motivo_salida | 172 | 97.73% |
| fuente_url | 0 | 0.00% |
| fuente | 0 | 0.00% |

### disponibilidad_jugadores.csv — 12 filas

| Campo | Filas N/D | % N/D |
|---|---:|---:|
| jornada_inicio | 0 | 0.00% |
| jornada_fin | 4 | 33.33% |
| jugador | 0 | 0.00% |
| tipo | 0 | 0.00% |
| detalle | 0 | 0.00% |
| fuente_url | 0 | 0.00% |
| fuente | 0 | 0.00% |

### construccion_jugador_partido.csv — 253 filas

| Campo | Filas N/D | % N/D |
|---|---:|---:|
| jornada | 0 | 0.00% |
| jugador | 0 | 0.00% |
| posicion | 0 | 0.00% |
| minutos | 0 | 0.00% |
| pases_completados | 0 | 0.00% |
| pases_intentados | 0 | 0.00% |
| pases_largos_precisos | 60 | 23.72% |
| pases_progresivos | 253 | 100.00% |
| pases_clave | 253 | 100.00% |
| ocasiones_creadas | 16 | 6.32% |
| grandes_ocasiones_creadas | 233 | 92.09% |
| xa | 78 | 30.83% |
| conducciones_progresivas | 253 | 100.00% |
| regates_exitosos | 144 | 56.92% |
| toques_area_rival | 16 | 6.32% |
| centros_precisos | 149 | 58.89% |
| fuente_url | 0 | 0.00% |
| fuente | 0 | 0.00% |

## Cobertura de disponibilidad y vacíos pendientes

La columna «sin convocatoria» indica ausencia de la alineación y del banco de FotMob, no su causa. Las jornadas anteriores a la incorporación de Cáseres o Lozano no se cuentan como lesiones. Se incluyen los once nombres pedidos y los demás jugadores que fueron titulares al menos una vez en la base.

| Jugador, nombre exacto | Jornadas sin participación | De ellas, sin convocatoria | Filas de eventos documentados |
|---|---|---|---:|
| Carlos Acevedo | Ninguna | Ninguna | 0 |
| Felipe Sánchez | Ninguna | Ninguna | 0 |
| Franco Pardo | 7 | Ninguna | 0 |
| Efraín Orona | 1, 2, 3, 5, 9, 14, 15, 16 | 14, 15, 16 | 3 |
| Diego González | 12, 15, 16 | 15, 16 | 1 |
| Facundo Cáseres | 1, 2, 3, 4, 5, 6, 7 | 1, 2, 3, 4, 5, 6, 7 | 0 |
| Tahiel Jiménez | 1, 2, 3, 5, 6, 7, 8, 9, 10 | 1, 2, 3, 5, 6, 7, 9 | 1 |
| Esteban Lozano | 1, 2, 3, 4, 5, 6, 12 | 1, 2, 3, 4, 5, 6 | 0 |
| Ezequiel Bullaude | Ninguna | Ninguna | 0 |
| Eduardo Aguirre | 14 | Ninguna | 2 |
| Fran Villalba | Ninguna | Ninguna | 0 |
| Aldo López | 8, 9 | 8, 9 | 0 |
| Carlos Gruezo | 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 | 1 |
| Emmanuel Echeverría | 1 | 1 | 0 |
| Javier Abella | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16 | Ninguna | 0 |
| Jonathan Pérez | 1, 2, 3, 4, 5, 8, 11 | 2, 3 | 2 |
| Kevin Palacios | 1, 2, 12, 13, 14 | 1, 2, 12 | 0 |
| Lucas Di Yorio | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | 2 |
| Luis Gómez | 1, 2, 3, 4, 5, 10, 11, 15 | 1, 2, 3, 4, 5, 11 | 0 |
| Mauricio Cuevas | Ninguna | Ninguna | 0 |
| Ramiro Sordo | 9, 12, 13, 15, 16 | 13 | 0 |
| Salvador Mariscal | 6, 8, 10, 11, 12, 13, 14, 15, 16 | 10 | 0 |

**Causas no verificadas:** por ejemplo, Aldo López no figura en convocatoria en J8–J9 y Kevin Palacios no figura en J12; no se obtuvo evidencia suficiente para clasificarlos como lesionados, suspendidos o convocados a selección. Pardo no juega J7, pero está en el banco; Aguirre no juega J14, pero también está convocado. Esos hechos no se convierten en bajas médicas. Las ausencias restantes sin evento documentado se mantienen como vacíos de contexto.

Los intervalos y las reapariciones no deben sumarse como si fueran bajas independientes ni transformarse en una variable binaria sin leer `detalle`: incluyen lesiones durante el juego, regresos al banquillo y disponibilidad parcial.
