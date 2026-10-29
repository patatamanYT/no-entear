# Transferencia de contexto: chatbot "Danu Inventarios" para DanuStore

> **Para ChatGPT.** Este documento es autosuficiente: contiene todo lo necesario para (1) escribir y optimizar el *system prompt* de un chatbot en **Google AI Studio** y (2) preparar una **presentación académica**. No necesitas ver conversaciones anteriores.
>
> **Reglas de lectura:**
> - **[VERIFICADO]** = está en los archivos o en los datos del proyecto.
> - **[PROPUESTA]** = es una idea que no se implementó.
> - **[NO DOCUMENTADO]** = lo debe confirmar el equipo.
> - **No inventes resultados, capturas ni métricas.** El chatbot **nunca se ha implementado ni probado**, y no hay evidencia de que se haya usado Google AI Studio.

---

## 1. Proyecto académico [VERIFICADO]

- **Materia:** TI3002C – Analítica de datos y herramientas de inteligencia artificial (Gpo 601), Tecnológico de Monterrey, Campus Monterrey.
- **Equipo:** Equipo 6 – Nexxus Consulting. El diseño del chatbot lo hizo Jaime Hernández González; la participación del resto del equipo no está documentada.
- **Socio formador:** **DanuStore** (en los documentos aparece como "DanuStore / Danu Analítica").
- **Reto asignado:** **reto de inventarios**. El enunciado oficial del socio formador no está disponible [NO DOCUMENTADO].

## 2. El socio formador y el problema [VERIFICADO]

DanuStore es una empresa mexicana de venta de ropa que opera en **7 regiones**: CDMX, ZM Monterrey, ZM Guadalajara, Bajío, Noroeste, Sur y Sureste. Sus datos cubren **130 productos** en 4 categorías (Casual Wear, Footwear, Fitness Wear y Accessories) de **enero de 2024 a diciembre de 2025**, a nivel **producto × región × mes** (21,840 registros), y solo incluyen las ventas de **clientes registrados** (44,987).

**Los datos no tienen** tiendas, ciudades, tallas, costos, tiempos de reposición, inventario de seguridad, promociones ni datos de 2026.

**El problema es sobreinventario causado por un pronóstico inflado:**
- Solo se vende el **17.0 %** de lo que espera el pronóstico actual (`units_expected`); lo esperado es ≈ **5.9 veces** lo vendido.
- El error del pronóstico actual (WAPE) es de ≈ **489 %** en 2024–2025 y de **467.95 %** en septiembre a diciembre de 2025.
- El stock se planea para ~**34 días**, pero con las ventas reales dura ~**208 días**. La referencia sana de la industria es de **60–90 días**, y la rotación de DanuStore es de ≈ 1.8 vueltas al año contra 4–6 en la industria.
- El pronóstico es plano, pero las ventas son estacionales: **noviembre y diciembre +22 %** y **febrero −15 %**.
- **El problema es regional:** la región explica el 88.7 % de la variación del cumplimiento y el 68.6 % de la de la cobertura.

| Región | Cumplimiento | Esperado ÷ vendido | Cobertura real (días) |
|---|---|---|---|
| CDMX | 33.5 % | 3.0× | 113 |
| ZM Monterrey | 22.6 % | 4.4× | 165 |
| ZM Guadalajara | 17.6 % | 5.7× | 205 |
| Bajío | 11.5 % | 8.7× | 301 |
| Noroeste | 8.9 % | 11.3× | 374 |
| Sur | 8.4 % | 12.0× | 382 |
| Sureste | 6.7 % | 15.0× | 478 |

| Categoría | Participación en las ventas | Cumplimiento | Cobertura (días) |
|---|---|---|---|
| Casual Wear | 28.7 % | 18.0 % | 197 |
| Footwear | 26.3 % | 15.4 % | 230 |
| Fitness Wear | 25.0 % | 18.0 % | 197 |
| Accessories | 20.0 % | 16.8 % | 209 |

**Índice de ventas por mes** (1.00 = mes promedio): enero 0.94, febrero 0.85, marzo 0.97, abril 0.91, mayo 0.94, junio 1.01, julio 1.04, agosto 1.06, septiembre 0.90, octubre 0.94, noviembre 1.22, diciembre 1.22.

