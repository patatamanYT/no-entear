# 02 · User personas, UX y UI

> Etiquetas: **[VERIFICADO]**, **[INFERENCIA]**, **[PROPUESTA]** y **[NO DOCUMENTADO]**. Las fuentes se describen en `07_FUENTES_Y_PENDIENTES.md`.
>
> **Aviso general:** el chatbot **no está implementado**. No existen pantallas, prototipos ni capturas. Todo lo de UX y UI que aparece aquí es **diseño en texto** (F9) o una **propuesta nueva de esta auditoría**, y se indica en cada caso.

---

## 1. User personas (versión vigente: Danu Inventarios)

Fuente: F9, la tabla "2. User persona" del diseño "Danu Inventarios" y los prompts para generar las fichas en ChatGPT Image. Los datos se transcriben **sin agregar nada**.

### 1.1 Carlos Méndez

| Campo | Dato original | Estado |
|---|---|---|
| Nombre | Carlos Méndez | [VERIFICADO] |
| Edad | 35 años | [VERIFICADO] |
| Ocupación | Planeador de compras | [VERIFICADO] |
| Ubicación | CDMX (corporativo) | [VERIFICADO] |
| Responsabilidades | No se documentaron. Se infiere del puesto que planea las compras de producto | [NO DOCUMENTADO] / [INFERENCIA] |
| Necesidades ("qué necesita del bot") | Pronóstico por producto, región y mes; saber cuánto pedir | [VERIFICADO] |
| Frustraciones | "El pronóstico actual siempre sale inflado"; "arma todo en Excel a mano" | [VERIFICADO] |
| Objetivo | "Comprar lo que de verdad se va a vender" | [VERIFICADO] |
| Habilidades digitales | No se documentaron. Usa Excel ("arma todo en Excel a mano") y computadora a diario | [NO DOCUMENTADO] / [INFERENCIA] |
| Uso del chatbot | Diario, en computadora | [VERIFICADO] |
| Frase | "Necesito saber cuánto pedir sin adivinar." | [VERIFICADO] |
| Escenario de uso | Pregunta "¿Cuánto pido de sneakers para diciembre en Monterrey?" y luego "¿Y dónde sobra?" (es el script de ejemplo del diseño; ver la sección 2.3) | [VERIFICADO] (ejemplo de diseño, no un uso real) |

### 1.2 Laura Gutiérrez

| Campo | Dato original | Estado |
|---|---|---|
| Nombre | Laura Gutiérrez | [VERIFICADO] |
| Edad | 42 años | [VERIFICADO] |
| Ocupación | Gerente regional Sureste | [VERIFICADO] |
| Ubicación | Región Sureste. No se documentó la ciudad | [VERIFICADO] (región) / [NO DOCUMENTADO] (ciudad) |
| Responsabilidades | No se documentaron. Se infiere del puesto que gestiona el inventario y las tiendas de su región | [NO DOCUMENTADO] / [INFERENCIA] |
| Necesidades | Alertas de sobrestock, sugerencias de traslado y promociones | [VERIFICADO] |
| Frustraciones | "Le llega inventario que no vende"; "no sabe a dónde mandarlo" | [VERIFICADO] |
| Objetivo | "No tener bodegas llenas ni tiendas vacías" | [VERIFICADO] |
| Habilidades digitales | No se documentaron. Usa el celular varias veces por semana | [NO DOCUMENTADO] / [INFERENCIA] |
| Uso del chatbot | Varias veces por semana, desde el celular | [VERIFICADO] |
| Frase | "Tengo bodega llena y en otra región se están quedando sin producto." | [VERIFICADO] |
| Escenario de uso | No hay un script propio. Le corresponden los flujos "Alertas del día" y "Redistribuir" (sección 2.2) | [INFERENCIA] |

**Coherencia con los datos.** La frustración de Laura coincide con el diagnóstico verificado: Sureste tiene la mayor cobertura (478 días) y el menor cumplimiento (6.7 %).

### 1.3 Material visual de las personas

- Se entregaron **dos prompts** para que ChatGPT Image generara las fichas (16:9, fondo blanco, acentos en azul marino `#1F4E79`, ilustración plana y cuatro tarjetas) [VERIFICADO] F9.
- **No hay evidencia de que las imágenes se hayan generado** ni de cómo quedaron [NO DOCUMENTADO]. Si existen, las tiene el equipo fuera del repositorio.

