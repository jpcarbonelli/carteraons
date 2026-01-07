import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="Mi Renta Fija", layout="wide")

# --- INFO DE TUS BONOS (Tasas y Meses de cobro) ---
INFO_BONOS = {
    "MGCOD": {"tasa": 0.095, "meses": [5, 11]},
    "YMCJD": {"tasa": 0.09, "meses": [3, 9]},
    "MR35D": {"tasa": 0.095, "meses": [5, 11]},
    "IRCPD": {"tasa": 0.0875, "meses": [1, 7]},
    "GEMSA": {"tasa": 0.10, "meses": [2, 8]},
    "ARC1O": {"tasa": 0.07, "meses": [4, 10]},
    "YMCHO": {"tasa": 0.09, "meses": [1, 7]}
}

st.title("💰 Mi Flujo de Caja Anual")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error("Error conectando a la base de datos.")
    df_db = pd.DataFrame()

# --- CÁLCULO DE FLUJO MENSUAL ---
if not df_db.empty:
    cronograma = []
    nombres_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    for _, fila in df_db.iterrows():
        ticker = fila['ticker']
        cant = fila['cantidad']
        if ticker in INFO_BONOS:
            pago_semestral = (cant * INFO_BONOS[ticker]['tasa']) / 2
            for m in INFO_BONOS[ticker]['meses']:
                cronograma.append({"Mes": nombres_meses[m-1], "Monto": pago_semestral, "Ticker": ticker, "Orden": m})

    df_flujo = pd.DataFrame(cronograma).sort_values("Orden")

    # GRÁFICO DE BARRAS (Tu flujo mes a mes)
    st.subheader("Proyección Mensual de Cobros (USD)")
    fig = px.bar(df_flujo, x="Mes", y="Monto", color="Ticker", text_auto='.2f',
                 title="Intereses a cobrar cada mes")
    st.plotly_chart(fig, use_container_width=True)
    
    # MÉTRICA TOTAL
    st.metric("Total Intereses Anuales", f"US$ {df_flujo['Monto'].sum():,.2f}")

# --- FORMULARIO LATERAL ---
with st.sidebar.form("carga"):
    st.header("Cargar Activo")
    t = st.selectbox("Ticker", list(INFO_BONOS.keys()))
    c = st.number_input("Cantidad", min_value=1)
    if st.form_submit_button("Guardar y Ver Flujo"):
        conn.table("carteras").insert({"email": "usuario@test.com", "ticker": t, "cantidad": c}).execute()
        st.success("¡Guardado!")
        st.rerun()
