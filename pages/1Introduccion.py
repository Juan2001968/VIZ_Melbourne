import streamlit as st

st.title("1. Introducción")

st.markdown("""
Nuestro propósito general en este estudio es **comprender los factores que inciden en el precio de las propiedades**
(*variable objetivo: `Price`*), explorando cómo varía este valor según las características estructurales del inmueble
y su ubicación dentro de la ciudad. Para ello se analizan variables como:

- `Rooms`: número de habitaciones.  
- `Landsize`: superficie del terreno.  
- `BuildingArea`: superficie construida.  
- `Bathroom`: número de baños.  
- `Car`: número de plazas de parqueo.  
- `Distance`: distancia al distrito central de negocios (CBD).  
- `Lattitude` y `Longtitude`: coordenadas geográficas.  
- `Regionname` y `Suburb`: variables espaciales de localización.

El estudio se estructura en cinco etapas principales:

1. **Análisis exploratorio de datos (EDA):** descripción general del conjunto de datos, identificación de patrones,
   asimetrías y relaciones entre variables.  
2. **Imputación de valores faltantes:** aplicación de técnicas de imputación acordes al porcentaje de datos ausentes,
   priorizando la conservación de patrones locales mediante imputación por grupos (`Suburb` o `Regionname`).  
3. **Análisis post–imputación:** comparación entre los valores antes y después del proceso de imputación,
   verificando la estabilidad de medidas de tendencia y dispersión.  
4. **Georreferenciación:** análisis espacial para identificar zonas de alta y baja valorización dentro de Melbourne.  
5. **Conclusiones:** síntesis de los hallazgos y reflexión sobre la utilidad del análisis para la comprensión del mercado inmobiliario.

En resumidas cuentas, buscamos **explicar cómo la localización y las características físicas influyen en el precio
de las viviendas**, mediante un enfoque descriptivo, analítico y visual. El resultado final constituye una herramienta
de comprensión del mercado inmobiliario de Melbourne y una aplicación práctica de técnicas de análisis de datos
en el contexto de visualización y georreferenciación.
""")
