import hmac
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Comparativa de métodos",
    layout="wide"
)

# ─────────────────────────────
# Contraseña
# ─────────────────────────────
if not st.session_state.get("autorizado"):

    st.title("Dashboard de modelos")

    clave = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        if hmac.compare_digest(
            clave,
            st.secrets["APP_PASSWORD"]
        ):
            st.session_state["autorizado"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")

    st.stop()


# ─────────────────────────────
# Cargar datos
# ─────────────────────────────
def cargar_datos(archivo, metodo):

    datos = pd.read_csv(
        archivo,
        sep=None,
        engine="python",
        encoding="utf-8-sig"
    )

    datos.columns = datos.columns.str.strip()

    columnas = [
        "Tiempo de predicción",
        "Año",
        "Presupuesto de horas",
        "Horas acertadas"
    ]

    if not set(columnas).issubset(datos.columns):
        st.error(
            f"{archivo} debe contener: {columnas}"
        )
        st.write(
            "Columnas encontradas:",
            list(datos.columns)
        )
        st.stop()

    for columna in columnas:
        datos[columna] = pd.to_numeric(
            datos[columna],
            errors="coerce"
        )

    datos = datos.dropna(subset=columnas)
    datos["Método"] = metodo

    return datos


# ─────────────────────────────
# Archivos
# ─────────────────────────────
con_analisis = cargar_datos(
    "data_dash_m2_analisis_criticas.csv",
    "Con análisis"
)

sin_analisis = cargar_datos(
    "data_dash_m2_sin_analisis_criticas.csv",
    "Sin análisis"
)

sin_fines = cargar_datos(
    "data_dash_m2_sinfines.csv",
    "Sin fines de semana"
)


datos_totales = pd.concat(
    [
        con_analisis,
        sin_analisis,
        sin_fines
    ],
    ignore_index=True
)


# ─────────────────────────────
# Selectores
# ─────────────────────────────
st.title(
    "Comparativa: con análisis, sin análisis y sin fines de semana"
)


# Años comunes a los 3 métodos
años_comunes = sorted(
    set(con_analisis["Año"])
    & set(sin_analisis["Año"])
    & set(sin_fines["Año"])
)

if not años_comunes:
    st.error("Los tres métodos no tienen años en común.")
    st.stop()


año = st.selectbox(
    "Selecciona el año",
    años_comunes,
    format_func=lambda valor: f"{valor:.0f}"
)


con_año = con_analisis[
    con_analisis["Año"] == año
]

sin_año = sin_analisis[
    sin_analisis["Año"] == año
]

sinfines_año = sin_fines[
    sin_fines["Año"] == año
]


# ─────────────────────────────
# Tiempo de predicción
# ─────────────────────────────
tiempos_comunes = sorted(
    set(con_año["Tiempo de predicción"])
    & set(sin_año["Tiempo de predicción"])
    & set(sinfines_año["Tiempo de predicción"])
)

if not tiempos_comunes:
    st.error(
        "Los tres métodos no tienen tiempos de predicción en común."
    )
    st.stop()


tiempo = st.selectbox(
    "Tiempo de predicción (en horas)",
    tiempos_comunes,
    format_func=lambda valor: f"{valor:g} horas"
)


con_filtrado = con_año[
    con_año["Tiempo de predicción"] == tiempo
]

sin_filtrado = sin_año[
    sin_año["Tiempo de predicción"] == tiempo
]

sinfines_filtrado = sinfines_año[
    sinfines_año["Tiempo de predicción"] == tiempo
]


# ─────────────────────────────
# Presupuesto
# ─────────────────────────────
presupuestos_comunes = sorted(
    set(con_filtrado["Presupuesto de horas"])
    & set(sin_filtrado["Presupuesto de horas"])
    & set(sinfines_filtrado["Presupuesto de horas"])
)

if not presupuestos_comunes:
    st.error(
        "Los tres métodos no tienen presupuestos en común."
    )
    st.stop()


presupuesto = st.select_slider(
    "Presupuesto de horas",
    options=presupuestos_comunes
)


# ─────────────────────────────
# Resultados seleccionados
# ─────────────────────────────
horas_con = con_filtrado.loc[
    con_filtrado["Presupuesto de horas"] == presupuesto,
    "Horas acertadas"
].iloc[0]


horas_sin = sin_filtrado.loc[
    sin_filtrado["Presupuesto de horas"] == presupuesto,
    "Horas acertadas"
].iloc[0]


horas_sinfines = sinfines_filtrado.loc[
    sinfines_filtrado["Presupuesto de horas"] == presupuesto,
    "Horas acertadas"
].iloc[0]


col1, col2, col3 = st.columns(3)

col1.metric(
    "Con análisis",
    f"{horas_con:.0f} de 100"
)

col2.metric(
    "Sin análisis",
    f"{horas_sin:.0f} de 100"
)

col3.metric(
    "Sin fines de semana",
    f"{horas_sinfines:.0f} de 100"
)


# ─────────────────────────────
# Gráfica comparativa
# ─────────────────────────────
datos_seleccionados = datos_totales[
    (datos_totales["Año"] == año)
    & (datos_totales["Tiempo de predicción"] == tiempo)
].sort_values("Presupuesto de horas")


fig = px.line(
    datos_seleccionados,
    x="Presupuesto de horas",
    y="Horas acertadas",
    color="Método",
    markers=True,
    range_y=[0, 100],
    title=(
        f"Comparación de métodos — Año {año:.0f} — "
        f"{tiempo:g} horas de anticipación"
    ),
    color_discrete_map={
        "Con análisis": "#1f77b4",
        "Sin análisis": "#ff7f0e",
        "Sin fines de semana": "#2ca02c"
    }
)


fig.add_vline(
    x=presupuesto,
    line_dash="dash",
    line_color="gray"
)


fig.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ─────────────────────────────
# Tabla comparativa
# ─────────────────────────────
tabla = datos_seleccionados.pivot_table(
    index="Presupuesto de horas",
    columns="Método",
    values="Horas acertadas",
    aggfunc="first"
).reset_index()


# Diferencias respecto a "Sin análisis"
if (
    "Con análisis" in tabla.columns
    and "Sin análisis" in tabla.columns
):
    tabla["Con análisis − Sin análisis"] = (
        tabla["Con análisis"]
        - tabla["Sin análisis"]
    )


if (
    "Sin fines de semana" in tabla.columns
    and "Sin análisis" in tabla.columns
):
    tabla["Sin fines − Sin análisis"] = (
        tabla["Sin fines de semana"]
        - tabla["Sin análisis"]
    )


st.subheader("Datos comparativos")

st.dataframe(
    tabla,
    use_container_width=True
)