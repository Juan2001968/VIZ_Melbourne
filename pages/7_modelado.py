# =========================================
# 7. Modelado predictivo del precio de la vivienda
# =========================================
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from joblib import load

from utils_melb import PALETTE, ACCENT

# Rutas de artefactos del modelo pre-entrenado
MODELS_DIR = Path("models")
MODEL_PATH = MODELS_DIR / "melb_model.pkl"
METRICS_PATH = MODELS_DIR / "melb_metrics.json"
PRED_PATH = MODELS_DIR / "melb_test_predictions.csv"

st.title("7. Modelado predictivo del precio de la vivienda")

st.markdown(
    """
En esta sección presentamos un **modelo de regresión supervisada** entrenado a partir del 
dataset de viviendas de Melbourne.  

El objetivo es **predecir el precio de una vivienda (`Price`)** utilizando como predictores
características estructurales (Rooms, Bathroom, Car, BuildingArea, etc.) y de ubicación
(Suburb, Postcode, Regionname, Lattitude, Longtitude, entre otras).

El entrenamiento del modelo se realizó **por fuera del dashboard** mediante el script
`train_model_melb.py`, y aquí solo **cargamos los artefactos ya entrenados** para analizar
sus resultados.
"""
)

# ---------------------------------------------------------------------
# 1. Verificación de artefactos
# ---------------------------------------------------------------------
missing = []
for p in (MODEL_PATH, METRICS_PATH, PRED_PATH):
    if not p.exists():
        missing.append(str(p))

if missing:
    st.error(
        "No se encontraron los archivos del modelo pre-entrenado necesarios para esta sección.\n\n"
        "Verifica que has ejecutado el script `train_model_melb.py` desde la raíz del proyecto "
        "y que existen los siguientes archivos:\n\n"
        + "\n".join(f"- `{m}`" for m in missing)
    )
    st.stop()

# ---------------------------------------------------------------------
# 2. Cargar modelo, métricas y predicciones
# ---------------------------------------------------------------------
with open(METRICS_PATH, "r", encoding="utf-8") as f:
    metrics_info = json.load(f)

best_model_name = metrics_info.get("mejor_modelo", "desconocido")
results = metrics_info.get("resultados", {})

df_pred = pd.read_csv(PRED_PATH)

# ---------------------------------------------------------------------
# 3. Resumen de desempeño del modelo
# ---------------------------------------------------------------------
st.subheader("7.1 Desempeño del modelo seleccionado")

col1, col2 = st.columns(2)

best_mae = results.get(best_model_name, {}).get("MAE", None)
best_r2 = results.get(best_model_name, {}).get("R2", None)

with col1:
    st.markdown("#### Modelo seleccionado")
    st.markdown(f"- **Mejor modelo:** `{best_model_name}`")
    if best_mae is not None and best_r2 is not None:
        st.markdown(
            f"""
- **MAE (Error absoluto medio):** {best_mae:,.0f} AUD  
- **R² (coeficiente de determinación):** {best_r2:.3f}
"""
        )

with col2:
    st.markdown("#### Comparación de modelos")
    if results:
        df_metrics = (
            pd.DataFrame(results)
            .T.reset_index()
            .rename(columns={"index": "Modelo"})
        )
        st.dataframe(df_metrics, use_container_width=True)
    else:
        st.info("No se encontraron métricas detalladas en el archivo JSON.")

st.markdown(
    """
En términos generales, un **MAE más bajo** indica que las predicciones se aproximan mejor
a los precios reales promedio; mientras que un **R² cercano a 1** sugiere que el modelo
logra explicar una gran proporción de la variabilidad en el precio de las viviendas.
"""
)

# ---------------------------------------------------------------------
# 4. Gráfico: Precio real vs. precio predicho
# ---------------------------------------------------------------------
st.subheader("7.2 Relación entre precio real y precio predicho")

if {"Price_real", "Price_pred"}.issubset(df_pred.columns):
    fig_scatter = px.scatter(
        df_pred,
        x="Price_real",
        y="Price_pred",
        labels={
            "Price_real": "Precio real (AUD)",
            "Price_pred": "Precio predicho (AUD)",
        },
        opacity=0.6,
        color_discrete_sequence=[PALETTE[-1]],
        title="Dispersión de precios reales vs. predichos",
    )

    # Línea de referencia y = x (predicción perfecta)
    min_val = float(
        min(df_pred["Price_real"].min(), df_pred["Price_pred"].min())
    )
    max_val = float(
        max(df_pred["Price_real"].max(), df_pred["Price_pred"].max())
    )
    fig_scatter.add_shape(
        type="line",
        x0=min_val,
        y0=min_val,
        x1=max_val,
        y1=max_val,
        line=dict(dash="dash", width=1),
    )

    fig_scatter.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown(
        """
En un modelo ideal, todos los puntos se ubicarían **sobre la línea diagonal** (y = x),
lo que implicaría que el precio predicho coincide exactamente con el real.
  
En la práctica, observamos cierta dispersión alrededor de esa línea, pero con una tendencia
marcada que indica que el modelo captura adecuadamente el patrón general de los precios.
"""
    )
else:
    st.warning(
        "El archivo de predicciones no contiene las columnas `Price_real` y `Price_pred`."
    )

# ---------------------------------------------------------------------
# 5. Distribución del error de predicción
# ---------------------------------------------------------------------
st.subheader("7.3 Distribución del error de predicción")

