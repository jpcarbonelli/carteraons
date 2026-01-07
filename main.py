import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="ON Investor Pro", layout="wide")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    # Leemos la base de datos
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_db = pd.DataFrame()

st.title("📊 Mi Cartera de Renta Fija Inteligente")

# --- PROCESAMIENTO DE DATOS ---
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    hoy = datetime.now().date()
    
    for _, fila in df_db.iterrows():
        try:
            # Cálculos base financieros
            cantidad = float(fila['cantidad'])
            tasa_cupon = float(fila.get('tasa', 0)) / 100
            ppc = float(fila.get('precio_promedio_compra', 100)) / 100 
            
            # Rentabilidad Real (Current Yield)
            renta_real = (tasa_cupon / ppc) if ppc > 0 else tasa_cupon
            pago_anual = cantidad * tasa_cupon
            pago_semestral = pago_anual / 2
            
            # Procesar meses de cobro
            meses_str = str(fila.get('meses_cobro', '1, 7'))
            meses_indices = [int(m.strip()) for m in meses_str.split(",")]
            
            for m in meses_indices:
                cronograma.append({
                    "Mes": meses_nombres[m-1],  # Nombre para el eje X
                    "USD": pago_semestral,
                    "Ticker": fila['ticker'],
                    "Renta Real (CY)": renta_real,
                    "Orden_Mes": m             # Número para ordenar
                })
        except: continue

    if cronograma:
        # Convertimos a DataFrame y ORDENAMOS por el número de mes
        df_flujo = pd.DataFrame(cronograma).sort_values("Orden_Mes")
        
        # --- MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Flujo Anual Total", f"US$ {df_flujo['USD'].sum():,.2f}")
        
        # Yield Promedio Ponderado
        if 'tasa' in df_db and 'precio_promedio_compra' in df_db:
            yield_promedio = (df_db['tasa'] / df_db['precio_promedio_compra']).mean() / 100
            m2.metric("Yield Promedio (CY)", f"{yield_promedio:.2%}")
        
        st.divider()
        
        # --- GRÁFICO (Respetando el orden cronológico) ---
        # El parámetro 'category_orders' asegura que el gráfico siga el orden de meses_nombres
        fig = px.bar(
            df_flujo, 
            x="Mes", 
            y="USD", 
            color="Ticker", 
            title="Cobros Mensuales Proyectados (Orden Cronológico)", 
            text_auto='.2f',
            category_orders={"Mes": meses_nombres} 
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- GESTIÓN DE ACTIVOS ---
        st.subheader("📋 Detalle y Gestión de Activos")
        for _, fila in df_db.iterrows():
            with st.expander(f"📌 {fila['ticker']} - Ver detalles"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Cantidad:** {fila['cantidad']:,}")
                c1.write(f"**PPC:** {fila['precio_promedio_compra']}%")
                
                c2.write(f"**Emisión:** {fila.get('f_emision')}")
                c2.write(f"**Vencimiento:** {fila.get('f_vencimiento')}")
                
                if fila.get('f_vencimiento'):
                    try:
                        venc = datetime.strptime(str(fila['f_vencimiento']), '%Y-%m-%d').date()
                        dias_faltan = (venc - hoy).days
                        c3.warning(f"Días al Vencimiento: {max(0, dias_faltan)}")
                    except: c3.write("Fecha vencimiento inválida")
                
                # Botón de eliminar con refresco automático
                if st.button("Eliminar", key=f"del_{fila['id']}"):
                    conn.table("carteras").delete().eq("id", fila['id']).execute()
                    st.rerun()

# --- SIDEBAR: FORMULARIO ---
with st.sidebar:
    st.header("📥 Nueva ON")
    with st.form("form_v2", clear_on_submit=True):
        t = st.text_input("Ticker").upper()
        c = st.number_input("Cantidad Nominal", min_value=0, step=500)
        tas = st.number_input("Tasa Cupón Anual (%)", format="%.2f")
        ppc_input = st.number_input("Precio Promedio de Compra (%)", value=100.0)
        
        f_emi = st.date_input("Fecha de Emisión")
        f_ven = st.date_input("Fecha de Vencimiento")
        
        mes = st.text_input("Meses de Pago (ej: 1, 7)", value="1, 7")
        
        if st.form_submit_button("Guardar Activo"):
            if t and c > 0:
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
                st.rerun() # Refresco automático para cargar el siguiente ticker