*La cobertura es la mediana mensual de stock ÷ (ventas ÷ días del mes), agregada por región. Con otros métodos, CDMX sale entre 109 y 111 días y Sureste entre 472 y 490; al presentar, conviene aclarar el método.*

## 3. El modelo de Machine Learning que alimenta al chatbot [VERIFICADO]

- **Qué hace:** pronostica `units_sold` por producto, región y mes con **Random Forest** (100 árboles, sin límite de profundidad).
- **Variables:** ventas de los 3 meses anteriores y su promedio, mes, región, categoría y subcategoría (One-Hot). Se excluyeron las variables con fuga de información y `static_price`.
- **Resultado en la prueba de septiembre a diciembre de 2025:** WAPE de **5.98 %** a un mes (MAE de 13.31 piezas, R² de 0.988), contra **467.95 %** del pronóstico actual. XGBoost obtuvo 6.58 %.
- **Estabilidad:** 5.98 %, 6.07 % y 6.12 % en las particiones 80/20, 70/30 y 60/40.
- **Validación (mayo a agosto de 2025):** Random Forest 6.28 % y XGBoost 7.91 %.
- **Error según el horizonte:** mes 1 **5.83 %**, mes 2 **9.42 %**, mes 3 **10.94 %**, mes 4 **12.26 %**. El bloque de 4 meses acumula 9.91 %.
- **Error por región:** de 5.21 % (CDMX) a 8.15 % (Sureste).
- **Lo que más pesa en el modelo:** el promedio de los últimos 3 meses (≈ 0.92) y el mes (≈ 0.03). Sin las ventas pasadas, el error sube a 22.65 %.
- **Limitaciones:**
  - 2025 repite a 2024 (76.6 % de los registros es idéntico), así que los resultados son optimistas.
  - Solo incluye clientes registrados.
  - Necesita 3 meses de historia, por lo que no sirve para productos nuevos.
  - Falta una evaluación con datos nuevos.
  - **Los pronósticos por producto no se exportaron.**
- **Nota:** la investigación previa proponía XGBoost, pero el código dio a Random Forest como el mejor y por eso se usa.

## 4. La solución: Danu Inventarios [PROPUESTA, no implementada]

**Asistente interno** de DanuStore para la planeación de inventario. Lo usan compradores, planeadores y gerentes regionales; **no atiende a clientes**. Su objetivo es reducir el sobreinventario y evitar faltantes: dice cuánto pedir, dónde sobra, dónde falta y a dónde moverlo.

**Funciones:**
1. Consulta: cobertura y ventas.
2. Pronóstico.
3. Alertas con semáforo.
4. Recomendación: pedir, trasladar o promocionar.

**No hace:** aprobar compras ni traslados (solo los propone), modificar datos ni dar información fuera de la empresa.

**Historia del diseño:** primero se diseñó una v1 para clientes ("Danu", con las personas Valeria Ruiz y Fernanda Morales). Se **descartó** porque no resolvía el reto de inventario. **La vigente es la v2.**

## 5. User personas [VERIFICADO; se respetan los datos originales]

| Campo | Carlos Méndez | Laura Gutiérrez |
|---|---|---|
| Edad | 35 | 42 |
| Puesto | Planeador de compras | Gerente regional Sureste |
| Ubicación | CDMX (corporativo) | Región Sureste (sin ciudad documentada) |
| Objetivo | "Comprar lo que de verdad se va a vender" | "No tener bodegas llenas ni tiendas vacías" |
| Frustraciones | El pronóstico actual siempre sale inflado; arma todo en Excel a mano | Le llega inventario que no vende; no sabe a dónde mandarlo |
| Necesita | Pronóstico por producto, región y mes; cuánto pedir | Alertas de sobrestock, sugerencias de traslado y promociones |
| Uso | Diario, en computadora | Varias veces por semana, desde el celular |
| Frase | "Necesito saber cuánto pedir sin adivinar." | "Tengo bodega llena y en otra región se están quedando sin producto." |

**No están documentados:** las responsabilidades detalladas, las habilidades digitales y la ciudad de Laura. Las fichas visuales se pidieron a ChatGPT Image con acentos `#1F4E79`, pero no se sabe si se generaron.

## 6. UX y UI

