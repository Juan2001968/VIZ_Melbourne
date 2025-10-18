import streamlit as st
import plotly.express as px
import pandas as pd
from utils_melb import load_raw, missing_table, PALETTE, ACCENT

st.title("2. Análisis exploratorio de datos")

df = load_raw("data/melb_data.csv")

st.subheader("2.1 Tamaño y tipos")
c1, c2 = st.columns(2)
with c1:
    st.write(f"Filas: {df.shape[0]}")
with c2:
    st.write(f"Columnas: {df.shape[1]}")
st.dataframe(df.dtypes.rename("dtype"))

st.markdown("""
### Análisis e interpretación de las variables del conjunto Melbourne Housing

A continuación se describen y analizan las variables del dataset, considerando su tipo, su papel dentro del análisis 
y observaciones relevantes para la etapa de imputación o modelado posterior.

| Variable | Tipo | Descripción | Comentarios |
|-----------|------|--------------|--------------|
| **Suburb** | Categórica | Nombre del suburbio o vecindario donde se encuentra la propiedad. | Variable espacial nominal. Útil para imputación por grupos y análisis geográfico; alta cardinalidad (muchos suburbios). |
| **Address** | Categórica | Dirección específica del inmueble. | Identificador textual sin valor analítico. Se excluye de análisis numérico. |
| **Rooms** | Numérica (discreta) | Número total de habitaciones de la vivienda. | Variable explicativa clave, relacionada con el tamaño y el precio. Se usa en correlaciones y gráficos bivariados. |
| **Type** | Categórica | Tipo de propiedad (h: casa, u: unidad, t: townhouse). | Categórica de baja cardinalidad; permite clasificar el mercado por tipo de vivienda. |
| **Price** | Numérica (continua) | Precio de venta en dólares australianos (AUD). | Variable objetivo principal. Presenta asimetría; se recomienda usar mediana y escalas logarítmicas para análisis posteriores. |
| **Method** | Categórica | Método de venta (S: vendida, SP: vendida antes, PI: no vendida, etc.). | Refleja modalidad de venta; se puede agrupar en vendida / no vendida. |
| **SellerG** | Categórica | Nombre del agente o grupo vendedor. | Alta cardinalidad. Puede tener valor en análisis de marca o desempeño de agencias. |
| **Date** | Temporal (objeto) | Fecha de venta. | Conviene convertirla a formato fecha para analizar estacionalidad y tendencias por año. |
| **Distance** | Numérica (continua) | Distancia al distrito central de negocios (CBD), en kilómetros. | Variable espacial continua. Negativamente correlacionada con el precio: a mayor distancia, menor valor promedio. |
| **Postcode** | Numérica (discreta) | Código postal de la propiedad. | Numérica pero categórica en esencia; representa zonas geográficas. Útil para agrupaciones. |
| **Bedroom2** | Numérica (discreta) | Número de dormitorios. | Muy correlacionada con `Rooms`. Puede servir para validar consistencia entre ambas. |
| **Bathroom** | Numérica (discreta) | Número de baños. | Variable explicativa relevante; correlacionada con `Rooms` y `BuildingArea`. |
| **Car** | Numérica (discreta) | Número de espacios para automóvil. | Relacionada con nivel socioeconómico o tamaño del inmueble; puede tener valores faltantes moderados. |
| **Landsize** | Numérica (continua) | Tamaño del terreno (m²). | Muy asimétrica con presencia de valores extremos; se recomienda usar mediana. |
| **BuildingArea** | Numérica (continua) | Superficie construida (m²). | Alta relación con `Price`; suele tener muchos valores faltantes, se imputará por grupos (`Suburb` o `Regionname`). |
| **YearBuilt** | Numérica (discreta) | Año de construcción. | Permite calcular antigüedad. Requiere imputación por grupos. |
| **CouncilArea** | Categórica | Jurisdicción o área del consejo local. | Variable espacial categórica de media cardinalidad; útil en análisis regional. |
| **Lattitude** | Numérica (continua) | Latitud de la propiedad. | Junto con `Longtitude`, permite visualizar distribución espacial. |
| **Longtitude** | Numérica (continua) | Longitud de la propiedad. | Complemento de `Lattitude` en la georreferenciación. |
| **Regionname** | Categórica | Región o macrozona de Melbourne. | Categórica geográfica intermedia; útil para segmentar el mercado y para imputación. |
| **Propertycount** | Numérica (discreta) | Número total de propiedades en el suburbio. | Indicador de densidad y tamaño del mercado local; discreta pero interpretable como contexto. |

**Resumen general:**
- El conjunto combina 14 variables numéricas y 7 categóricas.  
- La variable objetivo principal es **`Price`**.  
- Existen múltiples variables espaciales (`Suburb`, `Postcode`, `Regionname`, `Lattitude`, `Longtitude`), lo que permite análisis georreferenciados.  
- Algunas variables, aunque numéricas (`Postcode`, `Propertycount`), se interpretan mejor como categóricas.  
- Variables como `BuildingArea`, `YearBuilt` y `CouncilArea` presentan porcentajes altos de datos faltantes, por lo que requieren imputación cuidadosa.  
- Se observan colinealidades entre variables de tamaño (`Rooms`, `Bedroom2`, `BuildingArea`, `Bathroom`, `Car`), lo cual se tendrá en cuenta en la etapa de correlaciones y modelado.

---
""")
# =========================================
# 2.1 Revisión de duplicados
# =========================================

