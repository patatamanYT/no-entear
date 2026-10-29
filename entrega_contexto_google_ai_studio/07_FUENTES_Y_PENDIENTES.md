# 07 · Fuentes, trazabilidad, contradicciones y pendientes

## 1. Fuentes consultadas

| ID | Fuente | Ruta o ubicación | Qué aporta |
|---|---|---|---|
| F1 | Investigación de la Etapa 5.1 (individual) | `TI3002C_Etapa_5.1_6_Jaime_Hernandez_Gonzalez.docx` | El reto de inventarios, el diagnóstico (17 %, 34 contra 208 días, 113 a 478 días, η²), los indicadores de la industria, la propuesta de modelos y la bibliografía |
| F2 | Etapa 4.3: correlaciones, ANOVA y Chi-cuadrado | `TI3002C_Etapa_4.3_6.docx` | Los integrantes del equipo, el socio formador, las bases Micro y Macro, el número de clientes y los efectos regionales |
| F3 | Etapa 4.2: estadística descriptiva | `TI3002C_Etapa_4.2_Equipo_6.docx`, `notebooks/DanuStore_4_2.ipynb` | Los docentes, las variables y el análisis descriptivo |
| F4 | Notebook del código de ML | `etapa_5_1_codigo/TI3002C_Etapa 5.1_Código ML_6_Jaime Hernández González.ipynb` y `.py` | Variables, particiones, modelos y métricas (salidas ejecutadas) |
| F5 | PDF del notebook | `etapa_5_1_codigo/TI3002C_Etapa 5.1_Código ML_6_Jaime Hernández González.pdf` | Las mismas salidas, impresas |
| F6 | Material de estudio | `etapa_5_1_codigo/Resumen_Codigo_ML.pdf`, `Guia_presentacion_Codigo_ML.pdf`, `Codigo_ML_paso_a_paso.pdf` | El resumen de resultados y las limitaciones en lenguaje sencillo |
| F7 | Datos del Nivel Macro | `data_DanuStore_Equipo6_Mensual.csv` (**no está versionado en el repositorio**; se subió a la sesión) | 21,840 registros. Los indicadores por región y categoría **se recalcularon en esta auditoría** |
| F8 | Gráficas | `graficas_region/`, `graficas_cobertura/`, `histogramas_faltantes/`, `Diagrama_ER_DanuStore.png` | Las visualizaciones del diagnóstico |
| F9 | Historial de la conversación con el asistente | No está en el repositorio | El diseño completo del chatbot (v1 y v2), las user personas, los prompts de las fichas, las revisiones externas del modelo y las instrucciones de la Etapa 5.1 y de la presentación |

**Fuera de alcance:** `README.md`, `backend/`, `frontend/`, `Makefile` y `run.sh` pertenecen a una aplicación de análisis de fútbol 7 que no tiene relación con DanuStore.

**Nota sobre F9.** El diseño del chatbot **solo existe en la conversación**. Se recomienda que el equipo guarde este paquete como la fuente oficial.

## 2. Trazabilidad de los hallazgos clave

| Hallazgo | Documento | Fuente |
|---|---|---|
| Reto de inventarios | 01 §1 | F1, F9 |
| 17 % vendido de lo esperado; WAPE de 489 % | 01 §3.1 | F1; recalculado con F7 |
| Cobertura de 34 contra 208 días; de 113 a 478 por región | 01 §3.2 | F1; recalculado con F7 |
| Random Forest con 5.98 %; recursivo de 9.91 % y 12.26 % | 01 §5 | F4, F5 |
| 2025 repite a 2024 (76.6 %) | 01 §5.3 | F4 (§14), F6 |
| Diseño de Danu Inventarios, personas, flujos y prompt | 01 §6, 02, 03 §A | F9 |
| Semáforo corregido, reglas nuevas y paleta | 02 §3.3, 03 §C | **Propuesta de esta auditoría** |
| Optimizaciones O1–O12 | 04 | **Propuesta de esta auditoría** |

## 3. Contradicciones encontradas

| ID | Contradicción | Resolución |
|---|---|---|
| C1 | La investigación (F1) propone **XGBoost** como modelo principal; el código (F4) da a **Random Forest** como el mejor | **Resuelta con evidencia:** se usa Random Forest (5.98 % contra 6.58 % en la prueba y 6.28 % contra 7.91 % en la validación) |
| C2 | La cobertura de CDMX aparece como 109, 111 o 113 días, y la de Sureste como 472, 478 o 490, según el documento | **Explicada, no unificada:** son métodos distintos (mediana agregada por mes, mediana o promedio por registro). Este paquete usa 113 y 478 (F1, mediana agregada). **El equipo debe elegir un método para la presentación** |
| C3 | El WAPE del pronóstico actual aparece como 489 % (toda la base, F1) y 467.95 % (prueba de septiembre a diciembre de 2025, F4) | **Resuelta:** son periodos distintos y las dos cifras son correctas. Siempre hay que decir el periodo |
| C4 | El prompt del diseño dice "~10 % a cuatro meses"; el notebook da 9.91 % para el bloque y 12.26 % para el cuarto mes | **Resuelta con evidencia** (03 §C.2, O1) |
| C5 | El diseño menciona "tiendas", "Mérida" y "gerentes de tienda"; los datos solo tienen regiones | **Resuelta:** el chatbot debe responder a nivel región (O3) |
| C6 | Los botones del diseño ([Alertas de hoy], [Reporte mensual]) no coinciden exactamente con los del script ([Ver alertas], [Reporte]) | Menor; hay que unificar los nombres |
| C7 | El diseño plantea el objetivo de reducir a la mitad las horas en Excel sin tener una línea base | **No se usa como dato** (06 §1) |
| C8 | v1 (clientes, con las personas Valeria y Fernanda) contra v2 (interno, con Carlos y Laura) | **Resuelta:** la vigente es la v2, por la corrección explícita del usuario (F9) |

## 4. Datos que necesitan confirmación humana

1. **El enunciado oficial del reto** entregado por DanuStore, con sus objetivos tal cual.
2. **Si el equipo y el profesor aprobaron la v2** (asistente interno) como la versión final del chatbot.
3. **La autoría:** quién del equipo participó en el diseño del chatbot.
4. **El método de cobertura** que se usará en la presentación (C2).
5. **Los umbrales del semáforo** para 🟡 (30–60 días) y ⚪ (menos de 30 días), que son una propuesta de la auditoría.
6. **Si se generaron las fichas visuales** de Carlos y Laura, y dónde están.
7. **Si se usará Google AI Studio**, con qué modelo y con qué configuración (temperatura, etc.).
8. **La paleta, la tipografía y la interfaz:** el proyecto no las definió; las de la auditoría son solo propuestas.
9. **La exportación de los pronósticos por producto** a CSV para cargarlos como conocimiento, si se quiere que el bot dé pronósticos por producto.
10. **Datos que DanuStore no ha entregado:** tiendas, tiempo de reposición, inventario de seguridad, costos y promociones.
11. **Las metas numéricas** de los indicadores del documento 06.
12. **Las reflexiones personales** del equipo (06 §5).
13. **Los requisitos de la entrega** del chatbot y de la presentación: la rúbrica, la fecha y la duración no están en el repositorio.

## 5. Revisión de confidencialidad

- No se incluyen credenciales, claves API, correos ni matrículas.
- Se mencionan los nombres del equipo y de los docentes tal como aparecen en los documentos académicos. Si se van a compartir fuera del curso, conviene quitarlos.
- Los datos de DanuStore se presentan **agregados** (por región o categoría), sin registros individuales de clientes.