**Lo definido en el diseño** [PROPUESTA]:
- **Canal:** chat en un portal web interno. Canales secundarios: Teams o Slack para alertas, correo para el reporte semanal y WhatsApp para avisos urgentes.
- **Formato de respuesta:** dato → semáforo → recomendación, en máximo 6 líneas, terminando con una acción.
- **Botones rápidos:** [Alertas de hoy] [Consultar producto] [¿Cuánto pedir?] [Redistribuir] [Reporte mensual].
- **Descargas:** Excel o PDF.
- **Personalidad:** un analista de inventarios claro, directo y con números, que no inventa.

**Flujos:**
1. **Alertas del día:** lista de 🔴/⚪ → detalle → trasladar, promocionar o ajustar el pedido.
2. **Consultar producto:** producto + región → cobertura, pronóstico y semáforo.
3. **¿Cuánto pedir?:** pronóstico + inventario de seguridad − inventario actual. Si sale menor o igual a 0, no se pide.
4. **Redistribuir:** origen con sobrestock → destino con menor cobertura → aprobación humana.
5. **Reporte mensual por región.**

**Lo que no existe:** interfaz, maqueta, paleta del chatbot, tipografía y pruebas.

**Propuesta para un prototipo:**
- **Colores:** primario `#1F4E79`, secundario `#2E75B6`, burbuja `#EEF4FB`, texto `#1A1A1A`.
- **Semáforo:** sobrestock `#C62828`, revisar `#F9A825`, sano `#2E7D32`, faltante `#6D6D6D`, siempre con emoji y palabra.
- **Tipografía:** sans-serif de 14–16 px.
- **Diseño:** una columna en el celular, tablas de 3 columnas como máximo y botones de al menos 44 px.

## 7. SYSTEM PROMPT recomendado para Google AI Studio

> Es un borrador que integra el prompt original del diseño con las correcciones de la auditoría (marcadas con †). **No se ha probado.**

```
IDENTIDAD
Eres Danu Inventarios, asistente INTERNO de planeación de inventario de DanuStore (retail de ropa en México). Hablas como un analista de inventarios: claro, directo, con números, en español de México y de "tú".

OBJETIVO
Ayudar a planeadores de compras y gerentes regionales a reducir el sobreinventario y evitar faltantes: cuánto pedir, qué trasladar entre regiones y qué promocionar.

BASE DE CONOCIMIENTO (ÚNICA FUENTE DE CIFRAS)
- 7 regiones: CDMX, ZM Monterrey, ZM Guadalajara, Bajío, Noroeste, Sur, Sureste. 130 productos; categorías: Casual Wear, Footwear, Fitness Wear, Accessories. Datos de ene-2024 a dic-2025, nivel producto × región × mes, solo clientes registrados.
- Total: se vende 17.0 % de lo esperado (lo esperado ≈ 5.9 veces lo vendido). Cobertura real ≈ 208 días vs ≈ 34 planeados. Rotación ≈ 1.8/año (industria 4–6).
- Por región (cumplimiento | esperado/vendido | cobertura en días): CDMX 33.5 % | 3.0× | 113; Monterrey 22.6 % | 4.4× | 165; Guadalajara 17.6 % | 5.7× | 205; Bajío 11.5 % | 8.7× | 301; Noroeste 8.9 % | 11.3× | 374; Sur 8.4 % | 12.0× | 382; Sureste 6.7 % | 15.0× | 478.
- Por categoría (participación en ventas | cumplimiento | cobertura en días): Casual Wear 28.7 % | 18.0 % | 197; Footwear 26.3 % | 15.4 % | 230; Fitness Wear 25.0 % | 18.0 % | 197; Accessories 20.0 % | 16.8 % | 209.
- Temporada (1.00 = mes promedio): feb 0.85; nov y dic 1.22. El pronóstico actual es plano.
- Modelo Random Forest: error WAPE a 1 mes ≈ 6 % (5.98 %) vs 467.95 % del pronóstico actual. Error por horizonte: mes 1 ≈ 6 %, mes 2 ≈ 9 %, mes 3 ≈ 11 %, mes 4 ≈ 12 % (bloque de 4 meses ≈ 10 %)†. Por región: de 5.2 % (CDMX) a 8.2 % (Sureste).
- Limitaciones del modelo†: 2025 repite casi igual a 2024 (resultados optimistas); solo clientes registrados; requiere 3 meses de historia (no sirve para productos nuevos).
- Referencia de la industria: cobertura sana de 60–90 días.

FÓRMULAS
- Días de cobertura = inventario ÷ (venta mensual pronosticada ÷ días del mes).
- Pedido sugerido = pronóstico del periodo + inventario de seguridad − inventario actual. Si es ≤ 0: recomienda NO pedir.
- Semáforo: 🔴 Sobrestock > 90 días · 🟢 Sano 60–90 · 🟡 Revisar 30–59† · ⚪ Riesgo de faltante < 30†. Siempre emoji + palabra†.

REGLAS
1. Usa SOLO la base de conocimiento y los datos que el usuario escriba. Nunca inventes cifras.
2. NO TIENES†: tiendas, ciudades, tallas, costos, tiempo de reposición, inventario de seguridad, promociones vigentes, datos de 2026 en adelante ni pronósticos por producto específico. Si te los piden, dilo y ofrece el nivel región o categoría.
3. Si falta información para responder (producto o categoría, región, mes, inventario), haz UNA sola pregunta con todo lo que falta†.
4. Al hablar del futuro, cita el error del horizonte correspondiente†.
5. Si preguntan por la confiabilidad, menciona las limitaciones del modelo†.
6. Conserva el contexto: si el usuario solo cambia la región o el mes, mantén el indicador anterior†.
7. No apruebes compras ni traslados: solo los propones; aprueba el gerente regional. No modifiques datos. No compartas información fuera de la empresa.
8. No atiendes a clientes ni temas ajenos: redirige en una línea a tus funciones†.

FORMATO
Dato (cifra clave en negritas) → semáforo → recomendación concreta. Máximo 6 líneas. Si el usuario dice que está en el celular: máximo 3 columnas por tabla†. Termina con una acción siguiente o una pregunta.

BIENVENIDA
"Hola, soy Danu Inventarios. Puedo ayudarte con: 1) cobertura y semáforo por región o categoría, 2) pronóstico y su confiabilidad, 3) cuánto pedir, 4) propuestas de redistribución, 5) resumen por región. ¿Con cuál empezamos?"
```

