#!/usr/bin/env python
# coding: utf-8

# # TI3002C – Etapa 5.1: Código ML
# **Equipo 6 – Nexxus Consulting**
# **Nombre:** Jaime Hernández González
# **Matrícula:** A00840312
# 
# **Problemática (regresión):** pronosticar las **unidades vendidas (`units_sold`)** de cada producto, en cada región y en cada mes, para que DanuStore planee su inventario con un pronóstico más preciso que el que usa hoy (`units_expected`).
# 
# **Modelos:** Random Forest y XGBoost (los dos propuestos en la investigación de la Etapa 5.1).

# ## 1. Librerías

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

pd.set_option('display.max_colwidth', None)   # para ver los hiperparámetros completos en las tablas


# ## 2. Importar datos
# Se usa la base **mensual (Nivel Macro)**: 130 productos × 7 regiones × 24 meses (2024–2025).

# In[2]:


# Si usas Google Drive, monta tu Drive y cambia la ruta:
# from google.colab import drive
# drive.mount('/content/drive')
# df = pd.read_csv('/content/drive/MyDrive/data_DanuStore_Equipo6_Mensual.csv')

df = pd.read_csv('data_DanuStore_Equipo6_Mensual.csv')
print(df.shape)
df.head()


# ### 2.0 Exploración inicial
# Revisamos el tamaño de la base, los tipos de datos, si hay valores nulos o registros duplicados, y las estadísticas básicas de la variable objetivo.

# In[3]:


print('Filas y columnas:', df.shape)
print('Valores nulos en toda la base:', df.isnull().sum().sum())
print('Registros duplicados:', df.duplicated().sum())
print('Productos:', df['product_id'].nunique(), '| Regiones:', df['region'].nunique(), '| Categorías:', df['category'].nunique())
df.dtypes


# In[4]:


df[['units_sold', 'units_expected', 'stock', 'static_price']].describe().round(2)


# In[5]:


fig, ax = plt.subplots(1, 2, figsize=(12, 4))

ax[0].hist(df['units_sold'], bins=40)
ax[0].set_title('Distribución de units_sold')
ax[0].set_xlabel('Unidades vendidas por producto-región-mes')

df.groupby('region')['units_sold'].sum().sort_values().plot(kind='barh', ax=ax[1])
ax[1].set_title('Unidades vendidas por región (2024–2025)')
plt.tight_layout()
plt.show()


# **Interpretación:** la base no tiene nulos ni duplicados. `units_sold` tiene sesgo a la derecha (la mayoría de los registros vende poco y pocos venden mucho) y las ventas se concentran en CDMX, Monterrey y Guadalajara, por lo que la **región** será una variable importante.

# ### 2.1 Preparar la fecha
# La columna `month` viene como texto (January, February…). La convertimos a número y creamos una fecha para poder ordenar los datos en el tiempo.

# In[6]:


meses = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
         'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

df['mes'] = df['month'].map(meses)
df['fecha'] = pd.to_datetime(dict(year=df['year'], month=df['mes'], day=1))

# Ordenar por producto, región y fecha
df = df.sort_values(['product_id', 'region', 'fecha']).reset_index(drop=True)
df[['product_id', 'region', 'fecha', 'units_sold', 'units_expected']].head()


# ### 2.2 Las ventas a través del tiempo
# Antes de modelar vemos cómo se comportan las ventas reales contra lo que DanuStore esperaba vender.

# In[7]:


por_mes = df.groupby('fecha')[['units_sold', 'units_expected']].sum()

plt.figure(figsize=(11, 4))
plt.plot(por_mes.index, por_mes['units_sold'], marker='o', label='Ventas reales (units_sold)')
plt.plot(por_mes.index, por_mes['units_expected'], marker='o', label='Ventas esperadas (units_expected)')
plt.title('Ventas reales vs. esperadas por mes (todas las regiones)')
plt.ylabel('Unidades')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

print('Se vendió el', round(por_mes['units_sold'].sum() / por_mes['units_expected'].sum() * 100, 1), '% de lo esperado')


# In[8]:


por_region_mes = df.groupby(['fecha', 'region'])['units_sold'].sum().unstack()

por_region_mes.plot(figsize=(11, 4), marker='.')
plt.title('Ventas por región a través del tiempo')
plt.ylabel('Unidades')
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)
plt.grid(alpha=0.3)
plt.show()


# **Interpretación:** el pronóstico actual (`units_expected`) es casi plano y muy superior a las ventas reales, mientras que las ventas sí tienen picos (noviembre y diciembre) en todas las regiones, y el patrón de 2025 es igual al de 2024. Esto confirma que hace falta un modelo que aprenda el comportamiento real de las ventas.

# ## 3. Selección de variables
# ### 3.1 Universo de variables
# - **Variable objetivo (y):** `units_sold`.
# - **Variables candidatas:** `region`, `category`, `subcategory`, `mes`, `static_price` y las **ventas de meses anteriores** (rezagos), que creamos a continuación.
# 
# Para pronosticar el mes siguiente solo podemos usar información que **ya conocemos**. Por eso creamos:
# - `ventas_mes_anterior`: ventas del mes pasado (t−1).
# - `ventas_hace_2` y `ventas_hace_3`: ventas de hace 2 y 3 meses.
# - `promedio_3_meses`: promedio de los 3 meses anteriores.

