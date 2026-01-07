import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración visual
st.set_page_config(page_title="ON Investor Pro", layout="wide")
st.title("🚀 ON Investor Pro")

# --- BASE MAESTRA ACTUALIZADA ---
base_maestra = {
    base_maestra = {
    "MGCOD": {"tasa": 0.0800, "sector": "Energía", "estado": "Vigente"},
    "YMCJD": {"tasa": 0.0900, "sector": "Petróleo & Gas", "estado": "Vigente"},
    "MR35D": {"tasa": 0.0950, "sector": "Consumo Masivo", "estado": "Vigente"},
    "VSCTD": {"tasa": 0.0850, "sector": "Petróleo & Gas", "estado": "Vigente"},
    "IRCPD": {"tasa": 0.0800, "sector": "Real Estate", "estado": "Vigente"},
    "HJCID": {"tasa": 0.0825, "sector": "Energía", "estado": "Vigente"},
    "HJCJD": {"tasa": 0.0825, "sector": "Energía", "estado": "Vigente"},
    "PN36D": {"tasa": 0.0900, "sector": "Petróleo & Gas", "estado": "Vigente"},
    "PLC4D": {"tasa": 0.0800, "sector": "Telecomunicaciones", "estado": "Vigente"},
    "TLCQD": {"tasa": 0.0850, "sector": "Telecomunicaciones", "estado": "Vigente"},
    "TLCPD": {"tasa": 0.0850, "sector": "Telecomunicaciones", "estado": "Vigente"},
    "CS48D": {"tasa": 0.0750, "sector": "Real Estate", "estado": "Vigente"},
    "CS49D": {"tasa": 0.0750, "sector": "Real Estate", "estado": "Vigente"},
    "CIC9D": {"tasa": 0.0800, "sector": "Energía", "estado": "Vigente"},
    "CICAD": {"tasa": 0.0800, "sector": "Energía", "estado": "Vigente"},
    "GEMSA": {"tasa": 0.0000, "sector": "Energía", "estado": "Default"}
}
}

# --- ESTADO DE LA APP ---
if 'cartera' not in st.session_state:
    st.session_state.cartera = pd.DataFrame(columns=["Ticker", "Cantidad", "Sector", "Cobro_Estimado"])

# --- INTERFAZ ---
st.sidebar.header("Menú de Usuario")
with st.sidebar.expander("➕ Cargar Nuevo Activo", expanded=True):
    ticker = st.selectbox("Seleccioná Ticker", list(base_maestra.keys()))
    nominales = st.number_input("Nominales", min_value=0, step=100)
    if st.button("Guardar"):
        on_info = base_maestra[ticker]
        nuevo_item = {
            "Ticker": ticker, 
            "Cantidad": nominales,
            "Sector": on_info['sector'],
            "Cobro_Estimado": (nominales * on_info['tasa']) / 2 if on_info['estado'] == "Vigente" else 0
        }
        st.session_state.cartera = pd.concat([st.session_state.cartera, pd.DataFrame([nuevo_item])], ignore_index=True)

# --- DASHBOARD ---
if not st.session_state.cartera.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(st.session_state.cartera, values='Cantidad', names='Sector', title="Diversificación por Sector")
        st.plotly_chart(fig_pie)
    with col2:
        fig_bar = px.bar(st.session_state.cartera, x='Ticker', y='Cobro_Estimado', title="Cobro Próximo Cupón (USD)")
        st.plotly_chart(fig_bar)
    st.subheader("Tu Detalle de Cartera")
    st.dataframe(st.session_state.cartera)
else:
    st.info("Cargá tu primer activo en el menú lateral para empezar.")
