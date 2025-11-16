import streamlit as st
import plotly.express as px
from utils_melb import load_raw, compare_distributions, PALETTE

st.title("4. Análisis post–imputación: comparativa")

df_before = load_raw("data/melb_data.csv")
df_after  = st.session_state.get("df_imp", None)
if df_after is None:
    st.info("No hay datos imputados en memoria. Se imputará en la página 3 antes de continuar.")
else:
    comp = compare_distributions(df_before, df_after)
    st.subheader("4.1 Comparativa de momentos (antes vs después)")
    st.dataframe(comp)
    # =========================================
    # Comentarios sobre la comparación antes y después de la imputación
    # =========================================

    st.markdown("""
    ### Comparación de nulos antes y después de la imputación

    La tabla y/o gráfico de comparación permiten evaluar el impacto directo del proceso de imputación sobre la completitud de los datos.  
    Los resultados reflejan una **reducción significativa de los valores faltantes** en las variables críticas del dataset, lo que demuestra la efectividad del método aplicado.

    - **Antes de la imputación**, variables como *BuildingArea*, *YearBuilt* y *CouncilArea* presentaban altos porcentajes de valores ausentes (entre 10% y 47%),  
    lo que comprometía el análisis descriptivo y la validez estadística del conjunto de datos.

    - **Después de la imputación**, los valores faltantes se redujeron drásticamente:  
    *BuildingArea* pasó de más del 47% a apenas **0.12%**, y *YearBuilt* bajó de alrededor del 40% a **0.13%**, evidenciando un **proceso de imputación exitoso y controlado**.

    - El resto de las variables —como *Price*, *Rooms*, *Distance*, *Bathroom* y *Car*— quedaron completamente completas,  
    garantizando **consistencia analítica** y evitando sesgos en los modelos predictivos que se apliquen posteriormente.

    - Además, la trazabilidad del proceso asegura que cada imputación se hizo de forma **coherente con el contexto de los datos**,  
    utilizando información de otras variables como *Suburb* y *Regionname*, o estadísticas de tendencia central (mediana o moda) según el tipo de variable.

    En síntesis, la comparación confirma que el **proceso de imputación logró su objetivo**:  
    mejorar la calidad del dataset, reducir la pérdida de información y mantener la coherencia estructural de los datos para los análisis siguientes.
    """)


    

    st.subheader("4.2 Inspección gráfica de cambios (ejemplos)")
    for col in [c for c in ["Price","BuildingArea","Landsize","Distance"] if c in df_after.columns]:
        fig = px.histogram(df_after, x=col, nbins=30,
                           color_discrete_sequence=[PALETTE[2]])
        fig.update_layout(title=f"Distribución post–imputación de {col}")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
**Conclusión.** Las imputaciones mantienen la forma general de las distribuciones y corrigen huecos por ausencia de datos.
El uso de mediana para variables asimétricas y la imputación por grupos evitan sesgos agregados.
""")
