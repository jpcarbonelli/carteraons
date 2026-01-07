import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

st.set_page_config(page_title="ON Investor Pro", layout="wide")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error("Error de conexión con la base de datos.")
    df_db = pd.DataFrame()

st.title("📈 Mi Flujo de Caja Mensual")

# --- LÓGICA DE FLUJO Y VISUALIZACIÓN ---
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    # Aseguramos que existan las columnas para evitar errores de código
    for col in ['tasa', 'meses_cobro', 'id']:
        if col not in df_db.columns: df_db[col] = None

    for _, fila in df_db.iterrows():
        try:
            pago_anual = float(fila['cantidad']) * (float(fila.get('tasa', 0)) / 100)
            pago_semestral = pago_anual / 2
            meses = [int(m.strip()) for m in str(fila.get('meses_cobro', '1, 7')).split(",")]
            
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
        
        # 1. Gráfico Principal
        fig = px.bar(df_flujo, x="Mes", y="USD", color="Ticker", text_auto='.2f',
                     title="Proyección de Cobros Mensuales (USD)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # 2. Gestión de Cartera (Tabla con botones de borrado)
        st.subheader("📋 Gestión de Activos Cargados")
        cols_header = st.columns([2, 2, 2, 2, 1])
        cols_header[0].write("**Ticker**")
        cols_header[1].write("**Cantidad**")
        cols_header[2].write("**Tasa**")
        cols_header[3].write("**Meses**")
        cols_header[4].write("**Acción**")

        for _, fila in df_db.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
            c1.write(fila['ticker'])
            c2.write(f"{fila['cantidad']:,}")
            c3.write(f"{fila['tasa']}%")
            c4.write(fila['meses_cobro'])
            
            # Botón único para cada fila usando su ID de Supabase
            if c5.button("🗑️", key=f"del_{fila['id']}"):
                conn.table("carteras").delete().eq("id", fila['id']).execute()
                st.success(f"Eliminado {fila['ticker']}")
                st.rerun()

# --- PANEL LATERAL DE CARGA ---
with st.sidebar:
    st.header("📥 Cargar Activo")
    with st.form("form_carga"):
        t = st.text_input("Ticker").upper()
        cant = st.number_input("Cantidad Nominal", min_value=0, step=500)
        tas = st.number_input("Tasa Anual (%)", min_value=0.0, format="%.2f")
        mes = st.text_input("Meses de cobro (ej: 1, 7)", value="1, 7")
        
        if st.form_submit_button("Guardar en Cartera"):
            if t and cant > 0:
                conn.table("carteras").insert({
                    "email": "usuario@test.com", "ticker": t, 
                    "cantidad": cant, "tasa": tas, "meses_cobro": mes
                }).execute()
                st.rerun()
            else:
                st.error("Completá Ticker y Cantidad.")
