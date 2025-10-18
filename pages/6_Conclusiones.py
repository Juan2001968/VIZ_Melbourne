import streamlit as st

st.title("6. Conclusiones")

st.markdown("""
1) **Calidad de datos e imputación.** La base presenta porcentajes de nulos manejables; se aplicó una estrategia proporcional:
imputación simple (media/mediana o moda) cuando el porcentaje fue pequeño y **por grupos** (Suburb/Regionname) cuando fue moderado o alto,
conservando la heterogeneidad espacial. La validación muestra reducción efectiva de nulos sin distorsión sustantiva de las distribuciones.

2) **Hallazgos del EDA.** El precio y las superficies exhiben asimetría; la mediana es una medida robusta.
`BuildingArea` y `Rooms` muestran relación positiva con el precio; `Distance` relación negativa.
Existe colinealidad entre variables de tamaño/dotación que debe considerarse si se modela.

3) **Patrones espaciales.** Los cuartiles altos de precio se concentran en áreas centrales y corredores residenciales específicos.
La localización es determinante en el valor de la vivienda.

4) **Limitaciones.** El análisis no incorpora mapa base ni polígonos administrativos; la georreferenciación es puntual con lat/long.
Algunos campos pueden requerir transformaciones logarítmicas en etapas de modelado.

5) **Próximos pasos.** Incorporar capas espaciales de suburbios, evaluar modelos con regularización para colinealidad,
y analizar términos de interacción (por ejemplo, Distancia×Área construida) y transformaciones logarítmicas.
""")
