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
