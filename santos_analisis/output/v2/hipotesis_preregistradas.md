# Hipótesis y reglas de decisión (escritas antes de calcular resultados v2)

Fecha: 2026-11-20. Este archivo se confirma en git **antes** de ejecutar `src/analisis_v2.py`.

**Qué ya había visto al escribirlo (para ser transparente):**
- Los resultados del informe v1: npxG en contra 1.41 → 1.24, tiros a puerta del rival 6.6 → 3.3, y 3 goles sin penal recibidos con 7.4 npxG en contra en J8–J13.
- Las filas crudas de `portero_partido.csv`, que leí para validarlo (16 filas visibles a simple vista).

No había calculado agregados, intervalos ni descomposiciones con los datos nuevos. No se añadirán hipótesis sin avisar.

## Bloques y reglas comunes

- **Bloques:** J1–J7, J8–J13, J14–J16 y J8–J16.
- **Intervalos:** bootstrap percentil de partidos dentro de cada bloque (10 000 remuestreos, semilla 20261120). IC95 para diferencias. Las razones (por ejemplo, xGOT/xG o duelos ganados/totales) se calculan como **razón de sumas** dentro de cada remuestreo.
- **Sensibilidad obligatoria** para el estadístico principal de cada hipótesis:
  - Cortes alternativos: el bloque "después" empieza en J7, J8 o J9 y termina en J13.
  - Excluir de uno en uno cada partido de J8–J13 (leave-one-out).
  - Si el veredicto cambia por alguna de estas variantes, el informe lo dice.
- **N/D:** nunca se imputa, no cuenta como cero y no se suma como cero. Las filas con N/D en un campo quedan fuera de los cálculos de ese campo, **y sus minutos también salen del denominador por 90**. Cada prueba informa cuántas filas usó y cuántas excluyó.
- **Columnas prohibidas** (100 % N/D o muy incompletas): entradas_ganadas, perdidas_de_balon, pases_progresivos, pases_clave, conducciones_progresivas, salidas_exitosas, grandes_ocasiones_creadas, regates_exitosos, centros_precisos y faltas_recibidas.
- **Tasa de paradas:** nunca se calcula con J6 ni J15 (inconsistencias conocidas). El xGOT y los goles evitados sí se usan en esas jornadas.

## H1. El sobre-rendimiento defensivo de J8–J13 se debe a paradas de Acevedo, no solo a mala definición rival

La brecha entre el xG en contra y los goles recibidos se divide en dos partes:
- **xG − xGOT:** calidad o colocación de los remates rivales ("definición rival").
- **xGOT − goles = goles evitados:** paradas.

Se calcula en dos versiones: (a) completa, con penales; (b) excluyendo los partidos con penal en contra (J4 y J8).

- **Apoyada:** en J8–J13, goles evitados > 0 con IC95 que excluye 0 **y** las paradas aportan ≥ 50 % de la brecha.
- **Refutada:** goles evitados ≤ 0 en J8–J13, **o** las paradas aportan ≤ 25 % de la brecha y la relación xGOT/xG baja respecto a J1–J7.
- **No concluyente:** cualquier otro caso.

Se compara también con J1–J7, J14–J16 y J8–J16 (siempre el mismo portero).

## H2. La defensa mejoró de verdad en J8–J13

Se usan los jugadores con `posicion` Defensa o Mediocampista en `defensa_jugador_partido.csv`.

- **Resultado defensivo:** npxG en contra por partido y tiros a puerta del rival por partido (de la base).
- **Ejecución:** % de duelos ganados y % de duelos aéreos ganados (razón de sumas; las filas con duelos N/D quedan fuera).
- **Volumen** (solo descriptivo, no decide el veredicto): recuperaciones, intercepciones, despejes y bloqueos, por 90, por tiro rival y por cada 10 puntos de posesión rival.

Reglas de decisión:
- **Apoyada:** al menos un indicador de resultado mejora con IC95 que excluye 0, **y** al menos un indicador de ejecución mejora con IC95 que excluye 0, **y** la dirección se mantiene con los cortes J7 y J9.
- **Refutada:** ninguno de los dos indicadores de resultado mejora en la estimación puntual, **o** ambos indicadores de ejecución empeoran.
- **No concluyente:** el resto.

Además: descomposición de cada tasa en "mismos jugadores" (≥ 90 minutos en ambos bloques) y "cambio de nombres o de mezcla de minutos" (shift-share).

## H3. La mejora de los mismos jugadores viene de una mejor construcción

- **Grupo:** jugadores de campo con ≥ 90 minutos en J1–J7 y ≥ 90 minutos en J8–J13.
- **Principales:** ocasiones_creadas por 90 y toques_area_rival por 90 (agregado del grupo).
- **Secundarias** (solo descriptivas): % de pases completados, pases_largos_precisos por 90 y xA por 90 (solo filas con dato).

Reglas de decisión:
- **Apoyada:** las dos principales suben con IC95 que excluye 0 y se mantienen con los cortes J7 y J9.
- **Refutada:** las dos principales no suben (estimación puntual ≤ 0).
- **No concluyente:** el resto.

Los pases progresivos y las conducciones progresivas **no se pueden medir** con estos datos.

## H4. El cambio de formación y roles coincide con los cambios de rendimiento (descriptiva)

- Roles por jugador, jornada y formación.
- Rendimiento por formación **siempre separado por local y visita**.
- "central" no distingue lado; minuto_entrada no se usa; motivo_salida=lesion no se usa para inferir cambios tácticos.

Reglas de decisión:
- **Apoyada (descriptivamente):** el cambio de formación ocurre en la ventana del quiebre (J7–J9) **y**, dentro de la misma localía, las formaciones nuevas muestran mejor diferencia de npxG que la anterior.
- **Refutada:** el cambio no coincide con la ventana **y** no hay diferencia, o la diferencia va al revés, dentro de la misma localía.
- **No concluyente:** el resto (por ejemplo, si no se puede comparar dentro de la misma localía).

## H5. La caída de J14–J16 se asocia a las bajas de Orona y Diego González

- Quién jugó cada partido se toma de la tabla "jornadas sin participación" del README de datos.
- **Orona:** sin participación en J1, 2, 3, 5, 9, 14, 15 y 16. J13 se marca como "parcial" (salió lesionado al 21).
- **Diego González:** sin participación en J12, 15 y 16. En J14 jugó lesionado.
- Se compara la diferencia de npxG por partido con y sin cada jugador, en J1–J13 (fuera de la caída) y en J1–J16.

Reglas de decisión:
- **Consistente:** en J1–J13, los partidos sin el jugador tienen peor diferencia de npxG (estimación puntual) que los partidos con él.
- **No consistente:** en J1–J13, los partidos sin el jugador son iguales o mejores.
- **Tope del veredicto:** por diseño, como máximo "consistente / no concluyente". No puede quedar "apoyada" con 3 partidos.

## Actualización de la descomposición

- Solo se modifica la descomposición de v1 si H1 o H2 lo justifican.
- Los 7.4 puntos de sobre-rendimiento se desglosarán en cadena, partiendo de los xPts con npxG:
  1. Penales (xPts con xG total).
  2. Definición de Santos (goles reales a favor frente a xG).
  3. Colocación de los remates rivales (xGOT frente a xG en contra).
  4. Paradas (goles frente a xGOT).
- Se reportan dos órdenes del desglose y su promedio.
- Lo que no se pueda atribuir se declara "sin explicar".