st.subheader("2.1 Revisión de duplicados")

duplicados = df.duplicated().sum()

st.write(f"**Total de registros duplicados:** {duplicados}")

if duplicados > 0:
    st.warning(f"Se encontraron {duplicados} registros duplicados. Se eliminarán para garantizar trazabilidad.")
    df = df.drop_duplicates()
else:
    st.success("No se encontraron registros duplicados en el dataset.")




st.subheader("2.2 Valores faltantes")
st.markdown("Se cuantifica el porcentaje de nulos para identificar variables críticas.")
st.dataframe(missing_table(df))
# =========================================
# Comentario interpretativo sobre valores faltantes
# =========================================

st.markdown("""
### Interpretación de los valores faltantes

El análisis del porcentaje de datos ausentes permite identificar las variables que requieren tratamiento de imputación antes de cualquier modelado o visualización avanzada.  
En la base *Melbourne Housing Market*, se detectan cuatro variables con valores faltantes en diferentes proporciones.

---

#### 1. BuildingArea (47.50%)
Variable numérica que representa la **superficie construida (m²)** de la propiedad.  
Con casi **la mitad de los registros faltantes**, constituye el caso más crítico del conjunto.  
Eliminar esta variable implicaría una pérdida significativa de información, ya que se relaciona directamente con el `Price` y el tamaño del inmueble.  
Por tanto, se optará por **mantenerla e imputarla por grupos**, usando la **mediana dentro del mismo `Suburb`** (o `Regionname` si no existe información suficiente por suburbio).  
Esta estrategia conserva la variabilidad espacial y reduce el sesgo derivado de promedios globales.

---

#### 2. YearBuilt (39.58%)
Corresponde al **año de construcción** del inmueble.  
El porcentaje de faltantes es alto, pero se trata de una variable **estructural clave** para calcular la antigüedad (`Age = año actual - YearBuilt`).  
Por tanto, también se **mantendrá** en el análisis.  
La imputación se realizará **por grupos (`Suburb` o `Regionname`) usando la mediana**, ya que los rangos de antigüedad tienden a ser similares dentro de una misma zona urbana.

---

#### 3. CouncilArea (10.08%)
Variable **categórica espacial**, indica la jurisdicción administrativa o consejo local correspondiente a cada propiedad.  
El 10% de nulos sugiere registros sin asociación formal a un área administrativa, posiblemente por inconsistencias o propiedades fuera de límites definidos.  
La imputación ideal es **por moda dentro del `Suburb` o `Regionname`**, lo que garantiza consistencia geográfica entre los registros imputados.

---

#### 4. Car (0.46%)
Número de espacios de estacionamiento en la vivienda.  
Presenta una proporción mínima de nulos (<1%), lo que permite una **imputación simple mediante la mediana global**.  
Debido a que es una variable discreta y con valores bajos (0–3), la mediana o moda reflejan adecuadamente la tendencia central del conjunto.

---

#### 5. Resto de variables (0%)
El resto de variables (`Price`, `Rooms`, `Landsize`, `Bathroom`, `Distance`, etc.) no presentan valores faltantes, lo que indica **alta completitud** en la información principal del conjunto.

---

### Conclusión general
Las variables `BuildingArea`, `YearBuilt` y `CouncilArea` requieren **imputación por grupos** para preservar patrones espaciales y evitar distorsiones en el análisis.  
La variable `Car`, con muy pocos nulos, se imputará de forma simple.

Estas decisiones permiten mantener la coherencia espacial y evitar pérdida de información sustancial.  
En etapas posteriores se evaluará el impacto de la imputación mediante un **análisis comparativo antes y después del tratamiento**.
""")
# =========================================
# 2.3 Feature Engineering y trazabilidad
# =========================================

st.subheader("2.3 Feature Engineering y trazabilidad")

# Crear variable de antigüedad
df["Age"] = 2025 - df["YearBuilt"]

# Crear variable de precio por m² (si existen datos válidos)
df["Price_m2"] = df["Price"] / df["BuildingArea"]

