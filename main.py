import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="Gestor de Renta Fija", layout="wide")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    # Traemos todo de la base
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error("Error de conexión.")
    df_db = pd.DataFrame()

st.title("📈 Mi Flujo de Caja Automatizado")

# --- LÓGICA DE FLUJO ---
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    # Verificamos si las columnas existen, si no, las creamos con valores por defecto
    if 'tasa' not in df_db.columns: df_db['tasa'] = 0.08
    if 'meses_cobro' not in df_db.columns: df_db['meses_cobro'] = "1, 7"

    for _, fila in df_db.iterrows():
        try:
            # Calculamos el pago semestral basado en lo guardado
            pago_anual = float(fila['cantidad']) * (float(fila['tasa']) / 100)
            pago_semestral = pago_anual / 2
            
            # Convertimos el texto "1, 7" en una lista de números [1, 7]
            meses = [int(m.strip()) for m in str(fila['meses_cobro']).split(",")]
            
            for m in meses:
                cronograma.append({
                    "Mes": meses_nombres[m-1],
                    "USD": pago_semestral,
                    "Ticker": fila['ticker'],
                    "Orden": m
                })
        except:
            continue

    if cronograma:
        df_flujo = pd.DataFrame(cronograma).sort_values("Orden")
        
        # Dashboard
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(df_flujo, x="Mes", y="USD", color="Ticker", text_auto='.2f',
                         title="Cobros Mensuales Proyectados")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.metric("Total Intereses Anuales", f"US$ {df_flujo['USD'].sum():,.2f}")
            st.write("### Tus Tenencias")
            st.dataframe(df_db[['ticker', 'cantidad', 'tasa']], hide_index=True)

# --- PANEL LATERAL DE CARGA INTELIGENTE ---
with st.sidebar:
    st.header("📥 Cargar/Editar Activo")
    with st.form("form_final"):
        ticker = st.text_input("Ticker (ej: MGCOD)").upper()
        cantidad = st.number_input("Cantidad Nominal", min_value=0)
        tasa = st.number_input("Tasa Anual (%)", min_value=0.0, format="%.2f")
        meses_cobro = st.text_input("Meses de cobro (separados por coma)", value="1, 7")
        st.caption("Ejemplo: Si paga en Enero y Julio, poné: 1, 7")
        
        if st.form_submit_button("Guardar en mi Cartera"):
            nueva_data = {
                "email": "usuario@test.com",
                "ticker": ticker,
                "cantidad": cantidad,
                "tasa": tasa,
                "meses_cobro": meses_cobro
            }
            conn.table("carteras").insert(nueva_data).execute()
            st.success("¡Activo guardado con su flujo!")
            st.rerun()
