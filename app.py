from pathlib import Path

output = Path("/mnt/data/app_2_modelos.py")

codigo = r'''import hmac
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
m2 = cargar_datos(
    "data_dash_m2_sinfines.csv",
    "M2"
)

m3 = cargar_datos(
    "data_dash_m3_sinfines.csv",
    "M3"
)


datos_totales = pd.concat(
    [
        m2,
        m3
    ],
    ignore_index=True
)


# ─────────────────────────────
# Selectores
# ─────────────────────────────
st.title(
    "Comparativa: M2 vs M3"
)


# Años comunes a los 2 métodos
años_comunes = sorted(
    set(m2["Año"])
    & set(m3["Año"])
)

if not años_comunes:
    st.error("Los dos métodos no tienen años en común.")
    st.stop()


año = st.selectbox(
    "Selecciona el año",
    años_comunes,
    format_func=lambda valor: f"{valor:.0f}"
)


m2_año = m2[
    m2["Año"] == año
]

m3_año = m3[
    m3["Año"] == año
]


# ─────────────────────────────
# Tiempo de predicción
# ─────────────────────────────
tiempos_comunes = sorted(
    set(m2_año["Tiempo de predicción"])
    & set(m3_año["Tiempo de predicción"])
)

if not tiempos_comunes:
    st.error(
        "Los dos métodos no tienen tiempos de predicción en común."
    )
    st.stop()


tiempo = st.selectbox(
    "Tiempo de predicción (en horas)",
    tiempos_comunes,
    format_func=lambda valor: f"{valor:g} horas"
)


m2_filtrado = m2_año[
    m2_año["Tiempo de predicción"] == tiempo
]

m3_filtrado = m3_año[
    m3_año["Tiempo de predicción"] == tiempo
]


# ─────────────────────────────
# Presupuesto
# ─────────────────────────────
presupuestos_comunes = sorted(
    set(m2_filtrado["Presupuesto de horas"])
    & set(m3_filtrado["Presupuesto de horas"])
)

if not presupuestos_comunes:
    st.error(
        "Los dos métodos no tienen presupuestos en común."
    )
    st.stop()


presupuesto = st.select_slider(
    "Presupuesto de horas",
    options=presupuestos_comunes
)


# ─────────────────────────────
# Resultados seleccionados
# ─────────────────────────────
horas_m2 = m2_filtrado.loc[
    m2_filtrado["Presupuesto de horas"] == presupuesto,
    "Horas acertadas"
].iloc[0]


horas_m3 = m3_filtrado.loc[
    m3_filtrado["Presupuesto de horas"] == presupuesto,
    "Horas acertadas"
].iloc[0]


col1, col2 = st.columns(2)

col1.metric(
    "M2",
    f"{horas_m2:.0f} de 100"
)

col2.metric(
    "M3",
    f"{horas_m3:.0f} de 100"
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
        "M2": "#1f77b4",
        "M3": "#ff7f0e"
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


if (
    "M2" in tabla.columns
    and "M3" in tabla.columns
):
    tabla["M3 − M2"] = (
        tabla["M3"]
        - tabla["M2"]
    )


st.subheader("Datos comparativos")

st.dataframe(
    tabla,
    use_container_width=True
)
'''

output.write_text(codigo, encoding="utf-8")
print(f"Archivo creado: {output}")