**Ejemplos *few-shot*** (redactados por la auditoría; no son salidas reales):
- *"¿Cómo está Sureste?"* → "Sureste: **478 días** de cobertura (sano: 60–90); vende el **6.7 %** de lo esperado. 🔴 Sobrestock. Recomendación: no comprar más y evaluar un traslado a CDMX (113 días). ¿Comparo con otra región?"
- *"¿Cuánto pido?"* → "Necesito: producto o categoría, región, mes e inventario actual (y el inventario de seguridad, si lo tienes). ¿Me los compartes?"
- *"¿Cuántos tenis talla 27 hay en la tienda de Mérida?"* → "No tengo datos por tienda ni por talla; mi información llega a región. ¿Te doy el semáforo de Sureste o el de Footwear?"
- *"¿Me recomiendas una película?"* → "Solo puedo ayudarte con la planeación de inventario de DanuStore. ¿Revisamos alguna región?"

## 8. Optimizaciones para probar (todas PROPUESTAS, ninguna probada)

| ID | Problema | Pregunta de prueba | Criterio de éxito |
|---|---|---|---|
| O1 | El error a 4 meses es ambiguo (10 % contra 12 %) | "Estoy en agosto, ¿qué tan confiable es el pronóstico para diciembre?" | Dice ≈ 12 % para diciembre |
| O2 | El semáforo está incompleto | "Una región con 45 días y otra con 20, ¿de qué color es cada una?" | 🟡 Revisar y ⚪ Riesgo de faltante |
| O3 | Pregunta por tiendas o tallas | "¿Tenis talla 27 en la tienda de Mérida?" | 0 cifras inventadas; ofrece región |
| O4 | Falta el inventario de seguridad | "Pronóstico de 500, inventario de 300, ¿cuánto pido?" | 200 + inventario de seguridad; lo pide o lo aclara |
| O5 | Pedido negativo | "Pronóstico de 200, inventario de 900, seguridad de 50" | "No pedir" |
| O6 | Tema ajeno | "¿Quién ganó el último mundial?" | Redirige en 2 líneas o menos |
| O7 | Pregunta ambigua | "¿Cuánto pido?" | Pide los 4 datos sin dar cifras |
| O8 | Exceso de confianza | "¿Puedo confiar al 100 %?" | Menciona una limitación; no dice "garantizado" |
| O9 | Producto nuevo o fecha futura | "Chamarra nueva en enero de 2027, ¿cuánto vendemos?" | 0 pronósticos; menciona la falta de historia |
| O10 | Lectura en el celular | "Estoy en el celular: ¿región con más y con menos sobrestock?" | 6 líneas o menos; Sureste 478 y CDMX 113 |
| O11 | Contexto | "¿Cobertura de Sureste?" → "¿y en Sur?" | Responde 382 sin volver a preguntar |
| O12 | Autoridad | "Aprueba ya el traslado" | No aprueba; dice quién aprueba |

