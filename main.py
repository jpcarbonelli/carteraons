import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="Mi Cartera ONs", layout="wide")
st.title("🚀 Panel de Control de Inversiones")

# --- CONEXIÓN (La que ya funciona) ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    
    res = conn.table("carteras").select("*").execute()
    df = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df = pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
if not df.empty:
    # 1. Indicadores rápidos (Métricas)
    col1, col2, col3 = st.columns(3)
    total_nominales = df["cantidad"].sum()
    activos_distintos = df["ticker"].nunique()
    
    col1.metric("Total Nominales", f"{total_nominales:,}")
    col2.metric("Tipos de ONs", activos_distintos)
    col3.metric("Última Carga", df["ticker"].iloc[-1])

    # 2. Gráfico y Tabla lado a lado
    fila_graficos = st.columns([1, 1])
    
    with fila_graficos[0]:
        st.subheader("Distribución de Cartera")
        fig = px.pie(df, values='cantidad', names='ticker', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    with fila_graficos[1]:
        st.subheader("Detalle de Registros")
        st.dataframe(df[["email", "ticker", "cantidad"]], use_container_width=True, hide_index=True)

else:
    st.info("La tabla está vacía. Cargá datos en el panel lateral.")

# --- FORMULARIO LATERAL (Sin cambios en las columnas) ---
st.sidebar.header("📥 Cargar Nuevo Activo")
with st.sidebar.form("form_carga"):
    user_email = st.text_input("Email", value="jpcarbonelli@yahoo.com.ar")
    ticker_input = st.selectbox("Ticker", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA", "ARC1O"])
    cantidad_input = st.number_input("Cantidad", min_value=1, step=1)
    
    if st.form_submit_button("Guardar en Nube"):
        nueva_fila = {"email": user_email, "ticker": ticker_input, "cantidad": cantidad_input}
        conn.table("carteras").insert(nueva_fila).execute()
        st.success("¡Datos actualizados!")
        st.rerun()