# Crear variable de densidad urbana aproximada
df["Density"] = df["Propertycount"] / df.groupby("Regionname")["Propertycount"].transform("count")

st.write(df[["Price", "BuildingArea", "Price_m2", "Age", "Density"]].head())

st.markdown("""
Se generan nuevas variables derivadas que enriquecen el análisis:
- **Age:** antigüedad de la vivienda, derivada de `YearBuilt`.
- **Price_m2:** relación entre precio y área construida, indicador comparativo de valor.
- **Density:** aproximación a la densidad de propiedades en cada región.

Estas transformaciones aportan trazabilidad al proceso y mejoran la capacidad explicativa de los análisis posteriores.
""")


st.subheader("2.4 Estadísticos descriptivos (numéricos)")
st.dataframe(df.select_dtypes("number").describe().T)
# =========================================
# Comentario interpretativo del análisis descriptivo numérico
# =========================================

st.markdown("""
### Interpretación del análisis descriptivo numérico

El análisis de estadísticos descriptivos permite conocer la escala, variabilidad y presencia de valores extremos en las variables cuantitativas del conjunto de datos.

#### 1. Rooms
El número de habitaciones presenta una media de **2.94** con una mediana de **3**, mostrando una distribución ligeramente sesgada a la izquierda (más propiedades con 2–3 habitaciones).  
El rango va de 1 a 10 habitaciones, lo cual es coherente con un mercado predominantemente residencial.

#### 2. Price
El precio medio de las viviendas es de **1.07 millones de AUD**, con una desviación estándar alta (**639.000 AUD**), lo que indica una **alta dispersión** en los valores de venta.  
El rango va desde **85.000** hasta **9 millones**, confirmando la presencia de propiedades de lujo que generan asimetría positiva.  
Se recomienda usar **mediana (903.000 AUD)** o transformaciones logarítmicas para reducir el impacto de los valores extremos.

#### 3. Distance
La distancia promedio al distrito central de negocios (CBD) es de **10.1 km**, con valores entre 0 y 48 km.  
El 75% de las propiedades están ubicadas a menos de 13 km del centro, reflejando una concentración urbana y menor número de viviendas en zonas periféricas.  
La relación esperada con el precio es **negativa** (mayor distancia, menor valor).

#### 4. Postcode
El código postal varía entre 3000 y 3977, con una media de **3105**, lo que confirma la cobertura de un área metropolitana amplia.  
Aunque es numérica, se interpreta como **variable categórica geográfica**, útil para agrupar zonas o comparar precios medios por distrito.

#### 5. Bedroom2
La media es de **2.91 dormitorios** y la mediana de **3**, consistente con la variable `Rooms`.  
Sin embargo, hay registros con **0 dormitorios**, lo cual sugiere posibles errores de digitación o valores faltantes no declarados.  
Conviene revisar coherencia entre `Bedroom2` y `Rooms` antes del modelado.

#### 6. Bathroom
El promedio es **1.53 baños**, con valores entre 0 y 8.  
Distribución fuertemente concentrada en 1–2 baños.  
Los valores 0 pueden representar errores o viviendas con datos incompletos, por lo que deben tratarse en la imputación.

#### 7. Car
El número de espacios de estacionamiento tiene una media de **1.61** y mediana de **2**, rango de 0 a 10.  
Los valores de 0 pueden reflejar unidades sin garaje o datos faltantes.  
La desviación estándar (0.96) sugiere baja variabilidad general.

#### 8. Landsize
El tamaño de los terrenos muestra una media de **558 m²**, pero con una desviación extremadamente alta (**3.990 m²**) y un máximo de **433.000 m²**, lo cual indica **outliers severos**.  
La mediana (**440 m²**) es mucho más representativa.  
Se recomienda usar la **mediana** y considerar la detección de valores atípicos o escalado logarítmico.

#### 9. BuildingArea
El área construida tiene una media de **152 m²**, mediana de **126 m²** y un máximo de **44.515 m²**, lo cual confirma presencia de valores erróneos o propiedades atípicas.  
Además, solo se tienen **7.130 observaciones válidas** (≈52%), por lo que requiere imputación.  
Su fuerte asimetría justifica imputar por **mediana por Suburb**.

#### 10. YearBuilt
El año de construcción promedio es **1964**, con un rango entre **1196** y **2018**.  
El valor mínimo es **anómalo (1196)** y corresponde a un error evidente de registro.  
La distribución se centra entre 1940–2000, lo que refleja un parque habitacional mixto entre viviendas antiguas y modernas.

#### 11. Lattitude y Longtitude
La latitud promedio es **–37.8** y la longitud **145.0**, lo cual coincide con la localización de Melbourne.  
Ambas variables presentan **baja variabilidad** (desviación <0.1), indicando coherencia espacial de los datos.  
Se usarán posteriormente para la georreferenciación de precios.

#### 12. Propertycount
El número de propiedades por suburbio tiene una media de **7.454**, con una desviación elevada (**4.378**).  
Los valores van desde 249 hasta 21.650, lo cual sugiere una **alta desigualdad** en la densidad urbana entre suburbios.  
Variable útil como indicador de tamaño de mercado local.

---

### Conclusiones generales del análisis numérico

- El conjunto presenta **amplia variabilidad y asimetría** en las variables económicas (`Price`, `Landsize`, `BuildingArea`).  
- Las variables de tamaño (`Rooms`, `Bedroom2`, `Bathroom`, `Car`) se distribuyen de forma razonable, reflejando viviendas de 2–3 habitaciones como el perfil típico.  
- Se identifican **valores atípicos extremos** en `Landsize` y `BuildingArea`, que deben analizarse con técnicas de winsorización o transformaciones.  
- Las variables espaciales (`Lattitude`, `Longtitude`) son consistentes y fundamentales para el análisis geográfico.  
- `BuildingArea` y `YearBuilt` presentan datos faltantes relevantes y serán tratadas mediante imputación por grupos (`Suburb` / `Regionname`).  
- En conjunto, el análisis confirma un mercado inmobiliario **heterogéneo y asimétrico**, donde el precio depende fuertemente del tamaño, la localización y la antigüedad del inmueble.
""")


