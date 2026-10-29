# 06 · Impacto, dificultades y aprendizajes

> **No se inventan porcentajes, ahorros ni métricas.** Los impactos son **esperados** [PROPUESTA]. Las cifras que aparecen son la **situación actual verificada** (la línea base), no resultados del chatbot.

---

## 1. Impacto esperado

| Para quién | Beneficio esperado [PROPUESTA] | Base verificada que lo justifica |
|---|---|---|
| **DanuStore (socio formador)** | Comprar según la venta real y no según un pronóstico inflado | Lo esperado es ≈ 5.9 veces lo vendido; el WAPE actual es ≈ 468–489 % y el del modelo es de 5.98 % |
| | Liberar inventario en las regiones con exceso | Cobertura de 301 a 478 días en Bajío, Noroeste, Sur y Sureste |
| | Planear la temporada | Noviembre y diciembre +22 % y febrero −15 %, contra un plan plano |
| **Carlos (planeador)** | Saber cuánto pedir sin armar Excel a mano | Su frustración está documentada (F9) |
| **Laura (gerente regional)** | Alertas y propuestas de traslado para su región | Sureste: 478 días y 6.7 % de cumplimiento |

### Procesos que facilita [PROPUESTA]
1. La planeación mensual de compras (pedido sugerido).
2. La detección de sobrestock y de riesgo de faltante (semáforo).
3. La redistribución entre regiones (propuesta → aprobación humana).
4. El reporte mensual de cobertura y del error del pronóstico.

### Mejoras de eficiencia y beneficios operativos posibles [PROPUESTA, sin cuantificar]
- Menos tiempo armando reportes. **No hay una medición del tiempo actual**: el diseño original ponía la meta de "reducirlas a la mitad" sin tener la línea base, así que **no debe presentarse como dato**.
- Decisiones uniformes entre regiones, porque todas usan la misma regla de cobertura.
- Menos capital inmovilizado. **No es cuantificable porque no hay costos.**

## 2. Indicadores para medir el impacto

| Indicador | Fórmula | Línea base verificada | Meta |
|---|---|---|---|
| Días de cobertura | inventario ÷ venta diaria | ≈ 208 en total; de 113 (CDMX) a 478 (Sureste) | Acercarse a 60–90 (referencia de la industria). **No hay meta numérica aprobada** |
| Cumplimiento | vendido ÷ esperado | 17.0 % | Por definir con DanuStore |
| Error del pronóstico (WAPE) | Σ\|real − pronóstico\| ÷ Σ real | 467.95 % (actual) contra 5.98 % (modelo, prueba de 2025) | Que el monitoreo con datos nuevos no supere el error de validación. **Por definir** |
| Rotación | ventas anuales ÷ inventario promedio | ≈ 1.8 | Industria: de 4 a 6 |
| Brecha regional | cobertura máxima − cobertura mínima | 478 − 113 = 365 días | Por definir |
| Uso del chatbot | consultas, alertas atendidas, propuestas aprobadas | **No existe** (no hay chatbot) | Por definir |
| Tiempo en reportes | horas por semana | **No medido** | Por definir |

## 3. Dificultades reales y soluciones aplicadas (documentadas)

| # | Problema real | Solución aplicada | Fuente |
|---|---|---|---|
| 1 | Variables con fuga de información (acumulados, cumplimiento y cobertura del mismo mes) | Se excluyeron del modelo | Notebook §3.2 |
| 2 | `static_price` funcionaba como identificador del producto, así que el modelo podía memorizar | Se excluyó. Con precio, el WAPE baja de 5.98 % a 5.87 %; se documentó la diferencia | Notebook §12; revisión externa (F9) |
| 3 | Al principio, el periodo de prueba se usó para escoger los hiperparámetros | Se agregó una validación de mayo a agosto de 2025 con selección automática | Notebook §10.1 |
| 4 | 2025 repite a 2024 (76.6 % de los registros idénticos) y los resultados son optimistas | Se agregó el ingenuo estacional como línea base y se excluyó `ventas_hace_12`. Se reporta como limitación | Notebook §7.1 y §14 |
| 5 | El error a varios meses no estaba medido | Se agregó un pronóstico recursivo de 4 meses (5.83 % → 12.26 %; bloque de 9.91 %) | Notebook §13 |
| 6 | Las gráficas usaban otra partición que la mejor (70/30 contra 80/20) | Se unificó todo en 80/20 | Historial de commits |
| 7 | El código era demasiado complejo para un nivel de principiante | Se simplificó (sin lambda ni `**config`) | Commit 48eb5ff |
| 8 | La investigación recomendaba XGBoost, pero los datos dieron a Random Forest como el mejor | Se eligió Random Forest con la evidencia ejecutada | F1 contra F5 |
| 9 | El chatbot se diseñó primero para clientes, lo que no resolvía el reto | Se rediseñó como un asistente interno de inventario | F9 |
| 10 | Las cifras de cobertura difieren según el método (109/111/113 y 472/478/490) | Se documentó el método. **Falta unificarlo en la presentación** | Documento 07, C2 |

## 4. Aprendizajes técnicos (sustentados en lo anterior)

- En series de tiempo, **la partición debe ser temporal** y los hiperparámetros se eligen con validación, no con la prueba.
- **Una buena métrica necesita una buena línea base:** el ingenuo estacional reveló el problema de calidad de los datos.
- **Crear variables (rezagos) importó más que el algoritmo:** el error baja de 22.65 % a 5.98 %.
- El error crece con el horizonte. Por eso un chatbot debe citar el error que corresponde al plazo que se pregunta.
- **Un chatbot solo es útil si se conecta con el problema real.** El rediseño de clientes a inventario lo demuestra.

## 5. Reflexiones que todavía necesita aportar el equipo [PENDIENTE]

- Qué aprendió cada integrante y cómo se repartió el trabajo del chatbot.
- La opinión del socio formador sobre la propuesta (no está documentada).
- La experiencia real con Google AI Studio, una vez que se pruebe.
- Si DanuStore usaría el chatbot y qué datos podría entregar (tiendas, tiempo de reposición, costos).
