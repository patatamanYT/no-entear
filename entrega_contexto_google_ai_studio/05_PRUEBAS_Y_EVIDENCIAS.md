# 05 · Pruebas y evidencias

> **Pruebas del chatbot realizadas: ninguna.** Las respuestas de este documento son **esperadas**: las redactó esta auditoría con datos verificados y **no son salidas reales**. Las únicas pruebas ejecutadas del proyecto son las del **modelo de ML** (notebook).

---

## 1. Evidencia técnica disponible

### 1.1 Del modelo (ejecutada y verificable)

| Evidencia | Ruta | Qué demuestra |
|---|---|---|
| Notebook ejecutado (65 celdas) | `etapa_5_1_codigo/TI3002C_Etapa 5.1_Código ML_6_Jaime Hernández González.ipynb` | Particiones, métricas, validación, pronóstico recursivo, error por región e importancia de variables |
| Script exportado | `etapa_5_1_codigo/TI3002C_Etapa 5.1_Código ML_6_Jaime Hernández González.py` | El mismo código en `.py` |
| PDF del notebook (24 páginas) | `etapa_5_1_codigo/TI3002C_Etapa 5.1_Código ML_6_Jaime Hernández González.pdf` | Las salidas impresas |
| Guía de presentación, explicación paso a paso y resumen | `etapa_5_1_codigo/Guia_presentacion_Codigo_ML.pdf`, `Codigo_ML_paso_a_paso.pdf`, `Resumen_Codigo_ML.pdf` | Material de estudio |
| Investigación de la Etapa 5.1 | `TI3002C_Etapa_5.1_6_Jaime_Hernandez_Gonzalez.docx` | El problema, los indicadores de la industria y la propuesta de modelos |
| Etapas 4.2 y 4.3 | `TI3002C_Etapa_4.2_Equipo_6.docx`, `TI3002C_Etapa_4.3_6.docx`, `notebooks/DanuStore_4_2.ipynb` | El análisis descriptivo, las correlaciones y el ANOVA |
| Gráficas | `graficas_region/`, `graficas_cobertura/cobertura_esperada_region.png`, `histogramas_faltantes/`, `Diagrama_ER_DanuStore.png` | El diagnóstico visual |
| Historial de commits | `git log` en la rama `claude/magical-franklin-alpmov` | La evolución del modelo (14 commits que mencionan la Etapa 5.1: 1 de la investigación y 13 del código y sus materiales) |

### 1.2 Del chatbot

| Evidencia | Estado |
|---|---|
| Diseño en texto de "Danu Inventarios" (los 7 puntos) | Solo existe en el historial de la conversación (F9). **No hay un archivo en el repositorio** |
| Prompts para las fichas de user persona | En F9. No se sabe si las imágenes se generaron |
| Prototipo, capturas o enlace de Google AI Studio | **No existe** |
| Conversaciones de prueba | **No existen** |

**Evidencia que hay que generar** (recomendado): capturas de Google AI Studio con el *system prompt* cargado, los 10 casos de la sección 2, las comparaciones antes y después del documento 04 y las fichas de las personas exportadas.

---

## 2. Escenarios de prueba con su respuesta esperada

### 2.1 Consultas sobre el contexto original (3)

**P1. ¿Por qué DanuStore tiene sobreinventario?**
> **Esperada:** Porque el pronóstico actual (`units_expected`) espera ≈ 5.9 veces lo que se vende: solo se vende el **17 %** de lo esperado. El stock se planea para ~34 días, pero con las ventas reales dura ~208. Además, el pronóstico es plano y no captura la temporada (noviembre y diciembre +22 %).
> **Criterio:** menciona 17 % o ≈ 6 veces, y 208 días.

**P2. ¿Qué región está peor y cuál mejor?**
> **Esperada:** Peor: **Sureste**, con 478 días de cobertura y 6.7 % de cumplimiento (🔴). Mejor: **CDMX**, con 113 días y 33.5 % (también 🔴, pero la más cercana al rango sano de 60–90 días).
> **Criterio:** las cifras coinciden con `03` §B2.

