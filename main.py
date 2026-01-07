import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="Mi Cartera ONs", layout="wide")
st.title("🚀 Mi Cartera de Inversión")

# --- CONEXIÓN ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    
    conn = st.connection(
        "supabase", 
        type=SupabaseConnection,
        url=s_url,
        key=s_key
    )
    
    # Intentamos leer la tabla 'carteras'
    res = conn.table("carteras").select("*").execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        st.success("✅ Conectado a la tabla 'carteras'")
        st.subheader("Tus Activos")
        st.dataframe(df[["email", "ticker", "cantidad"]], use_container_width=True)
    else:
        st.info("La tabla está vacía. ¡Cargá tu primera ON!")

except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- FORMULARIO DE CARGA (Usando tus columnas reales) ---
st.sidebar.header("Nuevo Registro")
with st.sidebar.form("form_carga"):
    user_email = st.text_input("Email")
    ticker_input = st.selectbox("Ticker", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA"])
    cantidad_input = st.number_input("Cantidad", min_value=1, step=1)
    
    if st.form_submit_button("Guardar"):
        if user_email:
            # INSERTAMOS con los nombres de tus columnas: email, ticker, cantidad
            nueva_fila = {
                "email": user_email, 
                "ticker": ticker_input, 
                "cantidad": cantidad_input
            }
            conn.table("carteras").insert(nueva_fila).execute()
            st.success("¡Guardado correctamente!")
            st.rerun()
        else:
            st.warning("Poné un email para identificar tu cartera.")
