import streamlit as st
import pandas as pd
import altair as alt

# --- indicadores ---
INDICADORES_BASE = [
    "Instalacion de dispositivo", "Revision de dispositivo", "Reemplazo de dispositivo",
    "Reubicacion de dispositivo", "Reubicacion de equipo", "Exceso de velocidad",
    "Fallas de equipo", "Supension de gps", "Sistema de gps", "Dañadas en el taller",
    "Averia de equipo", "Rutas no permitidas", "Secuestro de unidad",
    "Paradas largas por unidad accidentada", "Camara cubierta", "Uso de celular",
    "Ojos cerrados", "Bostezo", "Fumar", "Traslado de personal", "Cruce indebido",
    "Fuera de ruta", "Carga no autorizada", "Parada no autorizada"
]

if "eventos" not in st.session_state:
    st.session_state.eventos = pd.DataFrame(columns=[
        "Número de reporte", "Fecha", "Indicador", "Unidad", "Conductor", "Km/h", "Ubicación", "Descripción"
    ])

if "indicadores" not in st.session_state or len(st.session_state.indicadores) == 0:
    st.session_state.indicadores = INDICADORES_BASE.copy()

# --- Función para generar número correlativo y llevar el orden ---
def generar_numero_reporte():
    if st.session_state.eventos.empty:
        return "MGPS-0001"
    else:
        ultimo = st.session_state.eventos["Número de reporte"].iloc[-1]
        numero = int(ultimo.split("-")[1])
        nuevo = numero + 1
        return f"MGPS-{nuevo:04d}"

# --- Banner ---
st.markdown("""
    <style>
    .banner-container {
        background-color: #2e7d32;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .banner-logo {
        width: 100px;
        height: auto;
        margin-bottom: 10px;
    }
    .banner-title {
        font-size: 24px;
        font-weight: bold;
    }
    .section {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .metric-card {
        background-color: #d0e6d3;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #2e7d32;
        font-size: 16px;
        font-weight: 600;
        color: #1b1b1b;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="banner-container">
        <img src="https://fospuca.com/wp-content/uploads/2018/08/fospuca.png" class="banner-logo">
        <div class="banner-title"> Cuadro de Eventos - Fospuca</div>
    </div>
""", unsafe_allow_html=True)

# --- Pestañas principales ---
tab1, tab2, tab3 = st.tabs(["➕ Gestión de eventos", "📋 Eventos y distribución", "📊 Indicadores"])

