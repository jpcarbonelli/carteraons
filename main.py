import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="ON Investor Pro", layout="wide")

# --- BASE DE DATOS TÉCNICA (Tasas y Meses de Pago) ---
# 'meses': [mes1, mes2] representan los meses del año en que paga cupón
DATOS_ONS = {
    "MGCOD": {"tasa": 0.08, "meses": [1, 7], "nombre": "Mastellone 2026"},
    "YMCJD": {"tasa": 0.09, "meses": [3, 9], "nombre": "YPF 2026"},
    "MR35D": {"tasa": 0.095, "meses": [5, 11], "nombre": "Gen. Mediterránea"},
    "IRCPD": {"tasa": 0.0875, "meses": [1, 7], "nombre": "IRSA 2028"},
    "GEMSA": {"tasa": 0.10, "meses": [2, 8], "nombre": "MSU Energy"},
    "ARC1O": {"tasa": 0.07, "meses": [4, 10], "nombre": "Arcor 2027"},
    "YMCHO": {"tasa": 0.09, "meses": [1, 7], "nombre": "YPF 2029"},
    "CSDO":  {"tasa": 0.08, "meses": [2, 8], "nombre": "Cresud 2026"},
}

st.title("📈 Flujo de Caja Mensual y Cartera")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_db = pd.DataFrame()

if not df_db.empty:
    # --- PROCESAMIENTO FINANCIERO ---
    # 1. Expandir los pagos a nivel mensual
    pagos_mensuales = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    for _, fila in df_db.iterrows():
        ticker = fila['ticker']
        cantidad = fila['cantidad']
        if ticker in DATOS_ONS:
            info = DATOS_ONS[ticker]
            monto_pago = (cantidad * info['tasa']) / 2  # Pago semestral
            for mes in info['meses']:
                pagos_mensuales.append({
                    "Mes": meses_nombres[mes-1],
                    "Mes_Num": mes,
                    "Ticker": ticker,
                    "Monto": monto_pago
                })

    df_flujo = pd.DataFrame(pagos_mensuales)
    
    # --- MÉTRICAS ---
    total_anual = df_flujo["Monto"].sum() if not df_flujo.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Anuales Totales", f"US$ {total_anual:,.2f}")
    c2.metric("Promedio Mensual", f"US$ {total_anual/12:,.2f}")
    c3.metric("Total Activos", df_db['ticker'].nunique())

    st.divider()

    # --- GRÁFICO DE FLUJO MENSUAL ---
    st.subheader("🗓 Proyección de Cobros Mensuales (Flujo de Caja)")
    if not df_flujo.empty:
        # Agrupar por mes para el gráfico
        df_agrupado = df_flujo.groupby(["Mes", "Mes_Num", "Ticker"])["Monto"].sum().reset_index()
        df_agrupado = df_agrupado.sort_values("Mes_Num")

        fig_flujo = px.bar(
            df_agrupado, 
            x="Mes", 
            y="Monto", 
            color="Ticker",
            title="Dólares a cobrar por mes",
            labels={"Monto": "USD"},
            text_auto='.2f'
        )
        st.plotly_chart(fig_flujo, use_container_width=True)
    
    # --- TABLA DE DETALLE ---
    with st.expander("Ver detalle de tenencias y tasas"):
        df_db['Tasa'] = df_db['ticker'].map(lambda x: DATOS_ONS.get(x, {}).get('tasa', 0))
        st.dataframe(df_db[['ticker', 'cantidad', 'Tasa']], use_container_width=True)

else:
    st.info("Cargá tus primeras ONs en el panel lateral para ver el flujo proyectado.")

# --- SIDEBAR: CARGA ---
with st.sidebar.form("form_add"):
    st.header("📥 Cargar Activo")
    email = st.text_input("Email", value="jpcarbonelli@yahoo.com.ar")
    ticker = st.selectbox("Seleccioná Ticker", list(DATOS_ONS.keys()))
    cantidad = st.number_input("Cantidad Nominal (US$)", min_value=1, step=500)
    
    if st.form_submit_button("Guardar"):
        conn.table("carteras").insert({"email": email, "ticker": ticker, "cantidad": cantidad}).execute()
        st.success("Guardado!")
        st.rerun()
