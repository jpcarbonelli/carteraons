import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="ON Investor Pro", layout="wide")
st.title("🚀 ON Investor Pro")

# --- CONEXIÓN ROBUSTA ---
try:
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    
    conn = st.connection(
        "supabase", 
        type=SupabaseConnection,
        url=s_url,
        key=s_key
    )
    
    # Intentamos leer forzando el esquema public
    # Usamos un try interno para que no se rompa la app si la tabla está recién creada
    try:
        res = conn.table("usuarios_config").select("*").execute()
        st.success("✅ ¡Conectado y Tabla encontrada!")
        
        if res.data:
            st.write("Registros actuales:")
            st.dataframe(pd.DataFrame(res.data))
        else:
            st.info("La tabla 'usuarios_config' existe pero no tiene datos aún.")
            
    except Exception as e:
        st.warning("La conexión es buena, pero la tabla 'usuarios_config' no responde.")
        st.write("Si acabas de crear la tabla, esperá 1 minuto o verificá que el nombre sea exacto.")

except Exception as e:
    st.error(f"Error crítico: {e}")

# --- FORMULARIO DE CARGA ---
with st.sidebar.form("form_carga"):
    st.header("Cargar Activo")
    user_email = st.text_input("Tu Email")
    on_ticker = st.selectbox("Ticker", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA"])
    cant = st.number_input("Cantidad", min_value=1)
    
    if st.form_submit_button("Guardar en Nube"):
        if user_email:
            # Intentamos insertar
            conn.table("usuarios_config").insert({
                "email": user_email, 
                "sheet_url": f"{on_ticker}:{cant}"
            }).execute()
            st.success("¡Datos guardados!")
            st.rerun()
        else:
            st.error("Falta el email.")