st.subheader("2.5 Detección de outliers")

numeric_cols = df.select_dtypes(include=["number"]).columns

outlier_summary = []

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][col].count()
    outlier_summary.append((col, outliers))

outlier_df = pd.DataFrame(outlier_summary, columns=["Variable", "Cantidad de outliers"])
st.dataframe(outlier_df)

st.markdown("""
Se emplea el método del rango intercuartílico (IQR) para identificar valores atípicos.
""")

# =========================================
# Comentarios sobre la detección de outliers
# =========================================

st.markdown("""
### Interpretación de la detección de outliers

El análisis de valores atípicos permite identificar observaciones que se alejan significativamente del comportamiento general de los datos.  
A partir de la tabla, se observa lo siguiente:

- **Rooms (682), Bedroom2 (655) y Car (644)** presentan un número considerable de outliers, lo cual es esperable en variables de conteo que pueden incluir propiedades con un número inusualmente alto de habitaciones o garajes (por ejemplo, residencias de lujo o propiedades comerciales).  
  En estos casos, conviene revisar si esos registros son plausibles o si corresponden a errores de carga.

- **Price (612 outliers)** muestra una dispersión amplia, lo que indica una **alta heterogeneidad del mercado inmobiliario**: existen tanto viviendas económicas como propiedades de alto valor, que podrían sesgar las medidas de tendencia central si no se tratan adecuadamente.

- **Distance (411)** y **Longtitude (408)** también presentan valores extremos. En el primer caso, es posible que haya viviendas muy alejadas del centro urbano; en el segundo, errores geográficos menores o ubicaciones periféricas fuera de la zona metropolitana.

- **Variables relacionadas con tamaño físico** como *Landsize (368)* y *BuildingArea (353)* muestran outliers típicos de terrenos o construcciones de dimensiones poco comunes.  
  Estos valores no necesariamente son errores, pero deben analizarse porque pueden distorsionar los modelos de regresión o clustering.

- **Propertycount (359)** y **Price_m2 (329)** mantienen dispersión moderada, lo que refleja variabilidad en densidad inmobiliaria y en valor por metro cuadrado.

- **Variables con pocos outliers** (*YearBuilt* y *Age*) presentan distribución más estable, indicando consistencia en los años de construcción y edad de las propiedades.

- Finalmente, la variable **Density (1293 outliers)** es la más crítica, posiblemente por contener valores calculados a partir de otras variables o por tener una escala distinta.  
  Este comportamiento sugiere una distribución muy asimétrica o presencia de errores de cálculo.

En conjunto, se puede concluir que las variables con mayor cantidad de outliers están asociadas con el **tamaño, valor y características estructurales** de las viviendas, elementos que suelen variar ampliamente en el mercado inmobiliario.  
Para el modelado posterior, se recomienda aplicar **winsorización, transformación logarítmica o técnicas robustas** que reduzcan el impacto de estos valores extremos.
""")


st.subheader("2.6 Distribuciones univariadas")


num_candidates = [c for c in ["Price","Rooms","Distance","Landsize","BuildingArea",
                              "Bedroom2","Bathroom","Car"] if c in df.columns]
for col in num_candidates:
    fig = px.histogram(df, x=col, nbins=30, color_discrete_sequence=[PALETTE[2]])
    fig.update_layout(title=f"Distribución de {col}", bargap=0.02)
    st.plotly_chart(fig, use_container_width=True)