# In[9]:


# Agrupamos por producto y región para que cada serie use SUS propias ventas pasadas
grupo = df.groupby(['product_id', 'region'])['units_sold']

df['ventas_mes_anterior'] = grupo.shift(1)
df['ventas_hace_2'] = grupo.shift(2)
df['ventas_hace_3'] = grupo.shift(3)
df['promedio_3_meses'] = (df['ventas_mes_anterior'] + df['ventas_hace_2'] + df['ventas_hace_3']) / 3
df['ventas_hace_12'] = grupo.shift(12)   # mismo mes del año pasado (solo para revisarla)

df[['product_id', 'region', 'fecha', 'units_sold', 'ventas_mes_anterior', 'promedio_3_meses']].head(6)


# ### 3.2 Variables que NO se pueden usar
# Estas variables se calculan **con las ventas del mismo mes** que queremos pronosticar. Si las usamos, el modelo "haría trampa" (fuga de información) porque en la vida real no las conocemos antes de que termine el mes:
# 
# | Variable | Por qué se excluye |
# |---|---|
# | `Ventas_Acumuladas_Mensual` | Es igual a `units_sold` |
# | `Venta_Promedio_Diaria` | Es `units_sold` ÷ días del mes |
# | `sales_amount` | Es `units_sold` × precio |
# | `Cumplimiento_Venta_Esperada` | Es `units_sold` ÷ `units_expected` |
# | `Dias_Cobertura_Inventario` | Usa la venta promedio diaria |
# | `Stock_Restante_Mensual` | Es stock − `units_sold` |
# 
# `units_expected` tampoco se usa como variable: se usa como **punto de comparación** (es el pronóstico actual de la empresa).

# ### 3.3 Correlaciones más importantes

# In[10]:


variables_numericas = ['units_sold', 'ventas_mes_anterior', 'ventas_hace_2', 'ventas_hace_3',
                       'promedio_3_meses', 'ventas_hace_12', 'units_expected', 'static_price', 'mes']

correlacion = df[variables_numericas].corr(method='spearman')