# --- TAB 1: Gestión de eventos ---
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Añadir nuevo evento")

    numero_reporte = generar_numero_reporte()
    st.text_input("Número de reporte", value=numero_reporte, disabled=True)

    fecha = st.date_input("Fecha")
    
    # Selector con opción vacía al inicio
    indicador_seleccionado = st.selectbox(
        "Indicador",
        [""] + st.session_state.indicadores,
        index=0  # Muestra la opción vacía por defecto
    )
    
    unidad = st.text_input("Unidad")
    conductor = st.text_input("Conductor")
    ubicacion = st.text_input("Ubicación")
    descripcion = st.text_area("Descripción")

    kmh = None
    if indicador_seleccionado == "Exceso de velocidad":
        kmh = st.number_input("Velocidad (km/h)", min_value=0, step=1, value=0)

    if st.button("Agregar evento"):
        if not indicador_seleccionado:
            st.error("Por favor, selecciona un indicador.")
        elif indicador_seleccionado == "Exceso de velocidad":
            if kmh <= 0:
                st.error("Debes ingresar una velocidad mayor a 0 (km/h) para el indicador 'Exceso de velocidad'.")
            else:
                nuevo = {
                    "Número de reporte": numero_reporte,
                    "Fecha": fecha,
                    "Indicador": indicador_seleccionado,
                    "Unidad": unidad,
                    "Conductor": conductor,
                    "Km/h": kmh,
                    "Ubicación": ubicacion,
                    "Descripción": descripcion
                }
                st.session_state.eventos = pd.concat(
                    [st.session_state.eventos, pd.DataFrame([nuevo])],
                    ignore_index=True
                )
                st.success(f"Evento agregado ✅ (Reporte {numero_reporte})")
        else:
            nuevo = {
                "Número de reporte": numero_reporte,
                "Fecha": fecha,
                "Indicador": indicador_seleccionado,
                "Unidad": unidad,
                "Conductor": conductor,
                "Km/h": None,
                "Ubicación": ubicacion,
                "Descripción": descripcion
            }
            st.session_state.eventos = pd.concat(
                [st.session_state.eventos, pd.DataFrame([nuevo])],
                ignore_index=True
            )
            st.success(f"Evento agregado ✅ (Reporte {numero_reporte})")

    st.subheader("Eliminar evento")
    if not st.session_state.eventos.empty:
        opciones_borrado = [f"{i+1} - {row['Número de reporte']}" for i, row in st.session_state.eventos.iterrows()]
        seleccion = st.selectbox("Selecciona evento a eliminar", opciones_borrado)
        borrar_idx = int(seleccion.split(" - ")[0]) - 1

        if st.button("Eliminar seleccionado"):
            st.session_state.confirmar_borrado = borrar_idx

        if "confirmar_borrado" in st.session_state:
            evento = st.session_state.eventos.loc[st.session_state.confirmar_borrado]
            resumen = f"Reporte: {evento['Número de reporte']} | Fecha: {evento['Fecha']} | Unidad: {evento['Unidad']} | Indicador: {evento['Indicador']}"
            st.warning(f"¿Seguro que quieres eliminar este evento?\n\n{resumen}")
            col1, col2 = st.columns(2)
            if col1.button("✅ Sí, eliminar"):
                st.session_state.eventos = st.session_state.eventos.drop(st.session_state.confirmar_borrado).reset_index(drop=True)
                if "confirmar_borrado" in st.session_state:
                    del st.session_state["confirmar_borrado"]
                st.success("Evento eliminado ❌")
            if col2.button("❌ Cancelar"):
                if "confirmar_borrado" in st.session_state:
                    del st.session_state["confirmar_borrado"]
                st.info("Eliminación cancelada")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Eventos y distribución ---
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Eventos registrados")
    unidad_filtro = st.selectbox("Filtrar por unidad", ["Todas"] + list(st.session_state.eventos["Unidad"].unique()))
    indicador_filtro = st.selectbox("Filtrar por indicador", ["Todos"] + st.session_state.indicadores)

    df_filtrado = st.session_state.eventos.copy()
    if unidad_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Unidad"] == unidad_filtro]
    if indicador_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Indicador"] == indicador_filtro]

    # Eliminar columna de Correlativo (por si acaso)
    if "Correlativo" in df_filtrado.columns:
        df_filtrado = df_filtrado.drop(columns=["Correlativo"])

    st.dataframe(df_filtrado)

    st.subheader("Distribución por tipo de evento")
    if not df_filtrado.empty:
        chart = alt.Chart(df_filtrado).mark_bar(size=20, color="#2e7d32").encode(
            x=alt.X("Indicador:N", sort="-y", title="Tipo de evento"),
            y=alt.Y("count():Q", title="Cantidad"),
            tooltip=["Indicador", "count()"]
        ).properties(
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No hay eventos para mostrar con los filtros seleccionados.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Indicadores ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Indicadores Totales")
    if len(st.session_state.indicadores) > 0:
        for ind in st.session_state.indicadores:
            count = st.session_state.eventos[st.session_state.eventos["Indicador"] == ind].shape[0]
            st.markdown(f'<div class="metric-card">{ind}<br><b>{count}</b></div>', unsafe_allow_html=True)
    else:
        st.info("No hay indicadores definidos. Agrega uno en la pestaña de gestión ⚙️")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.caption("Cuadro de eventos BETA 0.1 - Fospuca Caroní")