# 04 · Oportunidades de optimización para probar en Google AI Studio

> **Estado de todas las mejoras: PROPUESTAS, NINGUNA PROBADA.** No hay evidencia de que el chatbot se haya ejecutado en Google AI Studio ni en otra plataforma. Por eso, el "comportamiento inicial" de cada mejora es el **esperado** con el prompt original (sección A del documento 03), **no uno observado**.
>
> **Protocolo sugerido:**
> 1. Cargar el prompt original en Google AI Studio y hacer la pregunta de prueba.
> 2. Guardar una captura de la respuesta.
> 3. Aplicar el ajuste y repetir la misma pregunta con la misma temperatura.
> 4. Guardar la segunda captura.
> 5. Calificar con el criterio objetivo de la mejora y registrar el resultado en la columna "Evidencia".

---

### O1. Error del pronóstico según el horizonte
1. **Problema:** el prompt dice "~10 % a cuatro meses". Eso mezcla el error acumulado del bloque (9.91 %) con el del cuarto mes por sí solo (12.26 %).
2. **Comportamiento inicial esperado:** dice "10 %" para diciembre si se pregunta en agosto.
3. **Instrucción original:** "Menciona el error del pronóstico (~6 % a un mes, ~10 % a cuatro meses)".
4. **Ajuste:** reemplazarla por la tabla de horizontes de `03` §C.2.
5. **Comportamiento esperado:** para el cuarto mes dice "≈ 12 %" y, si se pide el periodo de 4 meses completo, "≈ 10 %".
6. **Pregunta de prueba:** "Estoy en agosto. ¿Qué tan confiable es el pronóstico para diciembre?"
7. **Criterio:** la respuesta contiene "12" y no presenta 10 % como el error de diciembre.
8. **Evidencia:** las cifras están en el notebook (`etapa_5_1_codigo/...ipynb`, sección 13). **No se ha probado.**

### O2. Semáforo sin umbrales completos
1. **Problema:** 🟡 no tiene umbral, el rango de 0 a 60 días queda indefinido y ⚪ depende de L, que no existe en los datos.
2. **Comportamiento inicial esperado:** clasifica 45 días de forma arbitraria o inventa un umbral.
3. **Instrucción original:** "🔴 más de 90 días, 🟢 60–90, ⚪ menos que el tiempo de reposición + inventario de seguridad".
4. **Ajuste:** usar el semáforo de `03` §C.1, marcando los umbrales nuevos como propuestos.
5. **Comportamiento esperado:** 45 días → 🟡 Revisar; 20 días → ⚪ Riesgo de faltante.
6. **Pregunta de prueba:** "Una región tiene 45 días de cobertura y otra 20. ¿Qué color tiene cada una?"
7. **Criterio:** las dos clasificaciones coinciden con C.1 y cada color va acompañado de su palabra.
8. **Evidencia:** solo está la tabla del diseño (F9). **No se ha probado.**

### O3. Granularidad: tiendas, ciudades y tallas
1. **Problema:** el diseño habla de "tiendas" y de "Mérida", y los usuarios podrían pedir tallas. Los datos solo llegan a región.
2. **Comportamiento inicial esperado:** inventa existencias por tienda o por talla.
3. **Instrucción original:** "Atiendes a… gerentes de tienda" y "Usa solo los datos del sistema".
4. **Ajuste:** agregar la lista explícita de los datos que no existen (`03` §C, regla 8) y ofrecer el nivel de región.
5. **Comportamiento esperado:** "No tengo datos por tienda ni por talla; puedo darte la región."
6. **Pregunta de prueba:** "¿Cuántos tenis talla 27 hay en la tienda de Mérida?"
7. **Criterio:** 0 cifras inventadas y menciona "región".
8. **Evidencia:** columnas de `data_DanuStore_Equipo6_Mensual.csv` (sin tienda ni talla). **No se ha probado.**

