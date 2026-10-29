# 01 · Contexto maestro del proyecto

> **Cómo leer este documento.** Cada afirmación lleva una etiqueta:
> - **[VERIFICADO]**: está en un archivo del repositorio, en los datos o en el historial de la conversación, y la cifra se recalculó en esta auditoría cuando fue posible.
> - **[INFERENCIA]**: se deduce de lo verificado, pero no está escrito tal cual.
> - **[PROPUESTA]**: es una idea de diseño que nunca se implementó.
> - **[NO DOCUMENTADO]**: no existe evidencia; lo debe confirmar el equipo.
>
> Las fuentes se identifican con los códigos de `07_FUENTES_Y_PENDIENTES.md` (por ejemplo, F1 o F5).

---

## 1. Datos académicos

| Campo | Valor | Estado |
|---|---|---|
| Materia | TI3002C – Analítica de datos y herramientas de inteligencia artificial (Gpo 601) | [VERIFICADO] F1, F2 |
| Institución | Tecnológico de Monterrey, Campus Monterrey | [VERIFICADO] F1, F2 |
| Equipo | Equipo 6 – Nexxus Consulting | [VERIFICADO] F1, F2 |
| Integrantes (Etapa 4.3) | Aldahir Zarazúa Núñez, Javier Alejandro Padilla Matus, Jaime Hernández González, Felix Samuel Vargas Mar, André Alberto Navarro de la Parra | [VERIFICADO] F2 |
| Docentes | Ildefonso Torres Vargas, Luis Daniel Mendoza Morales, Anna Karen Gárate Escamilla, Alvaro Martínez Sánchez | [VERIFICADO] F3 (Etapa 4.2) |
| Socio formador | **DanuStore** (en los documentos del equipo aparece como "DanuStore / Danu Analítica") | [VERIFICADO] F1, F2 |
| Reto asignado | **Reto de inventarios** | [VERIFICADO] F1 y las instrucciones de la Etapa 5.1 que se citan en la conversación (F9) |

**Nota sobre la autoría del chatbot.** El diseño del chatbot se hizo en la conversación a petición de Jaime Hernández González. No hay evidencia de que el resto del equipo lo haya revisado [NO DOCUMENTADO].

---

## 2. Socio formador: DanuStore

### 2.1 Giro y contexto

- **Giro:** empresa mexicana de venta de ropa (retail de moda) [VERIFICADO] F1.
- **Presencia:** 7 regiones: Ciudad de México, Zona Metropolitana de Monterrey, Zona Metropolitana de Guadalajara, Bajío, Noroeste, Sur y Sureste [VERIFICADO] F7.
- **Portafolio en los datos:** 130 productos en 4 categorías (Casual Wear, Footwear, Fitness Wear y Accessories) y 13 subcategorías (Bags, Belts, Boots, Bottoms, Dresses, Hats, Jewelry, Outerwear, Pants, Sandals, Shirts, Sneakers y Tops) [VERIFICADO] F7.
- **Clientes:** 44,987 clientes registrados únicos, clasificados por ingreso mensual en Básico (< $25,000), Silver ($25,000–50,000), Gold ($50,000–80,000) y Premium (> $80,000). El número de clientes está [VERIFICADO] en F2. Los rangos de ingreso están [VERIFICADO] en la conversación (F9, versión corregida de la Etapa 4.2), pero no en el texto de los archivos `.docx` del repositorio.
- **Lo que no está documentado:** tamaño de la empresa, número de tiendas, nombres de las sucursales, ciudades, canales de venta reales, sistemas internos (ERP, POS) y organigrama [NO DOCUMENTADO]. Existe la variable `Preferred_Channel`, pero el repositorio no describe los canales de la empresa.

### 2.2 Datos que entregó el socio formador

| Base | Detalle | Registros | Variables | Estado |
|---|---|---|---|---|
| Nivel Macro (mensual) | producto × región × mes, enero 2024 – diciembre 2025 | 21,840 (130 × 7 × 24) | 20 | [VERIFICADO] F7 |
| Nivel Micro (diario) | movimientos diarios de inventario con datos del cliente | 2,396,663 | 39 | [VERIFICADO] F2 |
| Clientes únicos | tabla que deriva el equipo | 44,987 | 16 | [VERIFICADO] F2 |

Variables del Nivel Macro: `month`, `year`, `product_id`, `region`, `units_expected`, `stock`, `percentage`, `units_sold`, `sales_amount`, `product_name`, `category`, `subcategory`, `static_price`, `inventory_key`, `Ventas_Acumuladas_Mensual`, `Stock_Restante_Mensual`, `Cumplimiento_Venta_Esperada`, `Product_Repeat_Purchase_Rate`, `Venta_Promedio_Diaria` y `Dias_Cobertura_Inventario` [VERIFICADO] F7. Las cinco últimas variables derivadas las creó el equipo [VERIFICADO] F2.