plt.figure(figsize=(9, 7))
sns.heatmap(correlacion, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlación de Spearman con units_sold')
plt.show()

print(correlacion['units_sold'].sort_values(ascending=False).round(3))


# In[11]:


# ¿Las ventas de 2025 se parecen a las de 2024?
tabla = df.pivot_table(index=['product_id', 'region', 'mes'], columns='year', values='units_sold')
iguales = (tabla[2024] == tabla[2025]).mean() * 100
print('Registros donde las ventas de 2025 son IGUALES a las de 2024:', round(iguales, 1), '%')
print('Diferencia promedio entre 2025 y 2024:', round((tabla[2025] - tabla[2024]).abs().mean(), 2), 'unidades')


# **Interpretación y selección:**
# - Las ventas de los meses anteriores (`ventas_mes_anterior`, `promedio_3_meses`) son las variables más relacionadas con `units_sold`, por eso se seleccionan.
# - `units_expected` tiene una correlación menor: ordena bien qué productos venden más, pero no acierta en la cantidad.
# - `mes` tiene correlación baja por sí sola, pero se conserva porque los árboles pueden encontrar **combinaciones** (por ejemplo, región × mes, o la temporada de noviembre–diciembre) que una correlación no detecta.
# - **`static_price` NO se usa:** cada producto tiene un precio único (ver la celda siguiente), así que el precio funciona como un **identificador del producto**. Como las ventas de 2025 repiten las de 2024, el modelo lo usaría para "recordar" cuánto vendió cada producto en lugar de aprender patrones, y dejaría de funcionar si los precios cambian (descuentos, inflación o productos nuevos). En la sección 12 se comprueba que quitarlo casi no cambia el error.
# - **`ventas_hace_12` NO se usa como variable del modelo:** su correlación es prácticamente 1 porque en la base **las ventas de 2025 repiten casi exactamente las de 2024**. Si la usáramos, el modelo solo copiaría el año anterior y no aprendería ningún patrón útil para cuando los datos no se repitan. Además, solo existe para 2025, lo que dejaría muy pocos meses para entrenar. **Sí se usa como línea base** ("vender lo mismo que hace un año", sección 7.1), porque esa información está disponible al pronosticar. Este hallazgo se reportará al socio formador como una observación sobre la calidad de los datos.
# 
# **Variables seleccionadas:** `region`, `category`, `subcategory`, `mes`, `ventas_mes_anterior`, `ventas_hace_2`, `ventas_hace_3`, `promedio_3_meses`.

# In[12]:


# ¿El precio identifica al producto?
print('Productos distintos:', df['product_id'].nunique())
print('Precios distintos:', df['static_price'].nunique())
print('¿Cada producto tiene un solo precio?', (df.groupby('product_id')['static_price'].nunique() == 1).all())


# ## 4. Codificar variables categóricas
# Los modelos solo entienden números. `region`, `category` y `subcategory` son texto, así que se convierten con **One-Hot Encoding** (`pd.get_dummies`): se crea una columna de 0 y 1 por cada categoría.

# In[13]:


# Quitamos los 3 primeros meses de cada serie (no tienen ventas anteriores para calcular los rezagos)
datos = df.dropna(subset=['promedio_3_meses']).copy()

variables = ['region', 'category', 'subcategory', 'mes',
             'ventas_mes_anterior', 'ventas_hace_2', 'ventas_hace_3', 'promedio_3_meses']

X = pd.get_dummies(datos[variables], columns=['region', 'category', 'subcategory'], dtype=int)
y = datos['units_sold']

print('Registros:', X.shape[0], '| Columnas después de codificar:', X.shape[1])
X.head()


# ## 5. Normalización / estandarización
# **No es necesaria.** Random Forest y XGBoost son modelos de **árboles de decisión**: separan los datos con reglas del tipo "¿ventas del mes anterior > 150?". Esas reglas funcionan igual si la variable está en unidades, en miles o estandarizada, así que la escala no cambia el resultado. La normalización sí sería necesaria en modelos que comparan distancias o usan coeficientes, como KNN, regresión lineal regularizada (Ridge/Lasso) o redes neuronales.

# ## 6. Partición de los datos (temporal)
# Como queremos pronosticar el **futuro**, no se usa una partición aleatoria: se entrena con los meses más antiguos y se prueba con los más recientes. Se prueban **tres particiones** (los datos con rezagos van de abril 2024 a diciembre 2025, 21 meses):
# - **80/20:** entrenar hasta agosto 2025 (17 meses) y probar con septiembre–diciembre 2025 (4 meses).
# - **70/30:** entrenar hasta junio 2025 (15 meses) y probar con julio–diciembre 2025 (6 meses).
# - **60/40:** entrenar hasta abril 2025 (13 meses) y probar con mayo–diciembre 2025 (8 meses).
# 
# **Importante:** en las secciones 7 a 12 la evaluación es **a un mes**: para pronosticar cada mes de prueba se usan las ventas **reales** del mes anterior, como pasaría si DanuStore pronostica cada mes cuando ya cerró el anterior. El pronóstico de varios meses desde un solo punto, sin conocer las ventas intermedias, se evalúa en la sección 13.
# 
# Las tres particiones tienen **periodos de prueba distintos y que se enciman** (septiembre–diciembre, julio–diciembre y mayo–diciembre), así que sus errores no se pueden comparar directamente para decir que una es "mejor": las diferencias pueden deberse a los meses que se evalúan (por ejemplo, la temporada de noviembre–diciembre). Sirven para ver si el modelo es **estable** con distintas cantidades de datos.

# In[14]:


particiones = {
    '80/20': '2025-09-01',
    '70/30': '2025-07-01',
    '60/40': '2025-05-01',
}

for nombre, corte in particiones.items():
    entrenamiento = datos['fecha'] < corte
    print(nombre, '-> entrenamiento:', entrenamiento.sum(), 'registros | prueba:', (~entrenamiento).sum(), 'registros')


# ## 7. Métricas de evaluación
# - **MAE:** error promedio en unidades.
# - **RMSE:** como el MAE, pero castiga más los errores grandes.
# - **WAPE:** error total ÷ ventas totales (en %). Es la métrica principal porque se lee fácil: "el pronóstico se equivoca X% de lo que se vende".
# - **R²:** qué tanto de la variación de las ventas explica el modelo (1 = perfecto).

# In[15]:


def evaluar(y_real, y_pred):
    mae = mean_absolute_error(y_real, y_pred)
    rmse = np.sqrt(mean_squared_error(y_real, y_pred))
    wape = np.abs(y_real - y_pred).sum() / y_real.sum() * 100
    r2 = r2_score(y_real, y_pred)
    return {'MAE': round(float(mae), 2), 'RMSE': round(float(rmse), 2), 'WAPE (%)': round(float(wape), 2), 'R2': round(float(r2), 3)}


# ### 7.1 Puntos de comparación (líneas base)
# Un modelo solo sirve si le gana a lo que ya existe:
# 1. **Pronóstico actual de DanuStore** (`units_expected`).
# 2. **Modelo ingenuo:** "este mes voy a vender lo mismo que el mes pasado".
# 3. **Ingenuo estacional:** "este mes voy a vender lo mismo que en el mismo mes del año pasado".

# In[16]:


resultados = []

for nombre, corte in particiones.items():
    prueba = datos['fecha'] >= corte
    fila = evaluar(y[prueba], datos.loc[prueba, 'units_expected'])
    fila.update({'Modelo': 'Pronóstico actual (units_expected)', 'Partición': nombre, 'Hiperparámetros': '-'})
    resultados.append(fila)

    fila = evaluar(y[prueba], datos.loc[prueba, 'ventas_mes_anterior'])
    fila.update({'Modelo': 'Ingenuo (mes anterior)', 'Partición': nombre, 'Hiperparámetros': '-'})
    resultados.append(fila)

    fila = evaluar(y[prueba], datos.loc[prueba, 'ventas_hace_12'])
    fila.update({'Modelo': 'Ingenuo estacional (mismo mes del año anterior)', 'Partición': nombre, 'Hiperparámetros': '-'})
    resultados.append(fila)

pd.DataFrame(resultados)[['Partición', 'Modelo', 'Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]


# **Interpretación de las líneas base:**
# - El pronóstico actual de DanuStore se equivoca ~470 %, y repetir el mes pasado ~19 %.
# - **Repetir el mismo mes del año pasado se equivoca menos del 0.5 %.** Esto no es porque sea un buen método en general, sino porque **en esta base las ventas de 2025 son casi una copia de las de 2024** (sección 3.3). Con estos datos, ningún modelo puede superarlo, y es la principal limitante del análisis: se reportará al socio formador.
# - Por eso los modelos de ML se construyen **sin** las ventas del año anterior: el objetivo es que aprendan patrones (nivel de ventas reciente, región, temporada) que sigan funcionando cuando las ventas de un año no repitan las del anterior.

# ## 8. Modelo 1: Random Forest
# Entrena muchos árboles de decisión, cada uno con una muestra aleatoria de los datos, y **promedia** sus pronósticos.
# 
# Hiperparámetros que se prueban:
# - `n_estimators`: número de árboles.
# - `max_depth`: profundidad máxima de cada árbol (None = sin límite).
# - `min_samples_leaf`: mínimo de registros en cada hoja (evita que el árbol memorice).

# In[17]:


configuraciones_rf = [
    {'n_estimators': 100, 'max_depth': None, 'min_samples_leaf': 1},
    {'n_estimators': 200, 'max_depth': 15,   'min_samples_leaf': 2},
    {'n_estimators': 300, 'max_depth': 8,    'min_samples_leaf': 5},
]

for nombre, corte in particiones.items():
    entrenamiento = datos['fecha'] < corte
    prueba = datos['fecha'] >= corte

    for config in configuraciones_rf:
        modelo = RandomForestRegressor(**config, random_state=42, n_jobs=-1)
        modelo.fit(X[entrenamiento], y[entrenamiento])
        prediccion = modelo.predict(X[prueba])

        fila = evaluar(y[prueba], prediccion)
        fila.update({'Modelo': 'Random Forest', 'Partición': nombre, 'Hiperparámetros': ', '.join(f'{k}={v}' for k, v in config.items())})
        resultados.append(fila)

tabla_rf = pd.DataFrame(resultados)
tabla_rf[tabla_rf['Modelo'] == 'Random Forest'][['Partición', 'Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]


# ## 9. Modelo 2: XGBoost
# Construye árboles **uno tras otro**; cada árbol nuevo corrige los errores de los anteriores.
# 
# Hiperparámetros que se prueban:
# - `n_estimators`: número de árboles.
# - `learning_rate`: qué tanto corrige cada árbol (más bajo = más lento pero más cuidadoso).
# - `max_depth`: profundidad máxima de cada árbol.

# In[18]:


configuraciones_xgb = [
    {'n_estimators': 300, 'learning_rate': 0.1,  'max_depth': 6},
    {'n_estimators': 500, 'learning_rate': 0.05, 'max_depth': 4},
    {'n_estimators': 800, 'learning_rate': 0.03, 'max_depth': 8},
]

for nombre, corte in particiones.items():
    entrenamiento = datos['fecha'] < corte
    prueba = datos['fecha'] >= corte

    for config in configuraciones_xgb:
        modelo = XGBRegressor(**config, random_state=42)
        modelo.fit(X[entrenamiento], y[entrenamiento])
        prediccion = modelo.predict(X[prueba])

        fila = evaluar(y[prueba], prediccion)
        fila.update({'Modelo': 'XGBoost', 'Partición': nombre, 'Hiperparámetros': ', '.join(f'{k}={v}' for k, v in config.items())})
        resultados.append(fila)

tabla_xgb = pd.DataFrame(resultados)
tabla_xgb[tabla_xgb['Modelo'] == 'XGBoost'][['Partición', 'Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]


# ## 10. Comparación de todos los modelos

# In[19]:


tabla_final = pd.DataFrame(resultados)[['Partición', 'Modelo', 'Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]
tabla_final = tabla_final.sort_values(['Partición', 'WAPE (%)']).reset_index(drop=True)
tabla_final


# In[20]:


# Menor WAPE (%) de cada modelo en cada partición
resumen = tabla_final.groupby(['Modelo', 'Partición'])['WAPE (%)'].min().unstack()
resumen = resumen[['80/20', '70/30', '60/40']].sort_values('80/20')
resumen


# In[21]:


# Mejor configuración de cada modelo en la partición 80/20
mejores = tabla_final[tabla_final['Partición'] == '80/20'].groupby('Modelo').first().sort_values('WAPE (%)')
mejores[['Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]


# ### 10.1 Elección de hiperparámetros sin usar los datos de prueba
# En las tablas anteriores se eligió la mejor configuración viendo directamente el error en los meses de prueba, lo cual puede dar un resultado **optimista**. Para elegir de forma correcta:
# 1. Se reservan **septiembre–diciembre 2025 como prueba final** y no se usan para decidir.
# 2. Dentro del entrenamiento se separa una **validación**: se entrena hasta abril 2025 y se evalúa con mayo–agosto 2025.
# 3. Se elige la configuración con menor error en validación y después se mide **una sola vez** en la prueba final (sección 11).

# In[22]:


inicio_validacion = '2025-05-01'
inicio_prueba = '2025-09-01'
entrenamiento_val = datos['fecha'] < inicio_validacion
validacion = (datos['fecha'] >= inicio_validacion) & (datos['fecha'] < inicio_prueba)

tabla_validacion = []
for config in configuraciones_rf:
    modelo = RandomForestRegressor(**config, random_state=42, n_jobs=-1)
    modelo.fit(X[entrenamiento_val], y[entrenamiento_val])
    fila = evaluar(y[validacion], modelo.predict(X[validacion]))
    fila.update({'Modelo': 'Random Forest', 'Hiperparámetros': ', '.join(f'{k}={v}' for k, v in config.items())})
    tabla_validacion.append(fila)

for config in configuraciones_xgb:
    modelo = XGBRegressor(**config, random_state=42)
    modelo.fit(X[entrenamiento_val], y[entrenamiento_val])
    fila = evaluar(y[validacion], modelo.predict(X[validacion]))
    fila.update({'Modelo': 'XGBoost', 'Hiperparámetros': ', '.join(f'{k}={v}' for k, v in config.items())})
    tabla_validacion.append(fila)

tabla_validacion = pd.DataFrame(tabla_validacion)[['Modelo', 'Hiperparámetros', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]
print('Error en VALIDACIÓN (mayo–agosto 2025):')
tabla_validacion.sort_values(['Modelo', 'WAPE (%)'])


# **Resultado:** en validación también ganan **Random Forest con 100 árboles sin límite de profundidad** y **XGBoost con 800 árboles, `learning_rate` = 0.03 y `max_depth` = 8**. Es decir, la elección no dependió de ver los datos de prueba. Estas configuraciones se entrenan con todo el periodo hasta agosto 2025 y se evalúan en la prueba final (septiembre–diciembre 2025).

# ## 11. Resultados de los mejores modelos
# Se entrenan las configuraciones elegidas en validación con todos los datos hasta agosto 2025 y se evalúan **una sola vez** en la prueba final (septiembre–diciembre 2025, partición 80/20).

# In[23]:


corte = '2025-09-01'
entrenamiento = datos['fecha'] < corte
prueba = datos['fecha'] >= corte

mejor_rf = RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_leaf=1, random_state=42, n_jobs=-1)
mejor_rf.fit(X[entrenamiento], y[entrenamiento])

mejor_xgb = XGBRegressor(n_estimators=800, learning_rate=0.03, max_depth=8, random_state=42)
mejor_xgb.fit(X[entrenamiento], y[entrenamiento])

resultado = datos.loc[prueba, ['fecha', 'region', 'units_sold', 'units_expected']].copy()
resultado['pronostico_rf'] = mejor_rf.predict(X[prueba])
resultado['pronostico_xgb'] = mejor_xgb.predict(X[prueba])

print('Resultado en la PRUEBA FINAL (septiembre–diciembre 2025):')
print('Random Forest:', evaluar(resultado['units_sold'], resultado['pronostico_rf']))
print('XGBoost:      ', evaluar(resultado['units_sold'], resultado['pronostico_xgb']))

# Total por mes: real vs. pronósticos de los dos modelos
total_mes = resultado.groupby('fecha')[['units_sold', 'pronostico_rf', 'pronostico_xgb', 'units_expected']].sum()

plt.figure(figsize=(10, 4))
plt.plot(total_mes.index, total_mes['units_sold'], marker='o', label='Ventas reales')
plt.plot(total_mes.index, total_mes['pronostico_rf'], marker='o', linestyle='--', label='Pronóstico Random Forest')
plt.plot(total_mes.index, total_mes['pronostico_xgb'], marker='o', linestyle=':', label='Pronóstico XGBoost')
plt.title('Septiembre–diciembre 2025: ventas reales vs. pronósticos')
plt.ylabel('Unidades')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# El pronóstico actual no se grafica porque es ~6 veces mayor y aplastaría la escala
total_mes.round(0)


# In[24]:


# Valores reales vs. estimados y residuales (residual = real - estimado) de los dos modelos
fig, ax = plt.subplots(2, 3, figsize=(15, 8))

for fila, (nombre, columna) in enumerate([('Random Forest', 'pronostico_rf'), ('XGBoost', 'pronostico_xgb')]):
    residual = resultado['units_sold'] - resultado[columna]

    # 1) Real vs. estimado: si el modelo fuera perfecto, todos los puntos caerían en la línea roja
    ax[fila, 0].scatter(resultado['units_sold'], resultado[columna], s=5, alpha=0.4)
    maximo = resultado['units_sold'].max()
    ax[fila, 0].plot([0, maximo], [0, maximo], color='red')
    ax[fila, 0].set_title(f'Real vs. estimado ({nombre})')
    ax[fila, 0].set_xlabel('Unidades reales')
    ax[fila, 0].set_ylabel('Unidades estimadas')

    # 2) Distribución de los residuales: deberían estar centrados en 0
    ax[fila, 1].hist(residual, bins=50)
    ax[fila, 1].axvline(0, color='red')
    ax[fila, 1].set_title(f'Distribución de los residuales ({nombre})')
    ax[fila, 1].set_xlabel('Real - estimado (unidades)')

    # 3) Residuales vs. estimado: no debería haber un patrón
    ax[fila, 2].scatter(resultado[columna], residual, s=5, alpha=0.4)
    ax[fila, 2].axhline(0, color='red')
    ax[fila, 2].set_title(f'Residuales vs. estimado ({nombre})')
    ax[fila, 2].set_xlabel('Unidades estimadas')
    ax[fila, 2].set_ylabel('Residual')

    print(f'{nombre}: residual promedio = {residual.mean():.2f} unidades; '
          f'el 90% de los errores está entre {residual.quantile(0.05):.1f} y {residual.quantile(0.95):.1f} unidades')

plt.tight_layout()
plt.show()


# In[25]:


# Error de los dos modelos por región
resultado['error_rf'] = np.abs(resultado['units_sold'] - resultado['pronostico_rf'])
resultado['error_xgb'] = np.abs(resultado['units_sold'] - resultado['pronostico_xgb'])

sumas = resultado.groupby('region')[['units_sold', 'error_rf', 'error_xgb']].sum()
por_region = pd.DataFrame({
    'Random Forest': sumas['error_rf'] / sumas['units_sold'] * 100,
    'XGBoost': sumas['error_xgb'] / sumas['units_sold'] * 100,
}).round(2)
print('WAPE (%) por región:')
por_region.sort_values('Random Forest')


# In[26]:


# ¿Qué variables usa más el modelo? (segundo método de selección de variables)
importancia = pd.Series(mejor_rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)

plt.figure(figsize=(8, 4))
importancia.sort_values().plot(kind='barh')
plt.title('Las 10 variables más importantes (Random Forest)')
plt.xlabel('Importancia')
plt.show()


# ## 12. Impacto del preprocesamiento
# Para medir qué tanto ayudó la preparación de los datos, se entrenan los dos modelos (partición 80/20, mejores hiperparámetros) con **4 grupos de variables**:
# 1. **Básicas:** región, categoría, subcategoría y mes (codificadas con One-Hot).
# 2. **Básicas + precio** (el precio como identificador del producto).
# 3. **Básicas + ventas pasadas** (las variables creadas en el preprocesamiento): **modelo final**.
# 4. **Básicas + ventas pasadas + precio** (prueba de robustez: ¿cuánto aporta el precio?).

# In[27]:


corte = '2025-09-01'
entrenamiento = datos['fecha'] < corte
prueba = datos['fecha'] >= corte

basicas = ['region', 'category', 'subcategory', 'mes']
rezagos = ['ventas_mes_anterior', 'ventas_hace_2', 'ventas_hace_3', 'promedio_3_meses']
grupos = {
    '1. Básicas': basicas,
    '2. Básicas + precio': basicas + ['static_price'],
    '3. Básicas + ventas pasadas (modelo final)': basicas + rezagos,
    '4. Básicas + ventas pasadas + precio': basicas + rezagos + ['static_price'],
}
modelos = {
    'Random Forest': lambda: RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'XGBoost': lambda: XGBRegressor(n_estimators=800, learning_rate=0.03, max_depth=8, random_state=42),
}

comparacion = []
for nombre_modelo, crear_modelo in modelos.items():
    for nombre_grupo, columnas in grupos.items():
        X_grupo = pd.get_dummies(datos[columnas], columns=['region', 'category', 'subcategory'], dtype=int)
        modelo = crear_modelo()
        modelo.fit(X_grupo[entrenamiento], y[entrenamiento])
        fila = evaluar(y[prueba], modelo.predict(X_grupo[prueba]))
        fila.update({'Modelo': nombre_modelo, 'Variables': nombre_grupo})
        comparacion.append(fila)

pd.DataFrame(comparacion)[['Modelo', 'Variables', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]


# **Interpretación:**
# - Con solo las variables **básicas** el error es alto: el modelo sabe la región, la categoría y el mes, pero no cuánto vende cada producto.
# - Con el **precio** el error baja mucho, pero no porque el precio explique las ventas: el modelo lo usa para **reconocer el producto** y "recordar" lo que vendió en 2024, que se repite en 2025.
# - Con las **ventas pasadas** (creadas en el preprocesamiento) el error baja casi igual **sin identificar el producto**: el modelo aprende del nivel de ventas reciente de cada serie.
# - **Prueba de robustez:** agregar el precio a las ventas pasadas casi no cambia el error. Es decir, el modelo final no depende del precio, y por eso se excluyó: así sigue funcionando si los precios cambian o entran productos nuevos.

# ## 13. Pronóstico de varios meses (recursivo)
# Hasta aquí, para pronosticar cada mes de prueba el modelo usó las **ventas reales** del mes anterior (pronóstico a **un mes**). En la vida real, si DanuStore quiere planear septiembre–diciembre desde agosto, todavía no conoce las ventas de septiembre, octubre ni noviembre.
# 
# Por eso se hace un **pronóstico recursivo**: se pronostica septiembre; ese pronóstico se usa como "venta del mes anterior" para pronosticar octubre, y así sucesivamente. Los errores se van acumulando, así que este es el **error realista para planear varios meses**.

# In[28]:


corte = '2025-09-01'
meses_prueba = sorted(df.loc[df['fecha'] >= corte, 'fecha'].unique())

def calcular_rezagos(tabla, columna):
    grupo = tabla.groupby(['product_id', 'region'])[columna]
    tabla['ventas_mes_anterior'] = grupo.shift(1)
    tabla['ventas_hace_2'] = grupo.shift(2)
    tabla['ventas_hace_3'] = grupo.shift(3)
    tabla['promedio_3_meses'] = (tabla['ventas_mes_anterior'] + tabla['ventas_hace_2'] + tabla['ventas_hace_3']) / 3
    return tabla

recursivo = []
for nombre, modelo in [('Random Forest', mejor_rf), ('XGBoost', mejor_xgb)]:
    # Historia: ventas reales hasta agosto 2025; desde septiembre se llenan con los pronósticos
    historia = df.copy()
    historia['ventas_simuladas'] = historia['units_sold'].where(historia['fecha'] < corte)

    for mes_prueba in meses_prueba:
        historia = calcular_rezagos(historia, 'ventas_simuladas')
        filas = historia['fecha'] == mes_prueba
        X_mes = pd.get_dummies(historia.loc[filas, variables], columns=['region', 'category', 'subcategory'], dtype=int)
        X_mes = X_mes.reindex(columns=X.columns, fill_value=0)   # mismas columnas que en el entrenamiento
        historia.loc[filas, 'ventas_simuladas'] = modelo.predict(X_mes)

    prueba_rec = historia[historia['fecha'] >= corte]
    for mes_prueba in meses_prueba:
        m = prueba_rec[prueba_rec['fecha'] == mes_prueba]
        fila = evaluar(m['units_sold'], m['ventas_simuladas'])
        fila.update({'Modelo': nombre, 'Mes': str(mes_prueba)[:7], 'Meses adelante': meses_prueba.index(mes_prueba) + 1})
        recursivo.append(fila)
    fila = evaluar(prueba_rec['units_sold'], prueba_rec['ventas_simuladas'])
    fila.update({'Modelo': nombre, 'Mes': 'Total sep–dic', 'Meses adelante': '1 a 4'})
    recursivo.append(fila)

tabla_recursiva = pd.DataFrame(recursivo)[['Modelo', 'Mes', 'Meses adelante', 'MAE', 'RMSE', 'WAPE (%)', 'R2']]
tabla_recursiva


# In[29]:


# Comparación: error a un mes vs. error recursivo (sep–dic 2025)
resumen_rec = pd.DataFrame({
    'A un mes (ventas reales)': [evaluar(resultado['units_sold'], resultado['pronostico_rf'])['WAPE (%)'],
                                 evaluar(resultado['units_sold'], resultado['pronostico_xgb'])['WAPE (%)']],
    'Recursivo (4 meses)': tabla_recursiva[tabla_recursiva['Mes'] == 'Total sep–dic']['WAPE (%)'].values,
}, index=['Random Forest', 'XGBoost'])
resumen_rec.loc['Pronóstico actual (units_expected)'] = evaluar(resultado['units_sold'], resultado['units_expected'])['WAPE (%)']
print('WAPE (%) en septiembre–diciembre 2025:')
resumen_rec


# **Interpretación:** al pronosticar varios meses con sus propios pronósticos, el error **crece mes a mes** porque los errores se acumulan. Aun así, el error total de 4 meses sigue siendo mucho menor que el del pronóstico actual de DanuStore. Este es el número que debería usar el área de planeación.

# ## 14. Conclusiones
# **Resultados por partición (WAPE a un mes):**
# 
# | Partición | Ingenuo estacional (año anterior) | Random Forest | XGBoost | Ingenuo (mes anterior) | Pronóstico actual |
# |---|---|---|---|---|---|
# | 80/20 | 0.29 % | **5.98 %** | 6.58 % | 19.8 % | 468 % |
# | 70/30 | 0.31 % | **6.07 %** | 6.97 % | 18.7 % | 471 % |
# | 60/40 | 0.30 % | **6.12 %** | 7.05 % | 18.2 % | 483 % |
# 
# **¿Qué modelo y qué división funcionaron mejor?**
# - **Entre los modelos de ML evaluados, el mejor es Random Forest** (100 árboles, sin límite de profundidad). Tiene el menor WAPE en las tres particiones y también ganó en la **validación** (mayo–agosto 2025), así que la elección no dependió de ver los datos de prueba. En la prueba final (septiembre–diciembre 2025) obtuvo un WAPE de 5.98 %, un MAE de 13.31 unidades y un R² de 0.988.
# - **XGBoost** quedó cerca (6.58 %, mismo R² y RMSE ligeramente menor, 20.54 contra 20.80), pero su error es menos parejo entre regiones: Random Forest va de 5.2 % a 8.2 %, y XGBoost de 3.6 % a 12.7 %.
# - **Particiones:** los resultados son muy parecidos en las tres (5.98 % a 6.12 % para Random Forest). Como los periodos de prueba son distintos y se enciman, **no se puede afirmar que una división sea mejor**; lo que muestran es que el modelo es **estable**, incluso entrenando con solo 13 meses.
# - **Ambos modelos le ganan por mucho al pronóstico actual de DanuStore** (~470 %) y a repetir el mes pasado (~19 %).
# - **Pero ninguno le gana a repetir el mismo mes del año anterior (~0.3 %).** Esto se debe a que en esta base **las ventas de 2025 son casi una copia de las de 2024** (76.6 % de los registros son idénticos). Con estos datos, la mejor predicción posible es copiar el año anterior. Los modelos de ML se construyeron sin esa información para que aprendan patrones que sigan sirviendo cuando las ventas no se repitan, que es lo normal en la vida real.
# - **Pronóstico de varios meses:** si se pronostica septiembre–diciembre desde agosto, usando los propios pronósticos como entrada, el error de Random Forest sube mes a mes (5.8 %, 9.4 %, 10.9 % y 12.3 %) y queda en **9.9 %** en total.
# - **Residuales:** en los dos modelos están centrados en 0 y el 90 % de los errores está entre −30 y +33 unidades, sin un patrón visible.
# 
# **¿Qué impacto tuvo el preprocesamiento?**
# - **Crear las ventas pasadas** fue lo más importante. Con solo región, categoría, subcategoría y mes el error es de **22.6 %**; con las ventas pasadas baja a **6.0 %** en Random Forest y 6.6 % en XGBoost.
# - **Excluir `static_price`:** como cada producto tiene un precio único, el precio funcionaba como identificador del producto. La prueba de robustez muestra que quitarlo casi no cambia el error (5.87 % con precio contra 5.98 % sin él), así que el modelo no depende de él.
# - **Excluir las variables con fuga** (Ventas_Acumuladas, Venta_Promedio_Diaria, Cumplimiento, etc.) evita un modelo "perfecto" pero inútil en la vida real.
# - **El One-Hot Encoding** permitió usar región, categoría y subcategoría. **La normalización no fue necesaria** porque los modelos de árboles no dependen de la escala.
# 
# **¿Qué impacto tuvo el ajuste de hiperparámetros?**
# Se compararon **configuraciones completas** (en cada una cambian varios hiperparámetros a la vez), así que no se puede atribuir la diferencia a un solo parámetro. Lo que sí se observa:
# - **Random Forest:** las configuraciones con árboles más limitados (menor `max_depth`, mayor `min_samples_leaf`) tuvieron más error: 5.98 % sin límite, 7.44 % con `max_depth` = 15 y 12.10 % con `max_depth` = 8 (partición 80/20).
# - **XGBoost:** la configuración con árboles poco profundos (`max_depth` = 4) tuvo 11.79 %, y la de 800 árboles, `learning_rate` = 0.03 y `max_depth` = 8 bajó a 6.58 %.
# - En los dos casos, las configuraciones más flexibles funcionaron mejor, lo cual tiene sentido porque necesitan distinguir 910 combinaciones de producto y región.
# 
# **Beneficio para DanuStore:** con un pronóstico basado en las ventas reales recientes, la región y la temporada, puede planear su stock según lo que realmente se va a vender, en lugar de un pronóstico plano e inflado, y así reducir el sobreinventario (según el análisis de la investigación 5.1, hoy el stock alcanza para ~208 días de venta real en lugar de los ~34 planeados).
# 
# **Limitantes:**
# 1. **Las ventas de 2025 repiten casi exactamente las de 2024.** Por eso repetir el año anterior es casi perfecto y los errores de los modelos son **optimistas**. Hay que confirmar con DanuStore si estos datos son reales y validar el modelo con datos nuevos antes de usarlo.
# 2. Las ventas son solo de clientes registrados.
# 3. El error crece con el horizonte (~6 % a un mes y ~10 % a cuatro meses). Lo recomendable es reentrenar y pronosticar cada mes con las ventas reales más recientes.