if "Error" in df_pred.columns:
    fig_hist = px.histogram(
        df_pred,
        x="Error",
        nbins=40,
        labels={"Error": "Error (Price_real − Price_pred) [AUD]"},
        color_discrete_sequence=[PALETTE[3]],
        title="Histograma del error de predicción",
    )
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        """
El **error** se define como la diferencia entre el precio real y el precio predicho 
(`Price_real − Price_pred`).  

- Valores **cercanos a 0** indican predicciones muy precisas.  
- Valores **positivos** indican que el modelo **subestima** el precio real.  
- Valores **negativos** indican que el modelo **sobreestima** el precio.  

Un histograma relativamente concentrado alrededor de 0 sugiere un buen desempeño global
del modelo, aunque pueden existir casos puntuales con errores altos que conviene analizar.
"""
    )
else:
    st.warning(
        "El archivo de predicciones no contiene la columna `Error` para analizar la distribución."
    )

# ---------------------------------------------------------------------
# 6. Vista geográfica opcional del error (si hay coordenadas)
# ---------------------------------------------------------------------
st.subheader("7.4 Error de predicción en el espacio geográfico")

if {"Lattitude", "Longtitude"}.issubset(df_pred.columns):
    df_map = df_pred.copy()
    df_map = df_map.rename(columns={"Lattitude": "lat", "Longtitude": "lon"})

    st.markdown(
        """
A continuación se muestra un mapa simple con la ubicación de las viviendas del conjunto
de prueba, coloreadas según el **error de predicción**.  

Esto permite explorar si existen **zonas de la ciudad donde el modelo tiende a fallar más**,
lo cual puede estar asociado a patrones urbanos específicos o a la falta de variables
explicativas adicionales.
"""
    )

    # Para evitar mapas muy pesados, se puede muestrear si hay demasiados puntos
    if len(df_map) > 5000:
        df_map_sample = df_map.sample(5000, random_state=42)
    else:
        df_map_sample = df_map

    # Normalizar error para mostrarlo en una columna aparte (no afecta st.map)
    df_map_sample["error_abs"] = df_map_sample["Error"].abs()

    st.map(df_map_sample[["lat", "lon", "error_abs"]])

else:
    st.info(
        "El archivo de predicciones no contiene columnas de coordenadas "
        "`Lattitude` y `Longtitude`. Por tanto, no se muestra el mapa geográfico de errores."
    )

# ---------------------------------------------------------------------
# 7. Descarga de predicciones
# ---------------------------------------------------------------------
st.subheader("7.5 Descargar predicciones del modelo")

csv_bytes = df_pred.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar CSV con precios reales, predichos y error",
    data=csv_bytes,
    file_name="melbourne_predicciones_modelo.csv",
    mime="text/csv",
)

st.markdown(
    """
El archivo descargado incluye, para cada vivienda del conjunto de prueba:

- **Precio real (`Price_real`)**  
- **Precio predicho (`Price_pred`)**  
- **Error (`Price_real − Price_pred`)**  
- Variables explicativas utilizadas por el modelo (Rooms, Distance, BuildingArea, etc.)  

Esto permite realizar análisis adicionales fuera del dashboard, por ejemplo en un notebook
de Jupyter o en otro entorno analítico.
"""
)
# ---------------------------------------------------------------------
# 8. Limitaciones y consideraciones finales
# ---------------------------------------------------------------------
st.subheader("7.6 Limitaciones y consideraciones finales")

st.markdown(
    """
Aunque el desempeño del modelo es adecuado para capturar el **comportamiento general**
del precio de la vivienda en Melbourne, es importante tener en cuenta varias
**limitaciones**:

- El modelo se entrena únicamente con las variables disponibles en el dataset 
  (características físicas y algunas variables de localización).  
  No incorpora factores externos como:
  - estado interno de la vivienda,  
  - remodelaciones recientes,  
  - dinámica específica del mercado en cada barrio,  
  - tasas de interés o condiciones macroeconómicas.

- Se trabaja con un **conjunto de datos histórico** y estático.  
  Si las condiciones del mercado cambian de manera fuerte, el desempeño del modelo
  podría degradarse y sería necesario **reentrenarlo** con datos más recientes.

- A pesar de que el error promedio es razonable, existen **casos puntuales con
  errores altos** (colas del histograma) que indican que el modelo no es fiable
  para todas las propiedades por igual, especialmente en precios extremadamente
  altos o muy bajos.

- El modelo hace supuestos implícitos sobre la relación entre las variables y el
  precio; por ejemplo, que la información faltante se puede imputar sin introducir
  sesgos fuertes. Si la imputación no representa bien la realidad, el modelo
  también heredará ese sesgo.

En futuras versiones del análisis se podría:

- Probar modelos adicionales (por ejemplo, **Gradient Boosting, XGBoost o CatBoost**)
  y realizar una búsqueda más exhaustiva de hiperparámetros.

- Incorporar nuevas fuentes de información (datos socioeconómicos de los barrios,
  indicadores de mercado, infraestructura cercana, etc.) para enriquecer los
  predictores.

- Implementar un **esquema de validación temporal** (por ejemplo, entrenamiento en
  años anteriores y prueba en años más recientes) para evaluar mejor la capacidad
  del modelo de generalizar en el tiempo.

- Analizar con mayor detalle los casos con error extremo, para entender si son
  outliers, errores de registro o patrones que el modelo no está capturando.
"""
)