**Límites de granularidad que afectan al chatbot** [VERIFICADO] F7:
- La base **no tiene tiendas, ciudades, tallas, costos, tiempos de reposición, promociones ni demanda no atendida**. El nivel más fino es **producto × región × mes**.
- Las ventas son **solo de clientes registrados** [VERIFICADO] F1, F5.

---

## 3. El problema: sobreinventario por un pronóstico inflado

### 3.1 Diagnóstico verificado

Todas las cifras de esta tabla salen del Nivel Macro, 2024–2025. Se recalcularon en esta auditoría y coinciden con F1.

| Hallazgo | Cifra | Fuente |
|---|---|---|
| Se vendió solo una fracción de lo esperado | **17.0 %** de `units_expected` (lo esperado es ≈ 5.9 veces lo vendido) | F1, F7 |
| Error del pronóstico actual (`units_expected`) | WAPE ≈ **489 %** en toda la base; **467.95 %** en la prueba de septiembre a diciembre de 2025 | F1, F5 |
| Cobertura planeada vs. cobertura real | **~34 días** planeados contra **~208 días** reales (mediana mensual agregada) | F1 |
| Rotación de inventario | ≈ **1.8 vueltas al año** (la industria de ropa reporta de 4 a 6) | F1 |
| El pronóstico no sigue la temporada | las ventas cambian por mes (F = 36.25, p < 0.001), pero el pronóstico es plano (F = 0.40, p = 0.958) | F1 |
| Temporada | noviembre y diciembre ≈ **+22 %** sobre un mes promedio; febrero ≈ **−15 %** | F1, F7 |
| La región manda | la región explica el **88.7 %** de la variación del cumplimiento y el **68.6 %** de la de los días de cobertura (η², ANOVA) | F1, F2 |

### 3.2 Indicadores por región

Fuente: F7, recalculado. La cobertura es la mediana de los meses de stock ÷ (ventas ÷ días del mes), agregando cada región por mes.

| Región | % de las ventas | Cumplimiento (vendido ÷ esperado) | Esperado ÷ vendido | Cobertura real (días) |
|---|---|---|---|---|
| Ciudad de México | 35.6 % | 33.5 % | 3.0× | **113** |
| ZM Monterrey | 22.2 % | 22.6 % | 4.4× | 165 |
| ZM Guadalajara | 15.9 % | 17.6 % | 5.7× | 205 |
| Bajío | 9.5 % | 11.5 % | 8.7× | 301 |
| Noroeste | 6.6 % | 8.9 % | 11.3× | 374 |
| Sur | 5.6 % | 8.4 % | 12.0× | 382 |
| Sureste | 4.7 % | **6.7 %** | **15.0×** | **478** |

**Las cifras de cobertura cambian según el método.** Con la mediana o el promedio de cada registro producto-región-mes, CDMX sale entre 109 y 111 días y Sureste entre 472 y 490. En los documentos del equipo aparecen las tres variantes, así que se debe aclarar el método al presentar (ver `07_FUENTES_Y_PENDIENTES.md`, contradicción C2).

### 3.3 Indicadores por categoría

Fuente: F7, recalculado.

| Categoría | % de las ventas | Cumplimiento | Cobertura real (días) |
|---|---|---|---|
| Casual Wear | 28.7 % | 18.0 % | 197 |
| Footwear | 26.3 % | 15.4 % | 230 |
| Fitness Wear | 25.0 % | 18.0 % | 197 |
| Accessories | 20.0 % | 16.8 % | 209 |

**Conclusión documentada:** el problema de inventario es más **regional** que de producto. Las regiones con menos venta reciben inventario proporcionalmente excesivo [VERIFICADO] F1, F2.

### 3.4 Indicadores de referencia de la industria

Estas cifras salen de F1 y son referencias orientativas de fuentes sectoriales y comerciales, no normas.
- Días de inventario sanos en ropa: **60 a 90 días** (61 a 91 si se usan de 4 a 6 vueltas al año).
- Sell-through al cierre de la temporada: 60–80 %.
- Inventario de seguridad: SS = z·σ·√L, con z = 1.65 para un nivel de servicio del 95 %.
- Punto de reorden: ROP = d̂·L + SS.
- **Lo que no se puede calcular en DanuStore:** el desabasto (no hay registro de demanda no atendida), el GMROI (no hay costos) y el ROP (no hay tiempo de reposición L).

---

## 4. Objetivos del reto

**Lo que piden las instrucciones** [VERIFICADO] F9, que cita las instrucciones de la Etapa 5.1: investigar los indicadores y parámetros de la industria de la ropa para evaluar la eficiencia de los inventarios, como baja rotación, sobrestock, desabasto, estacionalidad y días de inventario disponible.

