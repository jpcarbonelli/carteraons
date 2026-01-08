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
                
                c2.write(f"**Vencimiento:** {fila.get('f_vencimiento', 'S/D')}")
                if fila.get('f_vencimiento'):
                    try:
                        venc = datetime.strptime(str(fila['f_vencimiento']), '%Y-%m-%d').date()
                        dias = (venc - hoy).days
                        c2.write(f"**Días para Vencer:** {max(0, dias)}")
                    except: pass
                
                if st.button("Eliminar posición", key=f"del_{fila['id']}"):
                    conn.table("carteras").delete().eq("id", fila['id']).execute()
                    st.rerun()

# --- SIDEBAR: REGISTRO ---
with st.sidebar:
    st.header("📥 Registrar Operación")
    with st.form("form_smart", clear_on_submit=True):
        t = st.text_input("Ticker (ej: MGCOD)").upper()
        c_new = st.number_input("Cantidad Nominales", min_value=0, step=100)
        tas = st.number_input("Tasa Cupón (%)", format="%.3f")
        p_new = st.number_input("Precio de Compra (%)", value=100.0)
        f_ven = st.date_input("Fecha Vencimiento")
        mes = st.text_input("Meses Pago (ej: 1, 7)", value="1, 7")
        
        if st.form_submit_button("Confirmar Transacción"):
            if t and c_new > 0:
                try:
                    existente = df_db[df_db['ticker'] == t] if not df_db.empty else pd.DataFrame()
                    
                    if not existente.empty:
                        fila_v = existente.iloc[0]
                        c_old = float(fila_v['cantidad'])
                        p_old = float(fila_v['precio_promedio_compra'])
                        c_total = c_old + c_new
                        p_final = ((c_old * p_old) + (c_new * p_new)) / c_total
                        
                        conn.table("carteras").update({
                            "cantidad": c_total,
                            "precio_promedio_compra": round(p_final, 3),
                            "tasa": tas,
                            "f_vencimiento": str(f_ven)
                        }).eq("id", fila_v['id']).execute()
                    else:
                        conn.table("carteras").insert({
                            "email": "jpcarbonelli@yahoo.com.ar", "ticker": t,
                            "cantidad": c_new, "tasa": tas, "precio_promedio_compra": p_new,
                            "f_vencimiento": str(f_ven), "meses_cobro": mes
                        }).execute()
                    st.rerun()
                except Exception as e:
                    st.error("Error al guardar. Verifica los permisos de UPDATE en Supabase.")