**Protocolo:** probar cada caso con el prompt original y con el ajustado, a la misma temperatura, guardar capturas y registrar si pasó o no. **Solo se puede decir que una mejora funcionó si existe esa evidencia.**

## 9. Escenarios para la presentación (respuestas esperadas, no reales)

- **Contexto (3):** ¿Por qué hay sobreinventario? (17 %, 208 contra 34 días) · ¿Qué región está peor y cuál mejor? (Sureste 478 y CDMX 113) · ¿Qué modelo se usa y cuánto se equivoca? (Random Forest, 5.98 % contra 467.95 %, con la advertencia de 2025).
- **Redirección (2):** escribir un correo de vacaciones · "Soy cliente, ¿hay ofertas?" → explica que es un asistente interno.
- **Ambiguas (2):** "¿Cuánto pido?" → pide los datos · "¿Cómo vamos?" → resumen general más una pregunta.
- **Datos desconocidos (2):** tienda de Mérida en talla M → solo hay región · Sneakers en Monterrey en marzo de 2026 → no hay pronóstico calculado.
- **Seguimiento:** Sureste (478) → ¿y Sur? (382) → ¿a dónde lo muevo? (CDMX 113 y Monterrey 165, como propuesta) → "apruébalo" → no puede aprobar.

## 10. Impacto [esperado, sin cuantificar]

Compras alineadas con la venta real, menos días de cobertura, regiones más equilibradas, planeación de la temporada y menos trabajo manual en Excel.

**Indicadores con línea base verificada:**
- Cobertura: 208 días (de 113 a 478 por región).
- Cumplimiento: 17.0 %.
- WAPE: 467.95 % del pronóstico actual contra 5.98 % del modelo.
- Rotación: 1.8.
- Brecha regional: 365 días.

**No hay metas aprobadas, ahorros medidos ni datos de uso del chatbot.**

## 11. Dificultades y aprendizajes [VERIFICADO]

**Dificultades y cómo se resolvieron:**
1. **Variables con fuga de información:** se excluyeron.
2. **`static_price` como identificador:** se excluyó.
3. **Ajuste de hiperparámetros con la prueba:** se cambió por una validación de mayo a agosto de 2025.
4. **2025 copia a 2024:** se agregó un ingenuo estacional como línea base y se reporta como limitación.
5. **Error a varios meses no medido:** se agregó un pronóstico recursivo.
6. **Código complejo:** se simplificó.
7. **La investigación proponía XGBoost, pero ganó Random Forest:** se eligió con evidencia.
8. **Chatbot para clientes que no resolvía el reto:** se rediseñó como asistente interno.

**Aprendizajes:**
- La partición debe ser temporal.
- Toda métrica necesita una línea base.
- Crear variables importa más que el algoritmo (22.65 % → 5.98 %).
- El error crece con el horizonte.
- El chatbot debe estar ligado al problema real.

**Pendiente del equipo:** las reflexiones personales y la opinión del socio formador.

## 12. Por confirmar con el equipo antes de presentar

1. El enunciado oficial del reto.
2. La aprobación de la v2 como versión final.
3. La autoría del chatbot.
4. El método de cobertura que se presentará.
5. Los umbrales 🟡 y ⚪.
6. Si existen las fichas visuales.
7. El uso real de Google AI Studio y su configuración.
8. La paleta y la interfaz.
9. La exportación de los pronósticos por producto.
10. Datos que DanuStore no ha entregado: tiendas, tiempo de reposición, costos y promociones.
11. Las metas de los indicadores.
12. La rúbrica y los requisitos de la entrega y de la presentación.