**Objetivo general que definió el equipo** [VERIFICADO] F1: pronosticar las **unidades vendidas por producto, región y mes** con un modelo de Machine Learning que sustituya a `units_expected`, y convertir ese pronóstico en **reglas de inventario** (cobertura, reorden y redistribución entre regiones).

**Objetivos específicos** [INFERENCIA, armados a partir de F1, F4 y F5]:
1. Medir el error del pronóstico actual contra la venta real.
2. Entrenar y comparar dos modelos de regresión (Random Forest y XGBoost) con particiones temporales.
3. Traducir el pronóstico a cobertura proyectada, alertas de sobrestock y propuestas de redistribución.
4. Llevar esas decisiones a los usuarios internos por medio de un chatbot (Danu Inventarios) [PROPUESTA].

**El objetivo del socio formador con sus propias palabras** (el enunciado oficial del reto que entregó DanuStore) **no está en el repositorio** [NO DOCUMENTADO].

---

## 5. Modelo de Machine Learning, la base técnica del chatbot

Fuente: F4 y F5, el notebook ejecutado. Todas las cifras están **verificadas en las salidas del notebook**.

### 5.1 Planteamiento

- **Variable objetivo:** `units_sold` por producto, región y mes. Es un problema de regresión.
- **Variables:** `mes`; las ventas rezagadas `ventas_mes_anterior`, `ventas_hace_2` y `ventas_hace_3`; `promedio_3_meses`; y `region`, `category` y `subcategory` con codificación One-Hot.
- **Variables excluidas por fuga de información:** `Ventas_Acumuladas_Mensual`, `Venta_Promedio_Diaria`, `Cumplimiento_Venta_Esperada`, `Dias_Cobertura_Inventario`, `Stock_Restante_Mensual` y `sales_amount`.
- **Otras exclusiones:** `static_price` se excluyó porque funciona como identificador del producto. `ventas_hace_12` se excluyó porque 2025 repite a 2024.
- **Particiones temporales:** 80/20, 70/30 y 60/40.
- **Selección de hiperparámetros:** con una ventana de validación de mayo a agosto de 2025.
- **Prueba final:** septiembre a diciembre de 2025.

### 5.2 Resultados en la prueba final (partición 80/20, septiembre a diciembre de 2025)

| Método | MAE | RMSE | WAPE | R² |
|---|---|---|---|---|
| Pronóstico actual (`units_expected`) | 1,042.04 | 1,093.44 | **467.95 %** | −32.19 |
| Ingenuo (ventas del mes anterior) | 44.15 | 66.71 | ≈ 19.8 % | — |
| **Random Forest** (100 árboles, sin límite de profundidad) | **13.31** | 20.80 | **5.98 %** | 0.988 |
| XGBoost (800 árboles, learning_rate = 0.03, max_depth = 8) | 14.64 | 20.54 | 6.58 % | 0.988 |
| Ingenuo estacional (mismo mes del año anterior) | 0.64 | 4.12 | 0.29 % | 1.000 |

- **Estabilidad:** el WAPE del Random Forest fue de 5.98 % en 80/20, 6.07 % en 70/30 y 6.12 % en 60/40 [VERIFICADO] F5, F6.
- **Validación (mayo a agosto de 2025):** Random Forest 6.28 % y XGBoost 7.91 %.
- **Error por región (Random Forest):** de 5.21 % en CDMX a 8.15 % en Sureste. En XGBoost va de 3.64 % a 12.73 %.
- **Pronóstico recursivo de 1 a 4 meses (Random Forest):** 5.83 % → 9.42 % → 10.94 % → **12.26 %** en el cuarto mes. En el **bloque completo de septiembre a diciembre** el error es de **9.91 %** (XGBoost: 10.19 %).
- **Impacto del preprocesamiento:** sin las ventas pasadas el WAPE es de 22.65 %; con ellas baja a 5.98 %.
- **Importancia de variables:** `promedio_3_meses` ≈ 0.92 y `mes` ≈ 0.03 [VERIFICADO] F6.

### 5.3 Limitaciones del modelo, críticas para el chatbot

1. **Las ventas de 2025 repiten a las de 2024:** el 76.6 % de los registros es idéntico. Por eso el ingenuo estacional sale casi perfecto y los resultados son optimistas [VERIFICADO] F5, F6.
2. Las ventas son solo de clientes registrados.
3. El modelo necesita **3 meses de historia**, así que no sirve para productos nuevos.
4. El error crece con el horizonte: 6 % a un mes y 12 % en el cuarto mes.
5. Los meses de prueba se consultaron durante el análisis, así que falta una evaluación independiente.
6. **Los pronósticos por producto no se exportaron a ningún archivo.** Solo existen dentro del notebook [VERIFICADO]: no hay CSV de pronósticos en el repositorio.