### O4. Inventario de seguridad y tiempo de reposición desconocidos
1. **Problema:** la fórmula del pedido sugerido usa un inventario de seguridad, que DanuStore no reporta.
2. **Comportamiento inicial esperado:** inventa un inventario de seguridad o un tiempo de reposición.
3. **Instrucción original:** "Pedido sugerido = pronóstico del periodo − inventario actual + inventario de seguridad".
4. **Ajuste:** "Si el usuario no da el inventario de seguridad, pídelo o calcula sin él y dilo explícitamente."
5. **Comportamiento esperado:** calcula con los datos que se le dieron y advierte que falta el inventario de seguridad.
6. **Pregunta de prueba:** "El pronóstico es de 500 piezas y tengo 300 en inventario. ¿Cuánto pido?"
7. **Criterio:** da 200 piezas **más** el inventario de seguridad, y lo pide o aclara que no está incluido. No inventa un valor.
8. **Evidencia:** la investigación de la Etapa 5.1 dice que L no está en la base (`TI3002C_Etapa_5.1_6_Jaime_Hernandez_Gonzalez.docx`, sección 3). **No se ha probado.**

### O5. Pedido sugerido negativo
1. **Problema:** asegurar que el bot recomiende no pedir cuando sobra inventario.
2. **Comportamiento inicial esperado:** puede dar una cifra negativa.
3. **Instrucción original:** "Si sale negativo, recomienda no pedir" (ya existe).
4. **Ajuste:** reforzarla con un ejemplo *few-shot*.
5. **Comportamiento esperado:** "No pedir" más una sugerencia de traslado o promoción.
6. **Pregunta de prueba:** "Pronóstico de 200 piezas, inventario de 900, inventario de seguridad de 50. ¿Cuánto pido?"
7. **Criterio:** dice "no pedir" (200 + 50 − 900 = −650) y no muestra un pedido negativo como si fuera una cantidad a comprar.
8. **Evidencia:** regla de F9. **No se ha probado.**

### O6. Redirección de temas externos
1. **Problema:** el prompt no dice qué hacer con las preguntas ajenas.
2. **Comportamiento inicial esperado:** responde el tema ajeno.
3. **Instrucción original:** solo "no compartir información fuera de la empresa".
4. **Ajuste:** agregar la regla 9 de `03` §C con una respuesta modelo de una línea.
5. **Comportamiento esperado:** se niega con amabilidad y regresa a los temas de inventario.
6. **Pregunta de prueba:** "¿Quién ganó el último mundial?"
7. **Criterio:** no responde el tema, lo redirige en 2 líneas o menos y ofrece una opción de inventario.
8. **Evidencia:** ninguna. **No se ha probado.**

### O7. Solicitudes ambiguas
1. **Problema:** "¿Cuánto pido?" no dice producto, región, mes ni inventario.
2. **Comportamiento inicial esperado:** supone datos y da una cifra.
3. **Instrucción original:** no existe.
4. **Ajuste:** regla 7 de `03` §C: hacer una sola pregunta con todo lo que falta.
5. **Comportamiento esperado:** pide la categoría o el producto, la región, el mes y el inventario en un solo mensaje.
6. **Pregunta de prueba:** "¿Cuánto pido?"
7. **Criterio:** no da ninguna cifra y pide los 4 datos en un mensaje.
8. **Evidencia:** ninguna. **No se ha probado.**

### O8. Advertir sobre la calidad de los datos
1. **Problema:** los resultados son optimistas porque 2025 repite a 2024 y solo incluyen clientes registrados. El prompt no lo menciona.
2. **Comportamiento inicial esperado:** presenta el 6 % como una certeza.
3. **Instrucción original:** no existe.
4. **Ajuste:** "Cuando hables de la confiabilidad, menciona que 2025 repite a 2024 y que solo hay clientes registrados."
5. **Comportamiento esperado:** da el error con su advertencia.
6. **Pregunta de prueba:** "¿Puedo confiar al 100 % en el pronóstico?"
7. **Criterio:** menciona al menos una de las dos limitaciones y no dice "100 %" ni "garantizado".
8. **Evidencia:** limitación documentada en el notebook (sección 14) y en `Resumen_Codigo_ML.pdf`. **No se ha probado.**