### 1.4 Personas descartadas (no usar)

Valeria Ruiz (22 años, Silver, ZM Guadalajara) y Fernanda Morales (38 años, Gold, ZM Monterrey) pertenecen a la **v1 para clientes**, que se descartó. Se mencionan solo para dejar el rastro [VERIFICADO] F9.

---

## 2. UX: experiencia y flujos

### 2.1 Punto de entrada y canales

| Elemento | Diseño | Estado |
|---|---|---|
| Canal principal | Chat dentro del **portal web interno** de DanuStore | [PROPUESTA] F9 |
| Canales secundarios | Microsoft Teams o Slack para alertas, correo para el reporte semanal y WhatsApp para avisos urgentes a gerentes | [PROPUESTA] F9 |
| Existencia de un portal interno | No hay evidencia de que DanuStore tenga uno | [NO DOCUMENTADO] |
| Prototipo en Google AI Studio | No hay evidencia | [NO DOCUMENTADO] |

**Para el prototipo académico** [PROPUESTA de esta auditoría]: el punto de entrada sería el chat de Google AI Studio, con el *system prompt* del documento 03 y la base de conocimiento cargada como texto.

### 2.2 Flujos de conversación del diseño [PROPUESTA] F9

1. **Alertas del día:** entrar → lista de productos y regiones en 🔴 o ⚪ → ver detalle → [Trasladar] [Promoción] [Ajustar pedido].
2. **Consultar producto:** producto + región → stock, ventas, días de cobertura y pronóstico → semáforo.
3. **¿Cuánto pedir?:** producto + región + mes → pronóstico − inventario actual + inventario de seguridad = **pedido sugerido**. Si sale negativo, se recomienda no pedir.
4. **Redistribuir:** región con sobrestock → regiones con faltante → propuesta de traslado (producto, piezas, origen y destino) → se envía a aprobación.
5. **Reporte mensual:** resumen por región con la cobertura, el porcentaje vendido de lo esperado y el error del pronóstico.

### 2.3 Mensaje de bienvenida y consultas iniciales

**Diseño original** [PROPUESTA] F9. Las cifras son de ejemplo, no reales:
> **Danu:** Hola Carlos 👋. Hoy hay **12 alertas**: 9 🔴 sobrestock y 3 ⚪ riesgo de faltante.
> [Ver alertas] [Consultar producto] [¿Cuánto pedir?] [Redistribuir] [Reporte]

Los botones rápidos del diseño son **[Alertas de hoy] [Consultar producto] [¿Cuánto pedir?] [Redistribuir] [Reporte mensual]**. El script del diseño usa nombres un poco distintos ([Ver alertas] y [Reporte]), lo cual es una inconsistencia menor.

**Adaptación para Google AI Studio** [PROPUESTA de esta auditoría]: Google AI Studio no muestra botones, así que el menú se escribe como una lista numerada y no se muestran alertas inventadas al inicio:
> Hola, soy **Danu Inventarios**, el asistente de planeación de inventario de DanuStore. Puedo ayudarte con:
> 1. Cobertura y semáforo por región o categoría
> 2. Pronóstico y qué tan confiable es
> 3. Cuánto pedir (necesito producto, región, mes e inventario)
> 4. Propuestas de redistribución entre regiones
> 5. Resumen por región
> ¿Con cuál empezamos?

### 2.4 Preguntas de seguimiento [PROPUESTA de esta auditoría, basada en F9]

- Si falta la región, el producto o la categoría, o el mes: se hace **una sola pregunta** que pida lo que falta.
- Después de responder: se propone **una acción siguiente** ("¿Te armo la propuesta de traslado?"). Esto sí viene del diseño (F9).
- El contexto se conserva: si el usuario dice "¿y en Sur?", se mantiene el producto o la categoría de la pregunta anterior.

### 2.5 Manejo de errores y de datos desconocidos

| Caso | Comportamiento | Estado |
|---|---|---|
| Falta un dato | "Dilo; no inventes cifras" | [VERIFICADO como regla de diseño] F9 |
| Piden una tienda o ciudad | Aclarar que los datos solo llegan a nivel región | [PROPUESTA de esta auditoría] |
| Piden un inventario de seguridad o un tiempo de reposición | Pedir el dato al usuario o calcular sin él y decirlo | [PROPUESTA de esta auditoría] |
| Piden un producto nuevo (menos de 3 meses de historia) | Explicar que el modelo no lo cubre | [PROPUESTA basada en la limitación verificada] |
| Piden un mes de 2026 o posterior | No hay datos ni pronóstico calculado para ese mes | [PROPUESTA de esta auditoría] |

