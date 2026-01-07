import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Mi Renta Fija Pro", layout="wide", page_icon="📈")

# --- CONEXIÓN A BASE DE DATOS ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection("supabase", type=SupabaseConnection, url=s_url, key=s_key)
    
    # Traemos los datos actualizados
    res = conn.table("carteras").select("*").execute()
    df_db = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_db = pd.DataFrame()

# --- TÍTULO ---
st.title("💰 Panel de Renta Fija & Flujo de Caja")
st.markdown("---")

# --- LÓGICA DE FLUJO MENSUAL ---
if not df_db.empty:
    cronograma = []
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    for _, fila in df_db.iterrows():
        try:
            # Cálculo financiero: Cantidad * (Tasa/100) / 2 (pago semestral)
            cantidad = float(fila['cantidad'])
            tasa = float(fila.get('tasa', 0)) / 100
            pago_semestral = (cantidad * tasa) / 2
            
            # Procesamos los meses (ej: "1, 7" -> [1, 7])
            meses_str = str(fila.get('meses_cobro', '1, 7'))
            meses = [int(m.strip()) for m in meses_str.split(",")]
            
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
        
        # --- SECCIÓN 1: GRÁFICO Y MÉTRICAS ---
        col_met1, col_met2 = st.columns([3, 1])
        
        with col_met1:
            st.subheader("🗓️ Proyección de Cobros Mensuales")
            fig = px.bar(
                df_flujo, 
                x="Mes", 
                y="USD", 
                color="Ticker", 
                text_auto='.2f',
                labels={"USD": "Dólares a cobrar"},
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_met2:
            total_anual = df_flujo["USD"].sum()
            st.metric("Total Intereses Anuales", f"US$ {total_anual:,.2f}")
            st.metric("Promedio Mensual", f"US$ {total_anual/12:,.2f}")

        st.markdown("---")

        # --- SECCIÓN 2: GESTIÓN DE ACTIVOS (BORRADO) ---
        st.subheader("📋 Gestión de Cartera")
        
        # Encabezados de tabla
        h1, h2, h3, h4, h5 = st.columns([2, 2, 1, 2, 1])
        h1.write("**Ticker**")
        h2.write("**Cantidad**")
        h3.write("**Tasa**")
        h4.write("**Meses Pago**")
        h5.write("**Borrar**")

        for _, fila in df_db.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 1])
            c1.write(fila['ticker'])
            c2.write(f"{fila['cantidad']:,}")
            c3.write(f"{fila['tasa']}%")
            c4.write(fila['meses_cobro'])
            
            # AQUÍ ESTABA EL ERROR: Ahora el paréntesis está bien cerrado
            if c5.button("🗑️", key=f"del_{fila['id']}"):
                conn.table("carteras").delete().eq("id", fila['id']).execute()
                st.rerun()
else:
    st.info("Aún no hay datos. Utilizá el panel lateral para cargar tus activos.")

# --- SECCIÓN 3: PANEL LATERAL DE CARGA ---
with st.sidebar:
    st.header("📥 Cargar Nuevo Activo")
    with st.form("nuevo_activo", clear_on_submit=True):
        nuevo_ticker = st.text_input("Ticker (ej: MGCOD)").upper()
        nueva_cantidad = st.number_input("Cantidad Nominal", min_value=0, step=500)
        nueva_tasa = st.number_input("Tasa Anual (%)", min_value=0.0, format="%.2f")
        nuevos_meses = st.text_input("Meses de cobro (ej: 3, 9)", value="1, 7")
        
        if st.form_submit_button("Guardar en Nube"):
            if nuevo_ticker and nueva_cantidad > 0:
                conn.table("carteras").insert({
                    "email": "jpcarbonelli@yahoo.com.ar",
                    "ticker": nuevo_ticker,
                    "cantidad": nueva_cantidad,
                    "tasa": nueva_tasa,
                    "meses_cobro": nuevos_meses
                }).execute()
                st.rerun()