st.caption("Las variables de precio y superficies muestran asimetría a la derecha; se recomienda usar mediana para imputación y medidas de tendencia central.")
# =========================================
# Comentarios interpretativos de las distribuciones univariadas
# =========================================

st.markdown("""
### Interpretación de las distribuciones univariadas

Las siguientes gráficas permiten observar la forma, dispersión y presencia de valores atípicos en las principales variables numéricas del conjunto de datos.

---

#### 1. Distribución de **Price**
La variable `Price` presenta una **distribución fuertemente asimétrica hacia la derecha**.  
La mayoría de las propiedades se concentran entre **500.000 y 1.500.000 AUD**, mientras que existen pocos casos con valores muy altos que alcanzan hasta **9 millones**, lo que refleja la presencia de **outliers asociados a viviendas de lujo**.  
Esta forma indica que el mercado inmobiliario está dominado por propiedades de rango medio, con una pequeña proporción de inmuebles de alto valor.  
Para análisis posteriores se recomienda aplicar una **transformación logarítmica** o usar medidas robustas (mediana).

---

#### 2. Distribución de **Rooms**
`Rooms` muestra una **distribución unimodal**, centrada en **3 habitaciones**, seguida por viviendas de **2 y 4 habitaciones**.  
La presencia de pocos casos con más de 6 habitaciones indica que el mercado está compuesto principalmente por **viviendas familiares de tamaño estándar**, siendo los casos extremos (8–10 habitaciones) residencias excepcionales o registros atípicos.  
Esta variable es clave para explicar diferencias de precio.

---

#### 3. Distribución de **Distance**
La variable `Distance` presenta una **distribución sesgada positivamente**, con una concentración de propiedades entre **5 y 15 km del distrito central de negocios (CBD)**.  
La frecuencia disminuye gradualmente a medida que aumenta la distancia, lo que refleja una mayor densidad urbana en zonas cercanas al centro.  
Este patrón sugiere una **relación inversa esperada con el precio**, donde la localización más cercana al CBD tiende a elevar el valor de las viviendas.

---

#### 4. Distribución de **Landsize**
`Landsize` exhibe una **distribución altamente asimétrica**, con una gran concentración de terrenos pequeños (menores a **1.000 m²**) y unos pocos casos con valores extremadamente altos (hasta **433.000 m²**).  
Estos outliers probablemente corresponden a propiedades rurales o errores de medición.  
La alta dispersión justifica usar **mediana o transformaciones logarítmicas**, y aplicar una revisión de valores extremos para mejorar la representatividad estadística.

---

#### 5. Distribución de **BuildingArea**
La `BuildingArea` también presenta **asimetría severa**, con la mayoría de las viviendas concentradas por debajo de **500 m²**, mientras que algunos registros alcanzan valores exageradamente altos (más de **40.000 m²**).  
Estos casos son atípicos y podrían distorsionar los resultados si no se tratan adecuadamente.  
El comportamiento confirma la necesidad de **imputar valores faltantes** y analizar outliers antes del modelado.

---

#### 6. Distribución de **Bedroom2**
La variable `Bedroom2` tiene una forma similar a `Rooms`: **pico principal en 3 dormitorios**, seguido por propiedades de 2 y 4 habitaciones.  
Los casos con 0 o más de 10 dormitorios son **anómalos o residencias no convencionales**.  
Esta consistencia con `Rooms` sugiere que ambas variables están relacionadas y pueden usarse para validar imputaciones.

---

#### 7. Distribución de **Bathroom**
La variable `Bathroom` muestra una **distribución concentrada en 1 y 2 baños**, con algunos casos de hasta 8 baños.  
Los valores de 0 probablemente son errores o registros incompletos.  
La mayoría de las viviendas se ajustan al estándar residencial medio, y los casos extremos indican propiedades de lujo.

---

#### 8. Distribución de **Car**
La distribución de `Car` es **bimodal**, con dos picos en **1 y 2 espacios de estacionamiento**, lo cual es coherente con el tipo de vivienda predominante.  
Los valores de 0 indican inmuebles sin garaje (típicos en zonas céntricas o apartamentos), mientras que los valores mayores a 4 representan **casas grandes o registros atípicos**.  
La forma es razonable, con una ligera cola derecha.

---

### Conclusión general

Las distribuciones univariadas confirman que el conjunto de datos de *Melbourne Housing Market* presenta:

- **Alta asimetría positiva** en las variables de tamaño y precio (`Price`, `Landsize`, `BuildingArea`).  
- **Concentraciones centrales coherentes** en variables de recuento (`Rooms`, `Bathroom`, `Car`, `Bedroom2`).  
- **Outliers evidentes** en terrenos y áreas construidas, que deberán tratarse con winsorización o escalado logarítmico.  
- Un patrón geográfico indirecto en `Distance`, que sugiere gradiente urbano de precios.

En conjunto, las variables numéricas reflejan un **mercado residencial heterogéneo**, con amplia dispersión en tamaño y valor, y una clara estructura de concentración urbana.
""")