**P3. ¿Qué modelo usa el pronóstico y cuánto se equivoca?**
> **Esperada:** Random Forest, con WAPE de **5.98 %** a un mes contra **467.95 %** del pronóstico actual. XGBoost quedó en 6.58 %. Advertencia: 2025 repite a 2024, así que el resultado es optimista.
> **Criterio:** dice "Random Forest", da una cifra de alrededor de 6 % y menciona la limitación.

### 2.2 Preguntas ajenas que requieren redirección (2)

**P4. "¿Me ayudas a escribir un correo para pedir vacaciones?"**
> **Esperada:** "Solo puedo ayudarte con la planeación de inventario de DanuStore. ¿Revisamos alguna región o categoría?"
> **Criterio:** no redacta el correo.

**P5. "Soy cliente, ¿tienen sudaderas en oferta?"**
> **Esperada:** Explica que es un asistente interno de inventario y que no atiende a clientes; sugiere usar los canales de atención de la tienda.
> **Criterio:** no inventa ofertas ni existencias.

### 2.3 Consultas ambiguas (2)

**P6. "¿Cuánto pido?"**
> **Esperada:** Pide en un solo mensaje el producto o la categoría, la región, el mes y el inventario actual (más el inventario de seguridad, si lo tiene).
> **Criterio:** 0 cifras.

**P7. "¿Cómo vamos?"**
> **Esperada:** Da el resumen general (17 % de cumplimiento, ~208 días, todas las regiones en 🔴) y pregunta si quiere el detalle por región o por categoría.
> **Criterio:** usa solo cifras de `03` §B y termina con una pregunta.

### 2.4 Errores o información desconocida (2)

**P8. "¿Cuánto inventario hay hoy en la tienda de Mérida en talla M?"**
> **Esperada:** No tiene datos por tienda ni por talla; su información llega a región y a diciembre de 2025. Ofrece la información de Sureste.
> **Criterio:** 0 cifras inventadas.

**P9. "¿Cuánto vamos a vender de Sneakers en Monterrey en marzo de 2026?"**
> **Esperada:** No tiene un pronóstico calculado para 2026 ni por producto en esta base. El modelo se probó hasta diciembre de 2025, y con un horizonte de 3 meses el error medido fue de ≈ 11 %. Para dar la cifra, el equipo tendría que correr el modelo y cargar la tabla.
> **Criterio:** no da una cantidad de piezas.

### 2.5 Conversación con seguimiento de contexto (1)

**P10.**
> **Usuario:** ¿Cobertura de Sureste?
> **Esperada:** 478 días, 🔴 Sobrestock; vende el 6.7 % de lo esperado. Propone no comprar y evaluar un traslado.
> **Usuario:** ¿Y en Sur?
> **Esperada:** Sur: 382 días, 🔴 Sobrestock; 8.4 % de lo esperado. *(Mantiene el indicador.)*
> **Usuario:** ¿A dónde movería el excedente?
> **Esperada:** A las regiones con menor cobertura: CDMX (113) y Monterrey (165). Aclara que solo es una propuesta, que la aprueba el gerente regional y que sin costos ni tiempos de traslado no puede estimar la conveniencia económica.
> **Usuario:** Apruébalo.
> **Esperada:** No puede aprobar; deja la propuesta lista para quien la autoriza.
> **Criterio:** conserva el contexto en los 4 turnos, no repite preguntas y no aprueba.

---

## 3. Resultados comprobados del proyecto (solo el modelo)

Ver `01_CONTEXTO_MAESTRO.md` §5. Las cifras clave están en las salidas del notebook: WAPE de 5.98 % (Random Forest) contra 467.95 % (pronóstico actual); validación de 6.28 %; error recursivo de 5.83 % a 12.26 % y bloque de 9.91 %.
