# =========================================
# 5. Georreferenciación interactiva
# =========================================
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from utils_melb import load_raw

st.header("5. Georreferenciación")
st.subheader("5.1 Mapa interactivo de precios de vivienda en Melbourne")
df = load_raw("data/melb_data.csv")
# Filtrar datos válidos
geo_df = df.dropna(subset=["Lattitude", "Longtitude", "Price"]).copy()

# Crear cuartiles de precios
geo_df["price_bin"] = pd.qcut(geo_df["Price"], 4, labels=["Q1 (Bajo)", "Q2", "Q3", "Q4 (Alto)"])

# Crear mapa centrado en Melbourne
m = folium.Map(location=[-37.81, 144.96], zoom_start=11, tiles="CartoDB positron")

# Agregar puntos con colores por cuartil
color_dict = {
    "Q1 (Bajo)": "#9ecae1",
    "Q2": "#6baed6",
    "Q3": "#3182bd",
    "Q4 (Alto)": "#08519c"
}

marker_cluster = MarkerCluster().add_to(m)

for _, row in geo_df.iterrows():
    popup_text = f"""
    <b>Precio:</b> ${row['Price']:,.0f} AUD<br>
    <b>Habitaciones:</b> {row.get('Rooms', 'N/A')}<br>
    <b>Baños:</b> {row.get('Bathroom', 'N/A')}<br>
    <b>Tipo:</b> {row.get('Type', 'N/A')}<br>
    <b>Suburbio:</b> {row.get('Suburb', 'N/A')}
    """
    folium.CircleMarker(
        location=[row["Lattitude"], row["Longtitude"]],
        radius=4,
        color=color_dict[row["price_bin"]],
        fill=True,
        fill_color=color_dict[row["price_bin"]],
        fill_opacity=0.6,
        popup=popup_text
    ).add_to(marker_cluster)

# Mostrar mapa interactivo
st_data = st_folium(m, width=800, height=500)

# Comentario interpretativo
st.markdown("""
**Interpretación del mapa:**

El mapa muestra la **distribución geográfica de las propiedades según sus cuartiles de precio** en Melbourne.  
Se observa una **mayor concentración de precios altos (Q4)** en las zonas **inner south y eastern suburbs**, 
cercanas al centro urbano y con mejor acceso a servicios y transporte.  

En contraste, los **precios más bajos (Q1)** se localizan en áreas más periféricas o alejadas del núcleo central, 
confirmando un **gradiente urbano típico**: los valores de las propiedades tienden a disminuir con la distancia al centro.  

El mapa es totalmente interactivo: puedes hacer **zoom, desplazarte o seleccionar puntos específicos** para explorar los detalles de cada vivienda.
""")