st.subheader("2.7 Relaciones bivariadas con Price")
pairs = [c for c in ["Rooms","Distance","Landsize","BuildingArea"] if c in df.columns]
for col in pairs:
    if "Price" in df.columns:
        fig = px.scatter(df, x=col, y="Price",
                         opacity=0.4,
                         color_discrete_sequence=[PALETTE[3]])
        fig.update_layout(title=f"{col} vs Price")
        st.plotly_chart(fig, use_container_width=True)
st.caption("Se observa relación positiva de Price con Rooms y BuildingArea; relación negativa con Distance.")
# =========================================
# Comentario interpretativo de relaciones bivariadas con Price
# =========================================

st.markdown("""
### Interpretación de las relaciones bivariadas con Price

El análisis bivariado busca identificar relaciones directas o inversas entre las principales variables explicativas y el precio de venta (`Price`), con el fin de comprender los factores que determinan el valor de las propiedades.

---

#### 1. **Rooms vs Price**
La relación entre el número de habitaciones y el precio muestra una **tendencia positiva clara**: a medida que aumenta el número de habitaciones, el precio medio de la propiedad tiende a incrementarse.  
Sin embargo, se observa una **alta dispersión** dentro de cada categoría, especialmente entre viviendas de 3 a 5 habitaciones.  
Esto indica que, aunque el tamaño influye, el precio también depende de otros factores como la localización o la calidad constructiva.  
Las viviendas con más de 6 habitaciones son escasas y presentan precios muy variables, probablemente por tratarse de inmuebles de lujo o casos atípicos.

---

#### 2. **Distance vs Price**
La relación entre `Distance` y `Price` presenta un **patrón claramente decreciente**: las propiedades ubicadas más cerca del distrito central de negocios (CBD) alcanzan precios considerablemente más altos.  
A medida que aumenta la distancia (más de 15 km), los precios tienden a disminuir progresivamente, lo que evidencia un **efecto espacial de centralidad urbana**.  
Este comportamiento es típico de mercados metropolitanos donde la proximidad a zonas económicas o comerciales genera plusvalía.  
La nube de puntos también muestra una amplia dispersión, lo que indica la influencia de otros factores además de la distancia.

---

#### 3. **Landsize vs Price**
`Landsize` muestra una relación **positiva pero débil** con el precio.  
Aunque en teoría un mayor terreno debería implicar un valor más alto, el gráfico evidencia que la mayoría de las propiedades tienen terrenos pequeños y valores de precio muy diversos.  
Los pocos puntos con grandes extensiones (superiores a 10.000 m²) no siguen un patrón lineal y corresponden a **outliers o terrenos rurales**.  
La alta concentración de puntos en el rango bajo indica que el tamaño del lote **no es un predictor lineal fuerte del precio** sin considerar la ubicación y el tipo de propiedad.

---

#### 4. **BuildingArea vs Price**
La relación entre `BuildingArea` y `Price` es **positiva y más definida**: las viviendas con mayor área construida tienden a tener precios más altos.  
Sin embargo, al igual que `Landsize`, se observan **outliers significativos** con áreas exageradamente grandes (más de 10.000 m²) que distorsionan la relación general.  
La densidad de puntos cerca del origen sugiere que la mayoría de las propiedades se agrupan entre 100 y 300 m² con precios entre 500.000 y 2.000.000 AUD.  
En general, esta variable es un **predictor estructural fuerte del precio**, siempre que se controle la presencia de valores extremos.

---

### Conclusión general

Las relaciones bivariadas confirman que:

- **El tamaño físico del inmueble** (`Rooms`, `BuildingArea`) tiene un impacto directo y significativo en el precio.  
- **La localización** (`Distance`) ejerce un efecto inverso: la cercanía al centro urbano incrementa el valor del bien.  
- **El terreno (`Landsize`) influye en menor medida**, y su relación con el precio se ve afectada por la existencia de valores extremos.  
- En conjunto, las variables espaciales y estructurales explican gran parte de la variabilidad de los precios, pero también sugieren la necesidad de análisis multivariados posteriores (por ejemplo, regresiones) para cuantificar su peso relativo.
""")


st.subheader("2.8 Correlaciones numéricas")
num_cols = df.select_dtypes("number").columns
corr = df[num_cols].corr()
fig = px.imshow(corr, color_continuous_scale=[PALETTE[0], PALETTE[2], PALETTE[4]],
                zmin=-1, zmax=1, aspect="auto")
