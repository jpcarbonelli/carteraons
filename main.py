import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="ON Investor Pro", layout="wide", page_icon="📈")

# 2. CONEXIÓN A SUPABASE
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_db = pd.DataFrame()

st.title("📊 Mi Cartera de Renta Fija Inteligente")

# 3. PROCESAMIENTO DE DATOS
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    hoy = datetime.now().date()
    
    for _, fila in df_db.iterrows():
        try:
            cantidad = float(fila['cantidad'])
            tasa_cupon = float(fila.get('tasa', 0)) / 100
            ppc = float(fila.get('precio_promedio_compra', 100)) / 100 
            
            pago_anual = cantidad * tasa_cupon
            pago_semestral = pago_anual / 2
            
            meses_indices = [int(m.strip()) for m in str(fila.get('meses_cobro', '1, 7')).split(",")]
            
            for m in meses_indices:
                cronograma.append({
                    "Mes": meses_nombres[m-1],
                    "USD": pago_semestral,
                    "Ticker": fila['ticker'],
                    "Orden_Mes": m
                })
        except: continue

    if cronograma:
        df_flujo = pd.DataFrame(cronograma).sort_values("Orden_Mes")
        
        # --- MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        total_flujo = df_flujo['USD'].sum()
        m1.metric("Flujo Anual Total", f"US$ {total_flujo:,.2f}")
        
        if 'tasa' in df_db and 'precio_promedio_compra' in df_db:
            y_prom = (df_db['tasa'] / df_db['precio_promedio_compra']).mean() / 100
            m2.metric("Yield Promedio (CY)", f"{y_prom:.2%}")
        
        capital_inv = (df_db['cantidad'] * (df_db['precio_promedio_compra']/100)).sum()
        m3.metric("Inversión Estimada", f"US$ {capital_inv:,.2f}")

        # --- GRÁFICO ---
        fig = px.bar(
            df_flujo, x="Mes", y="USD", color="Ticker", 
            text_auto='.2f', category_orders={"Mes": meses_nombres},
            title="Proyección de Cobros Mensuales (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- GESTIÓN DE ACTIVOS ---
        st.subheader("📋 Detalle de la Cartera")
        for _, fila in df_db.iterrows():
            with st.expander(f"📌 {fila['ticker']} - {fila['cantidad']:,} nominales"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**PPC:** {fila['precio_promedio_compra']}%")
                c1.write(f"**Tasa:** {fila['tasa']}%")
                
                # Aquí agregamos la visualización de la fecha de emisión
                c2.write(f"**Emisión:** {fila.get('f_emision', 'S/D')}")
                c2.write(f"**Vencimiento:** {fila.get('f_vencimiento', 'S/D')}")
                
                if fila.get('f_vencimiento'):
                    try:
                        venc = datetime.strptime(str(fila['f_vencimiento']), '%Y-%m-%d').date()
                        dias = (venc
