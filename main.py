import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.title("🚀 ON Investor Pro")

# --- CONEXIÓN ---
try:
    # Traemos las credenciales de los secrets
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    
    conn = st.connection(
        "supabase", 
        type=SupabaseConnection,
        url=s_url,
        key=s_key
    )
    
    # Intentamos leer la tabla
    res = conn.table("usuarios_config").select("*").execute()
    
    st.success("✅ ¡CONECTADO TOTALMENTE!")
    
    # Si hay datos, los mostramos
    if res.data:
        st.write("Datos actuales:")
        st.dataframe(pd.DataFrame(res.data))
    else:
        st.info("Conexión exitosa, pero la tabla está vacía. ¡Listo para cargar!")

except Exception as e:
    if "401" in str(e):
        st.error("🔑 Error de Autenticación: La API Key es incorrecta o está incompleta.")
        st.info("Copiá la 'anon public key' desde Supabase usando el botón de 'Copy' y pegala de nuevo en los Secrets.")
    else:
        st.error(f"Error inesperado: {e}")