fig.update_layout(title="Matriz de correlaciones")
st.plotly_chart(fig, use_container_width=True)

# =========================================
# Comentarios interpretativos sobre la matriz de correlaciones
# =========================================

st.markdown("""
### Interpretación de la matriz de correlaciones numéricas

El mapa de calor muestra la fuerza y dirección de las relaciones lineales entre las variables numéricas del conjunto *Melbourne Housing Market*.  
Los tonos más oscuros representan correlaciones positivas fuertes, mientras que los tonos claros o azul pálido reflejan relaciones débiles o negativas.

---

#### 1. Correlaciones con la variable objetivo (**Price**)
- **Rooms (r = 0.50):** Existe una **correlación positiva moderada** entre el número de habitaciones y el precio. En general, más habitaciones implican propiedades de mayor valor.  
- **BuildingArea (r ≈ 0.59–0.60):** Es la **variable más correlacionada con el precio**, lo que confirma que el área construida es el mejor indicador estructural del valor de una vivienda.  
- **Bathroom (r ≈ 0.52):** Presenta una relación positiva significativa, reforzando la idea de que viviendas con mayor dotación sanitaria son más costosas.  
- **Car (r ≈ 0.42):** Muestra una correlación positiva moderada; el número de garajes suele aumentar con el tamaño y precio del inmueble.  
- **Distance (r ≈ -0.48):** Correlación **negativa**, lo que significa que los precios disminuyen conforme aumenta la distancia al centro de la ciudad.  
  Este patrón espacial confirma la existencia de un gradiente urbano de valorización.

En resumen, las variables **estructurales (Rooms, BuildingArea, Bathroom, Car)** y la **localización (Distance)** explican gran parte de la variación en el precio de las propiedades.

---

#### 2. Relaciones internas entre variables explicativas
- **Rooms, Bedroom2, Bathroom y Car** presentan **alta colinealidad positiva**, lo cual es lógico, ya que reflejan distintas medidas del tamaño del inmueble.  
  Esto implica que en modelados futuros (por ejemplo, regresión múltiple) conviene evitar incluir todas simultáneamente para no generar multicolinealidad.  
- **Landsize y BuildingArea** muestran **correlación positiva moderada**, lo que indica que las viviendas con mayor superficie de terreno tienden a tener más área construida.  
- **YearBuilt** tiene **correlaciones débiles** con las demás variables, lo que sugiere que la antigüedad no se asocia fuertemente con tamaño o precio de manera lineal.  
- **Latitude y Longitude** muestran correlación negativa moderada entre sí, coherente con la distribución geográfica de Melbourne (latitudes más al sur suelen tener longitudes menores).

---

#### 3. Conclusión general

- Las correlaciones confirman que el **tamaño del inmueble y su ubicación** son los principales factores determinantes del precio.  
- Las variables **Rooms, Bathroom, BuildingArea y Distance** deben priorizarse en análisis predictivos.  
- Existen **grupos de variables redundantes** (por ejemplo, `Rooms` y `Bedroom2`), que deberán tratarse mediante reducción de dimensionalidad o selección de variables.  
- La matriz sugiere una estructura **moderadamente multicolineal**, típica de conjuntos inmobiliarios donde las variables de tamaño tienden a crecer conjuntamente.

En conjunto, la matriz de correlaciones ofrece evidencia sólida sobre las dependencias lineales entre las características estructurales y espaciales del mercado inmobiliario de Melbourne.
""")

# =========================================
# 2.9 Análisis temporal del precio de vivienda
# =========================================
import plotly.express as px
import streamlit as st
import pandas as pd

st.subheader("2.9 Análisis temporal del precio promedio")

# Aseguramos que la columna de fecha esté en formato datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Creamos una columna "Year" (si no existe)
if "Year" not in df.columns:
    df["Year"] = df["Date"].dt.year

# Calculamos el precio promedio por año
price_trend = df.groupby("Year", as_index=False)["Price"].mean().dropna()

# Gráfico temporal
fig_time = px.line(
    price_trend,
    x="Year",
    y="Price",
    markers=True,
    line_shape="spline",
    title="Evolución del precio promedio por año",
    labels={"Price": "Precio promedio (AUD)", "Year": "Año"},
    color_discrete_sequence=["#1f77b4"]
)
fig_time.update_layout(
    template="simple_white",
    title_x=0.1,
    title_font=dict(size=18),
    yaxis=dict(tickformat=".0f")
)

st.plotly_chart(fig_time, use_container_width=True)

# =========================================
# Comentarios sobre el análisis temporal del precio promedio
# =========================================

