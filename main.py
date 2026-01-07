import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="ON Investor Pro", layout="wide")

# --- BASE DE DATOS TÉCNICA DE ONS (Tasas y Datos) ---
# Aquí podés actualizar las tasas (tasa_anual) según el mercado
DATOS_ONS = {
    "MGCOD": {"tasa_anual": 0.08, "nombre": "Mastellone 2026"},
    "YMCJD": {"tasa_anual": 0.09, "nombre": "YPF 2026"},
    "MR35D": {"tasa_anual": 0.095, "nombre": "Generación Mediterránea"},
    "IRCPD": {"tasa_anual": 0.0875, "nombre": "IRSA 2028"},
    "GEMSA": {"tasa_anual": 0.10, "nombre": "MSU Energy"},
    "ARC1O": {"tasa_anual": 0.07, "nombre": "Arcor 2027"},
    "YMCHO": {"tasa_anual": 0.09, "nombre": "YPF 2029"},
}

st.title("📊 Mi Cartera & Flujo de Caja")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_raw = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_raw = pd.DataFrame()

# --- LÓGICA FINANCIERA ---
if not df_raw.empty:
    # Cruzamos tus datos con la info financiera
    df_raw['tasa'] = df_raw['ticker'].map(lambda x: DATOS_ONS.get(x, {}).get('tasa_anual', 0))
    df_raw['nombre_on'] = df_raw['ticker'].map(lambda x: DATOS_ONS.get(x, {}).get('nombre', 'S/D'))
    
    # Cálculo de Flujo Anual: Cantidad * Tasa (asumiendo valor nominal 1 USD)
    df_raw['flujo_anual_estimado'] = df_raw['cantidad'] * df_raw['tasa']

    # --- MÉTRICAS SUPERIORES ---
    m1, m2, m3 = st.columns(3)
    total_invertido = df_raw['cantidad'].sum()
    flujo_total = df_raw['flujo_anual_estimado'].sum()
    tasa_promedio = (df_raw['tasa'] * df_raw['cantidad']).sum() / total_invertido if total_invertido > 0 else 0

    m1.metric("Total Nominales", f"US$ {total_invertido:,.0f}")
    m2.metric("Flujo de Caja Anual (Est.)", f"US$ {flujo_total:,.2f}", help="Suma de intereses anuales")
    m3.metric("Tasa Promedio Cartera", f"{tasa_promedio:.2%}")

    st.divider()

    # --- CUERPO PRINCIPAL ---
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("💰 Proyección de Ingresos")
        fig_bar = px.bar(df_raw, x='ticker', y='flujo_anual_estimado', 
                         title="Intereses Anuales por Ticker",
                         labels={'flujo_anual_estimado': 'USD Anuales'},
                         color='ticker', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("📝 Detalle de Tenencias")
        # Mostramos la tabla con las tasas
        st.dataframe(df_raw[['ticker', 'nombre_on', 'cantidad', 'tasa', 'flujo_anual_estimado']], 
                     column_config={
                         "tasa": st.column_config.NumberColumn("Tasa (Coupon)", format="%.2%"),
                         "flujo_anual_estimado": st.column_config.NumberColumn("Ingreso Anual", format="US$ %.2f")
                     },
                     hide_index=True, use_container_width=True)

else:
    st.info("Cargá activos para ver el análisis de flujo.")

# --- SIDEBAR: CARGA ---
with st.sidebar.form("nueva_carga"):
    st.header("📥 Cargar Activo")
    email = st.text_input("Email", value="jpcarbonelli@yahoo.com.ar")
    # Lista extendida de Tickers
    ticker = st.selectbox("Seleccioná ON", list(DATOS_ONS.keys()))
    cantidad = st.number_input("Cantidad Nominal", min_value=1, step=100)
    
    if st.form_submit_button("Guardar en Nube"):
        conn.table("carteras").insert({"email": email, "ticker": ticker, "cantidad": cantidad}).execute()
        st.success("Carga exitosa")
        st.rerun()