### 5.4 Contradicción resuelta con evidencia

La investigación de la Etapa 5.1 (F1) proponía **XGBoost como modelo principal**. El código (F4, F5) mostró que **Random Forest ganó** en las tres particiones y en la validación. Para el chatbot se usa **Random Forest**, porque hay evidencia ejecutada que lo respalda.

---

## 6. La solución: chatbot "Danu Inventarios"

### 6.1 Cómo evolucionó el diseño

| Versión | Descripción | Estado |
|---|---|---|
| v1 "Danu" | Chatbot híbrido de ventas y atención para **clientes** en el sitio web: tallas, existencias por tienda, ofertas y pedidos | **Descartada como solución principal.** El usuario la corrigió: *"es para lo de inventario… es resolver el problema de inventario"* (F9) |
| v2 "Danu Inventarios" | Asistente **interno** para quienes deciden el inventario | **Diseño vigente** [PROPUESTA]; no está implementado |

La v1 solo sirve como posible complemento. Sus user personas (Valeria Ruiz y Fernanda Morales) **no corresponden a la versión vigente** y no deben usarse.

### 6.2 Nombre y propósito

**Danu Inventarios** es un asistente interno de DanuStore para la planeación de inventario. Su propósito es **reducir el sobreinventario y evitar faltantes**: dice cuánto pedir, dónde sobra, dónde falta y a dónde mover el producto, con base en el pronóstico del modelo Random Forest [PROPUESTA] F9.

### 6.3 Problemas específicos que resuelve

| Problema verificado | Cómo lo atiende el chatbot [PROPUESTA] |
|---|---|
| El pronóstico actual espera ≈ 6 veces lo que se vende | Da el pronóstico del modelo (≈ 6 % de error a un mes) en lugar de `units_expected` |
| Cobertura de ~208 días contra 60–90 días sanos | Calcula los días de cobertura y los marca con un semáforo |
| Desbalance regional (113 contra 478 días) | Propone traslados de las regiones con más cobertura a las que tienen menos |
| No hay estacionalidad en el plan | Advierte sobre noviembre y diciembre (+22 %) y febrero (−15 %) |
| El planeador arma todo en Excel a mano | Responde en lenguaje natural y permite descargar las tablas |

### 6.4 Las cuatro funciones del diseño [PROPUESTA] F9

1. **Consulta:** inventario, ventas y días de cobertura por producto, región y tienda. Ojo: la base no tiene tiendas.
2. **Pronóstico:** cuánto se va a vender el próximo mes o los próximos cuatro meses.
3. **Alertas:** semáforo de sobrestock y de riesgo de faltante.
4. **Recomendación:** cuánto pedir, qué trasladar entre regiones y qué promocionar.

### 6.5 Usuarios beneficiados

Son compradores, planeadores de inventario y gerentes de tienda o de región. El diseño los representa con dos personas: Carlos Méndez y Laura Gutiérrez (ver `02_UX_UI_USER_PERSONAS.md`). **No atiende a clientes finales.**

### 6.6 Alcance y restricciones

- **Fuera de alcance** [PROPUESTA] F9: aprobar compras o traslados (solo los propone), modificar datos del sistema, atender clientes y compartir información fuera de la empresa.
- **Restricciones de los datos** [VERIFICADO]: no hay tiendas, tallas, costos, tiempo de reposición, inventario de seguridad, promociones ni datos de 2026 en adelante.

### 6.7 Beneficios esperados y limitaciones

- **Beneficios esperados** [PROPUESTA]: compras alineadas con la venta real, menos días de cobertura, regiones más equilibradas y menos trabajo manual en Excel. **No hay mediciones** de ninguno de estos beneficios.
- **Limitaciones** [VERIFICADO]: las del modelo (sección 5.3), las de granularidad (sección 2.2) y que **no existe ninguna implementación**, ni conexión con datos, ni pruebas del chatbot.

---

## 7. Relación entre el chatbot y las necesidades de la organización

Problema (pronóstico inflado y sobreinventario regional) → modelo (Random Forest, WAPE de 5.98 %) → reglas (cobertura, pedido sugerido y redistribución) → **chatbot**, que lleva esas reglas a quien decide, en lenguaje natural.

La relación entre el diagnóstico y el modelo está verificada. La relación entre el modelo y el chatbot es **una propuesta**.

---

## 8. Contenido del repositorio que no pertenece a este proyecto

El repositorio `patatamanyt/no-entear` también contiene una aplicación de análisis de video de fútbol 7: `README.md`, `backend/`, `frontend/`, `Makefile` y `run.sh`. **No tiene relación con DanuStore**, así que no se debe usar como evidencia de este proyecto [VERIFICADO].