st.markdown("""
### Interpretación del análisis temporal

El gráfico muestra la **evolución del precio promedio de las propiedades en Melbourne** durante los años **2016 y 2017**.  
En este período corto, se observa una **leve disminución del valor medio**, pasando de aproximadamente **1.09 millones de AUD en 2016**  
a cerca de **1.07 millones en 2017**.

Aunque la variación no es drástica, este descenso puede reflejar **ajustes coyunturales en el mercado inmobiliario**, como:
- Cambios en las tasas de interés o políticas de financiamiento hipotecario.
- Una mayor oferta de propiedades nuevas que moderó los precios promedio.
- Factores económicos generales, como desaceleración del crecimiento o restricciones crediticias temporales.

Es importante resaltar que el rango temporal disponible **no permite inferir tendencias de largo plazo**.  
Sin embargo, este comportamiento sugiere que el mercado de Melbourne en 2017 mostró señales de **estabilización o leve corrección**  
después del fuerte crecimiento observado en años anteriores (según reportes externos del mercado).

En resumen, el análisis temporal evidencia una **ligera contracción en los precios promedio**,  
posiblemente asociada a un ajuste natural del ciclo inmobiliario en la ciudad.
""")


# =========================================
# 2.10 Evidencias analíticas y validación estadística
# =========================================

st.subheader("2.10 Evidencias analíticas y validación estadística")

from scipy import stats

# Prueba de normalidad (Shapiro-Wilk)
sample_price = df["Price"].dropna().sample(500, random_state=42)
shapiro_test = stats.shapiro(sample_price)

st.write("**Prueba de normalidad (Shapiro-Wilk) para Price:**")
st.write(f"Estadístico = {shapiro_test.statistic:.4f}, p-value = {shapiro_test.pvalue:.4f}")

if shapiro_test.pvalue < 0.05:
    st.warning("Los datos de Price **no siguen una distribución normal** (p < 0.05). Se sugiere usar métodos no paramétricos.")
else:
    st.success("Los datos de Price son aproximadamente normales (p > 0.05).")

# Prueba de homogeneidad de varianzas (Levene)
groups = [df[df["Rooms"] == i]["Price"].dropna() for i in [2, 3, 4]]
stat, p = stats.levene(*groups)
st.write(f"**Prueba de Levene (Rooms 2–4):** Estadístico = {stat:.4f}, p-value = {p:.4f}")

# Correlación Spearman (Price vs Distance)
rho, pval = stats.spearmanr(df["Price"], df["Distance"], nan_policy="omit")
st.write(f"**Correlación Spearman Price–Distance:** rho = {rho:.3f}, p-value = {pval:.4f}")

# =========================================
# Comentarios sobre las evidencias analíticas y validación estadística
# =========================================

st.markdown("""
### Interpretación de las pruebas estadísticas

El conjunto de evidencias estadísticas confirma varios aspectos importantes sobre el comportamiento de los datos:

- **Prueba de normalidad (Shapiro–Wilk):**  
  El estadístico de Shapiro–Wilk fue **0.8579** con un *p-value* de **0.0000**, lo que indica que la variable **Price no sigue una distribución normal** (p < 0.05).  
  En consecuencia, los análisis posteriores deben aplicar **métodos no paramétricos**, ya que los supuestos de normalidad no se cumplen.  
  Este resultado es común en precios inmobiliarios, donde la distribución suele ser **asimétrica hacia la derecha**, con presencia de viviendas de muy alto valor (outliers positivos).

- **Prueba de homogeneidad de varianzas (Levene):**  
  La prueba de Levene para comparar la varianza de *Price* entre grupos definidos por *Rooms (2–4)* arrojó un estadístico de **448.07** (p = 0.0000).  
  Esto significa que **las varianzas entre grupos no son iguales**, descartando la homocedasticidad.  
  En términos prácticos, la dispersión de precios aumenta con el número de habitaciones, lo cual refleja una mayor heterogeneidad en el segmento de viviendas más grandes.

- **Correlación de Spearman (Price – Distance):**  
  El coeficiente de Spearman fue **rho = –0.130** con *p-value* < 0.001, lo que evidencia una **correlación negativa débil pero significativa** entre el precio y la distancia al centro.  
  Esto confirma el **gradiente urbano** ya observado en los mapas y gráficos: los precios tienden a ser más altos en zonas centrales y disminuyen progresivamente hacia la periferia.

---

En conjunto, las pruebas estadísticas reafirman los patrones detectados visualmente:
- La distribución de precios es **asimétrica** y con **alta dispersión**.  
- Existen **diferencias significativas de varianza** entre categorías de propiedades.  
- Y la **relación espacial** entre precio y distancia es coherente con el comportamiento urbano típico de las grandes ciudades.
""")
