import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="ON Investor Pro", layout="wide")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except:
    df_db = pd.DataFrame()

st.title("📊 Mi Cartera de Renta Fija Inteligente")

# --- PROCESAMIENTO DE DATOS ---
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    hoy = datetime.now().date()
    
    for _, fila in df_db.iterrows():
        try:
            cantidad = float(fila['cantidad'])
            tasa_cupon = float(fila.get('tasa', 0)) / 100
            # Usamos el nuevo nombre de campo
            ppc = float(fila.get('precio_promedio_compra', 100)) / 100 
            
            # Rentabilidad Real sobre lo invertido
            renta_real = (tasa_cupon / ppc) if ppc > 0 else tasa_cupon
            
            # Flujo de caja
            pago_anual = cantidad * tasa_cupon
            pago_semestral = pago_anual / 2
            
            meses = [int(m.strip()) for m in str(fila.get('meses_cobro', '1, 7')).split(",")]
            
            for m in meses:
                cronograma.append({
                    "Mes": meses_nombres[m-1],
                    "USD": pago_semestral,
                    "Ticker": fila['ticker'],
                    "Renta Real (CY)": renta_real,
                    "Orden": m
                })
        except: continue

    if cronograma:
        df_flujo = pd.DataFrame(cronograma).sort_values("Orden")
        
        # --- MÉTRICAS SUPERIORES ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Flujo Anual Total", f"US$ {df_flujo['USD'].sum():,.2f}")
        # Yield Promedio de la cartera (Ponderado por cantidad)
        yield_promedio = (df_db['tasa'] / df_db['precio_promedio_compra']).mean() / 100 if 'tasa' in df_db else 0
        m2.metric("Yield Promedio (CY)", f"{yield_promedio:.2%}")
        
        # --- GRÁFICO ---
        st.plotly_chart(px.bar(df_flujo, x="Mes", y="USD", color="Ticker", 
                               title="Cobros Mensuales Proyectados", text_auto='.2f'), use_container_width=True)

        # --- GESTIÓN Y DETALLE ---
        st.subheader("📋 Detalle de Activos y Rendimientos")
        
        # Mostramos la tabla de gestión con el botón de borrado
        for _, fila in df_db.iterrows():
            with st.expander(f"📌 {fila['ticker']} - Detalle"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Cantidad:** {fila['cantidad']:,}")
                c1.write(f"**PPC:** {fila['precio_promedio_compra']}%")
                
                c2.write(f"**Emisión:** {fila.get('f_emision', 'S/D')}")
                c2.write(f"**Vencimiento:** {fila.get('f_vencimiento', 'S/D')}")
                
                # Cálculo de días restantes
                if fila.get('f_vencimiento'):
                    venc = datetime.strptime(fila['f_vencimiento'], '%Y-%m-%d').date()
                    dias_faltan = (venc - hoy).days
                    c3.warning(f"Días al Vencimiento: {max(0, dias_faltan)}")
                
                if st.button("Eliminar Registro", key=f"del_{fila['id']}"):
                    conn.table("carteras").delete().eq("id", fila['id']).execute()
                    st.rerun()

# --- SIDEBAR: CARGA CON PRECIO PROMEDIO ---
with st.sidebar:
    st.header("📥 Nueva ON")
    with st.form("form_v2"):
        t = st.text_input("Ticker").upper()
        c = st.number_input("Cantidad Nominal", min_value=0)
        tas = st.number_input("Tasa Cupón Anual (%)", format="%.2f")
        ppc_input = st.number_input("Precio Promedio de Compra (%)", value=100.0)
        
        f_emi = st.date_input("Fecha de Emisión")
        f_ven = st.date_input("Fecha de Vencimiento")
        
        mes = st.text_input("Meses de Pago (ej: 5, 11)", value="1, 7")
        
        if st.form_submit_button("Guardar Activo"):
            conn.table("carteras").insert({
                "email": "jpcarbonelli@yahoo.com.ar",
                "ticker": t,
                "cantidad": c,
                "tasa": tas,
                "precio_promedio_compra": ppc_input,
                "f_emision": str(f_emi),
                "f_vencimiento": str(f_ven),
                "meses_cobro": mes
            }).execute()
            st.rerun()
