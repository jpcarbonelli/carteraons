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
    
    # Procesamos cada activo para generar los cobros
    for _, fila in df_db.iterrows():
        try:
            # Cálculo financiero
            cantidad = float(fila['cantidad'])
            tasa = float(fila.get('tasa', 0)) / 100
            pago_anual = cantidad * tasa
            pago_semestral = pago_anual / 2
            
            # Procesamos los meses (convertimos "1, 7" en lista [1, 7])
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
            st.info("Este cálculo asume que todas las ONs pagan cupones semestrales.")

        st.markdown("---")

        # --- SECCIÓN 2: GESTIÓN DE ACTIVOS ---
        st.subheader("📋 Gestión de Cartera")
        st.write("Aquí podés ver tus datos guardados y eliminar registros viejos.")
        
        # Encabezados de tabla manual para incluir el botón de borrar
        h1, h2, h3, h4, h5 = st.columns([2, 2, 1, 2, 1])
        h1.write("**Ticker**")
        h2.write("**Cantidad**")
        h3.write("**Tasa**")
        h4.write("**Meses Pago**")
        h5.write("**Acción**")

        for _, fila in df_db.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 1])
            c1.write(f"**{fila['ticker']}**")
            c2.write(f"{fila['cantidad']:,}")
            c3.write(f"{fila['tasa']}%")
            c4.write(fila['meses_cobro'])
            
            # Botón para borrar usando el ID de la fila
            if c5.button("🗑️", key