### 2.6 Redirección de temas externos

- Regla del diseño: no dar información a clientes ni compartir información fuera de la empresa [VERIFICADO como regla de diseño] F9.
- Redirección sugerida [PROPUESTA]: "Solo te puedo ayudar con la planeación de inventario de DanuStore. Si quieres, revisamos la cobertura de alguna región."

### 2.7 Cierre de la interacción

- Diseño: cada respuesta termina con una acción ([aprobar] [ver detalle] [descargar]) [PROPUESTA] F9.
- Cierre sugerido [PROPUESTA]: un resumen de una línea con las decisiones que se tomaron y la aclaración de que la aprobación final es de una persona.

---

## 3. UI: interfaz

### 3.1 Lo que existe

**No existe ninguna interfaz implementada.** No hay maquetas en Figma, ni HTML, ni capturas [VERIFICADO: no hay archivos del chatbot en el repositorio].

### 3.2 Lo que se definió en el diseño [PROPUESTA] F9

| Elemento | Definición |
|---|---|
| Formato de respuesta | **Dato corto → semáforo → recomendación** |
| Semáforo | 🔴 sobrestock (más de 90 días) · 🟡 revisar (sin umbral definido) · 🟢 sano (60–90 días) · ⚪ riesgo de faltante (menos que el tiempo de reposición más el inventario de seguridad) |
| Botones rápidos | Los 5 de la sección 2.3 |
| Descargas | Tabla en Excel o PDF |
| Longitud | Máximo 6 líneas por respuesta |
| Personalidad visual | "Como un analista de inventarios: claro, directo y con números" |

### 3.3 Paleta de colores

| Uso | HEX | Origen | Estado |
|---|---|---|---|
| Azul marino (acentos de las fichas de user persona) | `#1F4E79` | Prompts de las personas (F9) y documentos del equipo | [VERIFICADO] (solo en las fichas) |
| Azul medio (encabezados de las tablas de los PDF de estudio) | `#2E75B6` | PDF de estudio `Resumen_Codigo_ML.pdf` y `Guia_presentacion_Codigo_ML.pdf` (F6) | [VERIFICADO] (no es del chatbot) |
| "Azul claro" y "verde azulado" | sin HEX | Prompts de las personas (F9) | [VERIFICADO] (no tienen código) |
| Paleta del chatbot | — | — | [NO DOCUMENTADO] |

**Paleta propuesta** para un prototipo [PROPUESTA de esta auditoría; no se usó en el proyecto]:

| Rol | HEX |
|---|---|
| Primario (encabezado, botones) | `#1F4E79` |
| Secundario (enlaces, foco) | `#2E75B6` |
| Fondo | `#FFFFFF` · burbuja del bot `#EEF4FB` |
| Texto | `#1A1A1A` · texto secundario `#555555` |
| Semáforo: sobrestock | `#C62828` |
| Semáforo: revisar | `#F9A825` |
| Semáforo: sano | `#2E7D32` |
| Semáforo: riesgo de faltante | `#6D6D6D` (con ícono y texto, no solo color) |

### 3.4 Tipografía, distribución, componentes, diseño responsivo y accesibilidad

| Aspecto | Estado | Propuesta (no implementada) |
|---|---|---|
| Tipografía | [NO DOCUMENTADO] para el chatbot. Los PDF de estudio usan Arial | Sans-serif del sistema (Arial o Inter), 14–16 px en el cuerpo |
| Distribución | [NO DOCUMENTADO] | Encabezado con el nombre del bot, área de mensajes, chips de acciones rápidas arriba del campo de texto, botón de enviar |
| Componentes | Botones rápidos y descargas [PROPUESTA] F9 | Chips, tablas compactas, insignia del semáforo con texto ("🔴 Sobrestock") |
| Jerarquía | Dato → semáforo → recomendación [PROPUESTA] F9 | La cifra principal en negritas y la acción al final |
| Diseño responsivo | Implícito, porque Laura lo usa en el celular [INFERENCIA] | Una sola columna; tablas de 3 columnas como máximo en el celular |
| Accesibilidad | [NO DOCUMENTADO] | El semáforo nunca depende solo del color (emoji o ícono + palabra), contraste AA y botones de al menos 44 px |