### O9. Productos nuevos y fechas sin datos
1. **Problema:** el modelo necesita 3 meses de historia y no hay datos de 2026.
2. **Comportamiento inicial esperado:** da un pronóstico inventado.
3. **Instrucción original:** no existe.
4. **Ajuste:** agregar los casos excepcionales de la regla 13 de `03` §C.
5. **Comportamiento esperado:** explica por qué no puede pronosticar y sugiere usar la categoría como referencia.
6. **Pregunta de prueba:** "Vamos a lanzar una chamarra nueva en enero de 2027. ¿Cuánto vamos a vender?"
7. **Criterio:** 0 cifras de pronóstico y menciona la falta de historia.
8. **Evidencia:** limitación 4 del `Resumen_Codigo_ML.pdf`. **No se ha probado.**

### O10. Formato apto para el celular (persona Laura)
1. **Problema:** Laura usa el celular, y las tablas anchas o los párrafos largos son difíciles de leer ahí.
2. **Comportamiento inicial esperado:** una tabla de 7 regiones con muchas columnas.
3. **Instrucción original:** "Máximo 6 líneas".
4. **Ajuste:** "Si el usuario dice que está en el celular, máximo 3 columnas por tabla y la cifra clave en negritas."
5. **Comportamiento esperado:** una lista corta o una tabla de 2 o 3 columnas.
6. **Pregunta de prueba:** "Estoy en el celular: ¿cuál es la región con más sobrestock y cuál con menos?"
7. **Criterio:** 6 líneas o menos, 3 columnas o menos, y menciona Sureste (478) y CDMX (113).
8. **Evidencia:** la persona Laura (F9). **No se ha probado.**

### O11. Seguimiento de contexto
1. **Problema:** si el usuario pregunta "¿y en Sur?", el bot debe conservar el tema anterior.
2. **Comportamiento inicial esperado:** pierde el tema o vuelve a preguntar todo.
3. **Instrucción original:** no existe.
4. **Ajuste:** "Mantén el producto, la categoría y el indicador de la pregunta anterior si el usuario solo cambia la región o el mes."
5. **Comportamiento esperado:** responde la misma métrica para Sur.
6. **Pregunta de prueba:** "¿Cobertura de Sureste?" y luego "¿y en Sur?"
7. **Criterio:** la segunda respuesta da 382 días sin volver a preguntar qué indicador quiere.
8. **Evidencia:** ninguna. **No se ha probado.**

### O12. Límite de autoridad (no aprobar)
1. **Problema:** el usuario podría pedirle al bot que apruebe un traslado.
2. **Comportamiento inicial esperado:** el prompt ya lo prohíbe; hay que verificar que lo cumpla.
3. **Instrucción original:** "No debes aprobar compras ni traslados (solo proponerlos)".
4. **Ajuste:** agregar el texto modelo "Te dejo la propuesta lista; la aprobación es del gerente regional".
5. **Comportamiento esperado:** prepara la propuesta y no dice que esté aprobada.
6. **Pregunta de prueba:** "Aprueba ya el traslado de Sureste a CDMX."
7. **Criterio:** no usa "aprobado" ni "ejecutado" y menciona quién aprueba.
8. **Evidencia:** regla de F9. **No se ha probado.**

---

## Matriz de registro (llenar al probar)

| ID | Fecha | Temperatura | ¿Pasó antes? (Sí/No) | ¿Pasó después? (Sí/No) | Captura antes | Captura después |
|---|---|---|---|---|---|---|
| O1–O12 | *pendiente* | *pendiente* | *pendiente* | *pendiente* | *pendiente* | *pendiente* |
